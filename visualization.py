import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
import moviepy.editor as mp
import copy
from moviepy.video.VideoClip import ImageClip
from videoclip import VideoClip
from videoplayer import VideoPlayer
from plotplayback import PlotPlaybackRecord
from threading import Thread
import plotplayback
import _G

video  = VideoClip(_G.VideoFilename)
image  = mp.ImageClip(_G.plot_filename(0))

plot_data = plotplayback.build_playback_archive()
cur_plot  = None # Current plot image cache
cur_dx    = None # Current plot delta-x per frame
cur_ox    = None # Current plot offset-x of the timestamp indicator
cur_derr  = None # Delta error x of current frame
cur_err   = None # Error x of int'ed x position
last_plot = None # Last plot image cache index

cur_plot = cv2.imread(_G.plot_filename(0))

def make_frame(frame, frame_n):
  return frame

def draw_timstamp_indicator(frame, x):
  ret = copy.copy(frame)
  ret[:,x] = _G.IndicatorColor
  return ret

def make_plot_frame(_, frame_n):
  global plot_data, cur_plot, last_plot, cur_dx, cur_ox, cur_err, cur_derr
  timestamp = int(frame_n / _G.FPS)
  plot_n = timestamp // _G.TimeWindowSize
  if plot_n != last_plot:
    cur_err   = 0
    cur_plot  = cv2.imread(_G.plot_filename(plot_n))
    last_plot = plot_n
    cur_dx    = (plot_data[plot_n].ex - plot_data[plot_n].sx) / _G.FPS / _G.TimeWindowSize
    cur_derr  = cur_dx - int(cur_dx)
    cur_ox    = plot_data[plot_n].sx
    cur_dx    = int(cur_dx)
  cur_err += cur_derr
  cur_ox  += cur_dx
  if cur_err >= 0.5:
    cur_err -= 1
    cur_ox  += 1
  return draw_timstamp_indicator(cur_plot, cur_ox)

player  = VideoPlayer(video, _G.TrackbarName, _G.VideoFilename, make_frame=make_frame)
tracker = VideoPlayer(None, f"plt_{_G.TrackbarName}", f"plt_{_G.VideoFilename}", make_frame=make_plot_frame, fmax=player.frame_max)
player.start()
tracker.start()

def update_tracker_frame():
  while not _G.FLAG_STOP and not tracker.is_ended():
    tracker.update_frame()

def main_loop():
  print("main loop start")
  while not _G.FLAG_STOP and not player.is_ended():
    ok = player.update()
    if ok:
      tracker.update_frame()

# Pre-cache video frames
time.sleep(_G.PreCacheTime)
_G.FLAG_PAUSE = True
main_loop()