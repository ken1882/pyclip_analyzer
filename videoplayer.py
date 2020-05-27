import os.path
from queue import Queue
from threading import Thread
import cv2
import time
import moviepy.editor as mp
import numpy as np
from ffpyplayer.player import MediaPlayer
import _G
from _G import out_filename

TrackBarName   = 'frame no.'
WindowName     = "test"

class VideoPlayer:
  
  AudioSyncInterval = 60
  THREAD_MSG_CLEAR  = "_th_clr_"
  THREAD_MSG_VSEEK  = "_th_vseek_"

  def __init__(self, video, trackbar_name, window_name, **kwargs):
    self.cur_frame   = 0
    self.dframe_cnt  = 0 
    self.audio_frame = 0
    self.last_vframe = -1 # last video frame
    self.last_aframe = -1 # last audio frame
    self.video       = video
    self.audio       = None
    self.audio_sync_interval = VideoPlayer.AudioSyncInterval
    if video:
      self.src       = video.src
      self.frame_max = video.frame_max
    else:
      self.frame_max = kwargs.get('fmax')
    self.trackbar  = trackbar_name
    self.window    = window_name
    self.dqueue    = Queue(maxsize=_G.MaxQueueSize)
    self.equeue    = Queue()
    self.FLAG_ENCODE_STOP = not kwargs.get('output')
    self.FLAG_DECODE_STOP = False
    self.FLAG_LOCK = False
    self.thread_msg = None

    if self.FLAG_ENCODE_STOP:
      print(f"Ostream closed for {window_name}")
    
    mkframe = kwargs.get('make_frame')
    if not mkframe:
      mkframe = lambda f,t: f
    self.make_frame = mkframe
    cv2.namedWindow(self.window)
    cv2.createTrackbar(self.trackbar, self.window, 0, self.frame_max, self.set_next_frame)
  
  def init_ostream(self):
    if not self.video:
      print("No video loaded for {self}")
      return
    fname  = out_filename(_G.StreamFileIndex)
    fourcc = cv2.VideoWriter_fourcc(*_G.VideoCodec)
    _fps   = self.video.fps
    _res   = (_G.CanvasWidth, _G.CanvasHeight)
    return cv2.VideoWriter(fname, fourcc, _fps, _res)

  def set_next_frame(self, n):
    if not self.video:
      return
    if not self.FLAG_ENCODE_STOP:
      print("Cannot jump a encoding video")
      return
    if abs(n - self.cur_frame) >= _G.AutoSyncThreshold:
      self.jump_to_frame(n)

  def set_audio_frame(self, n):
    t = self.video.frame2timestamp(n)
    print(f"Sync f={n}, t={t}")
    self.audio.seek(t, False, accurate=True)

  def jump_to_frame(self, n):
    print(f"Jumping to frame {n}")
    self.lock_threads()
    self.cur_frame  = n
    self.dframe_cnt = n
    self.clear_queue()
    self.seek_video(n)
    self.sync_audio_channel()
    self.unlock_threads()
    ori_pause_stat = _G.FLAG_PAUSE
    # fiber = self.wait_until_safe2play()
    # while fiber:
    #   fiber, _ = _G.resume(fiber)
    #   time.sleep(_G.UPS)
    self.pause(ori_pause_stat)

  def sync_audio_channel(self):
    if self.audio:
      self.set_audio_frame(self.cur_frame)

  def start(self):
    dth = Thread(target=self.update_decode, daemon=True)
    dth.start()
    if not self.FLAG_ENCODE_STOP:
      eth = Thread(target=self.update_encode, daemon=True)
      eth.start()
    if self.video:
      ath = Thread(target=self.extract_audio, daemon=True)
      ath.start()
      while not self.audio:
        time.sleep(_G.UPS)
      sth = Thread(target=self.update_synchronzation, daemon=True)
      sth.start()
    return self

  def extract_audio(self):
    fname = _G.FullAudioFilename
    if not os.path.exists(fname):
      v = mp.VideoFileClip(self.src)
      v.audio.write_audiofile(fname)
    self.audio = MediaPlayer(_G.FullAudioFilename)
    self.audio.toggle_pause()
    print("Audio loaded")
  
  def process_thread_message(self):
    if self.thread_msg == VideoPlayer.THREAD_MSG_CLEAR:
      print("Clear queue")
      self.dqueue.queue.clear()
    elif self.THREAD_MSG_VSEEK == VideoPlayer.THREAD_MSG_VSEEK:
      print("Seek to", self.thread_args[0])
      if self.video:
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.thread_args[0])
    
  def update_decode(self):
    # current framt count in decoding
    self.dframe_cnt = 0
    while not self.FLAG_DECODE_STOP:
      time.sleep(_G.UPS)
      
      if self.thread_msg:
        self.process_thread_message()
        self.thread_msg  = None
        self.thread_args = None
      
      if self.FLAG_LOCK:
        pass

      if not self.dqueue.full():
        frame = None
        if self.video:
          ret, frame = self.video.read()
          if not ret:
            self.FLAG_DECODE_STOP = True
            return
        frame = self.make_frame(frame, self.dframe_cnt)
        self.dqueue.put(frame)
        self.dframe_cnt += 1
    print("Decode Ended")

  def update_encode(self):
    ostream = self.init_ostream()
    while not self.FLAG_ENCODE_STOP:
      if not self.equeue.empty():
        ostream.write(self.equeue.get())
      time.sleep(_G.SubThreadUPS)

  def update_synchronzation(self):
    while not _G.FLAG_STOP:
      time.sleep(_G.SubThreadUPS)
      if self.FLAG_LOCK:
        pass
      aframe = self.audio.get_pts() * self.video.fps
      if abs(aframe - self.cur_frame) > _G.AutoSyncThreshold:
        self.sync_audio_channel()
        print(f"Auto Synced: {aframe} > {self.cur_frame}")

  def frame_available(self):
    if self.FLAG_LOCK:
      return False
    return self.dqueue.qsize() > 0

  def get_frame(self):
    if self.FLAG_LOCK:
      return None
    if self.dqueue.empty():
      return None
    return self.dqueue.get()

  def get_audio_frame(self):
    return int(self.audio.get_pts() * self.video.fps)

  def write_async_ostream(self, frame):
    self.equeue.put(frame)

  def update(self):
    frame_synced = self.update_frame()
    self.update_input()
    self.update_flags()
    return frame_synced
  
  def update_frame(self):
    if self.audio:
      self.audio_frame = self.get_audio_frame()
      if self.audio_frame == self.last_aframe:
        return False
      self.last_aframe = self.audio_frame
    
    if self.is_ended() or _G.FLAG_PAUSE:
      return False

    cv2.setTrackbarPos(self.trackbar, self.window, self.cur_frame)
    
    frame = self.get_frame()
    if frame is None:
      return False
      
    cv2.imshow(self.window, frame)
    if not self.FLAG_ENCODE_STOP:
      self.write_async_ostream(frame)
    
    if not _G.FLAG_PAUSE:
      self.last_vframe  = self.cur_frame
      self.cur_frame   += 1
    return True

  def update_flags(self):
    if self.is_ended() and not self.equeue.empty():
      self.FLAG_ENCODE_STOP = True

  def update_input(self):
    key = cv2.waitKey(_G.UPMS)
    if key == _G.VK_ESC:
      self.stop()
    elif key == _G.VK_SPACE:
      self.pause(_G.FLAG_PAUSE ^ True)
    elif key == _G.VK_S or key == _G.VK_s:
      print(f"e/d queue size={self.equeue.qsize()}/{self.dqueue.qsize()}")

  def stop(self):
    _G.FLAG_STOP = True

  def pause(self, flg):
    if _G.FLAG_PAUSE != flg:
      self.audio.toggle_pause()
    _G.FLAG_PAUSE = flg
    self.sync_audio_channel()

  def is_ended(self):
    return self.cur_frame >= self.frame_max
  
  def make_audio_window(self):
    window, val = self.audio.get_frame()
    if window is None or val == 'eof':
      return (None,None)
    return window
  
  # Should be called from main thread to wait
  def wait_until_safe2play(self):
    while self.dqueue.qsize() < _G.MaxQueueSize // 2:
      self.pause(True)
      yield

  def clear_queue(self):
    self.send_thread_message(VideoPlayer.THREAD_MSG_CLEAR)
  
  def lock_threads(self):
    self.FLAG_LOCK = True
    time.sleep(_G.UPS*2)
  
  def unlock_threads(self):
    self.FLAG_LOCK = False
    time.sleep(_G.UPS*2)
  
  def seek_video(self, n):
    self.send_thread_message(VideoPlayer.THREAD_MSG_VSEEK, n)
  
  def send_thread_message(self, msg, *args):
    while self.thread_msg:
      time.sleep(_G.UPS)
    self.thread_msg  = msg
    self.thread_args = args