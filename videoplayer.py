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

class VideoPlayer:
  
  def __init__(self, video, trackbar_name, window_name, **kwargs):
    self.cur_frame = 0
    self.video     = video
    if video:
      self.src       = video.src
      self.audio     = MediaPlayer(video.src)
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
    self.audio.seek(t, False)

  def start(self):
    dth = Thread(target=self.update_decode, daemon=True)
    dth.start()
    if self.video:
      ath = Thread(target=self.extract_audio)
      ath.start()
    if not self.FLAG_ENCODE_STOP:
      eth = Thread(target=self.update_encode, daemon=True)
      eth.start()
    return self

  def extract_audio(self):
    fname = audio_filename(_G.StreamFileIndex)
    if not os.path.exists(fname):
      v = mp.VideoFileClip(self.src)
      v.audio.write_audiofile(fname)

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

  def frame_available(self):
    return self.dqueue.qsize() > 0

  def get_frame(self):
    if self.dqueue.empty():
      return None
    return self.dqueue.get()

  def write_async_ostream(self, frame):
    if not self.FLAG_ENCODE_STOP:
      self.equeue.put(frame)

  def update(self):
    self.update_frame()
    self.update_input()
    self.update_flags()
  
  def update_frame(self):
    if self.is_ended() or _G.FLAG_PAUSE:
      return
    
    cv2.setTrackbarPos(self.trackbar, self.window, self.cur_frame)
    
    frame = self.get_frame()
      
    if frame is None:
      return
      
    cv2.imshow(self.window, frame)
    # print(f"qsize={self.dqueue.qsize()}")
    self.write_async_ostream(frame)
    
    if not _G.FLAG_PAUSE:
      self.cur_frame += 1

  def update_flags(self):
    if self.is_ended() and not self.equeue.empty():
      self.FLAG_ENCODE_STOP = True

  def update_input(self):
    key = cv2.waitKey(_G.UPS)
    if key == _G.VK_ESC:
      _G.FLAG_STOP = True
    elif key == _G.VK_SPACE:
      _G.FLAG_PAUSE ^= True
      self.audio.toggle_pause()

  def is_ended(self):
    return self.cur_frame >= self.frame_max
  
  def make_audio_window(self):
    window, val = self.audio.get_frame()
    if window is None or val == 'eof':
      return (None,None)
    return window