import os.path
from queue import Queue
from threading import Thread
import cv2
import time
import moviepy.editor as mp
import numpy as np
from ffpyplayer.player import MediaPlayer
import _G
from _G import audio_filename, out_filename

TrackBarName   = 'frame no.'
WindowName     = "test"

def test_callback(*args):
  print(args)

class VideoPlayer:
  
  AudioSyncInterval = 60

  def __init__(self, video, trackbar_name, window_name, **kwargs):
    self.cur_frame   = 0
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
    print(not kwargs.get('output'))
    self.FLAG_ENCODE_STOP = not kwargs.get('output')
    self.FLAG_DECODE_STOP = False
    
    mkframe = kwargs.get('make_frame')
    if not mkframe:
      mkframe = lambda f,t: f
    self.make_frame = mkframe
    cv2.namedWindow(self.window)
    cv2.createTrackbar(self.trackbar, self.window, 0, self.frame_max, self.set_current_frame)
  
  def init_ostream(self):
    if not self.video:
      print("No video loaded for {self}")
      return
    fname  = out_filename(_G.StreamFileIndex)
    fourcc = cv2.VideoWriter_fourcc(*_G.VideoCodec)
    _fps   = self.video.fps
    _res   = (_G.CanvasWidth, _G.CanvasHeight)
    return cv2.VideoWriter(fname, fourcc, _fps, _res)

  def set_current_frame(self, n):
    # self.cur_frame = n
    pass

  def set_audio_frame(self, n):
    t = self.video.frame2timestamp(n)
    print(f"Sync f={n}, t={t}")
    self.audio.seek(t, False, accurate=True)

  def sync_audio_channel(self):
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
        time.sleep(_G.UPMS)
      sth = Thread(target=self.update_synchronzation, daemon=True)
      sth.start()
    return self

  def extract_audio(self):
    fname = _G.FullAudioFilename
    if not os.path.exists(fname):
      v = mp.VideoFileClip(self.src)
      v.audio.write_audiofile(fname)
    self.audio = MediaPlayer(_G.FullAudioFilename, callback=test_callback)
    self.audio.toggle_pause()
    print("Audio loaded")

  def update_decode(self):
    # current framt count in decoding
    deframe_cnt = 0
    while not self.FLAG_DECODE_STOP:
      if not self.dqueue.full():
        frame = None
        if self.video:
          ret, frame = self.video.read()
          if not ret:
            self.FLAG_DECODE_STOP = True
            return
        frame = self.make_frame(frame, deframe_cnt)
        self.dqueue.put(frame)
        deframe_cnt += 1
      time.sleep(_G.UPMS)
    print("Decode Ended")

  def update_encode(self):
    ostream = self.init_ostream()
    while not self.FLAG_ENCODE_STOP:
      if not self.equeue.empty():
        ostream.write(self.equeue.get())

  def update_synchronzation(self):
    while not _G.FLAG_STOP:
      time.sleep(_G.UPMS)
      aframe = self.audio.get_pts() * self.video.fps
      if abs(aframe - self.cur_frame) > 12:
        self.pause(True)
        print("Auto Paused")

  def frame_available(self):
    return self.dqueue.qsize() > 0

  def get_frame(self):
    if self.dqueue.empty():
      return None
    return self.dqueue.get()

  def get_audio_frame(self):
    return int(self.audio.get_pts() * self.video.fps)

  def write_async_ostream(self, frame):
    if not self.FLAG_ENCODE_STOP:
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
    # print(f"qsize={self.dqueue.qsize()}")
    self.write_async_ostream(frame)
    
    if not _G.FLAG_PAUSE:
      self.last_vframe  = self.cur_frame
      self.cur_frame   += 1
    return True

  def update_flags(self):
    if self.is_ended() and not self.equeue.empty():
      self.FLAG_ENCODE_STOP = True

  def update_input(self):
    key = cv2.waitKey(_G.UPS)
    if key == _G.VK_ESC:
      self.stop()
    elif key == _G.VK_SPACE:
      self.pause(_G.FLAG_PAUSE ^ True)

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