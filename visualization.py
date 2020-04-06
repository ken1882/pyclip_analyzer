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
plot_len  = len(plot_data)
cur_plot  = None # Current plot image cache
cur_dx    = None # Current plot delta-x per frame
cur_ox    = None # Current plot offset-x of the timestamp indicator
cur_derr  = None # Delta error x of current frame
cur_err   = None # Error x of int'ed x position
last_plot = None # Last plot image cache index

cur_plot = cv2.imread(_G.plot_filename(0))

def draw_timstamp_indicator(frame, x):
  ret = copy.copy(frame)
  ret[:,x] = _G.IndicatorColor
  return ret

def calc_next_plot_pos():
  global cur_dx, cur_ox, cur_err, cur_derr 
  cur_err += cur_derr
  cur_ox  += cur_dx
  if cur_err >= 0.5:
    cur_err -= 1
    cur_ox  += 1

def calc_plot_pos(frame_n):
  global plot_data, plot_len, cur_plot, last_plot
  global cur_dx, cur_ox, cur_err, cur_derr
  timestamp = int(frame_n / _G.FPS)
  plot_n = timestamp // _G.TimeWindowSize
  if plot_n >= plot_len:
    return
  if plot_n != last_plot:
    cur_err   = 0
    cur_plot  = cv2.imread(_G.plot_filename(plot_n))
    last_plot = plot_n
    cur_dx    = (plot_data[plot_n].ex - plot_data[plot_n].sx) / _G.FPS / _G.TimeWindowSize
    cur_derr  = cur_dx - int(cur_dx)
    cur_ox    = plot_data[plot_n].sx
    cur_dx    = int(cur_dx)
    offset    = int(frame_n % (_G.FPS * _G.TimeWindowSize))
    while offset > 1:
      offset -= 1
      calc_next_plot_pos()
  calc_next_plot_pos()

def make_plot_frame(_, frame_n):
  global cur_plot, cur_ox
  calc_plot_pos(frame_n)
  return draw_timstamp_indicator(cur_plot, cur_ox)

player  = VideoPlayer(video, _G.TrackbarName, _G.VideoFilename)
tracker = VideoPlayer(None, f"plt_{_G.TrackbarName}", f"plt_{_G.VideoFilename}", make_frame=make_plot_frame, fmax=player.frame_max)
player.start()
tracker.start()


def main_loop():
  global last_plot
  print("main loop start")
  while not _G.FLAG_STOP and not player.is_ended():
    if abs(tracker.cur_frame - player.cur_frame) >= _G.AutoSyncThreshold:
      tracker.jump_to_frame(player.cur_frame)
      last_plot = -1

    ok = player.update()
    if ok:
      tracker.update_frame()

# Pre-cache video frames
time.sleep(_G.PreCacheTime)
_G.FLAG_PAUSE = True
main_loop()