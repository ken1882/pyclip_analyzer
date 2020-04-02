import os.path
import pickle as pk
import numpy as np
from glob import glob
import cv2
import _G

class PlotPlaybackRecord:

  def __init__(self, st):
    self.timestamp = st
    self.sx = 0
    self.ex = 0

def build_playback_archive():
  filename = _G.PlotPlaybackFilename
  if os.path.exists(filename):
    print(f"Archive {filename} already exists")
    return _G.load_data(filename)
  print(f"Building archive playback for '{filename}'")
  files  = glob_plots(filename)
  cur_timestamp = 0
  data   = []
  _len   = len(files)
  for i, file in enumerate(files):
    print(f"Processing {i}/{_len}")
    dat = PlotPlaybackRecord(cur_timestamp)
    dat.sx, dat.ex = find_plot_window_length(file)
    data.append(dat)
    cur_timestamp += _G.TimeWindowSize
  _G.dump_data(data, filename)
  print("Archived dumped")
  return data

def glob_plots(filename):
  path = "/".join(filename.split('/')[:-1])
  return glob(f"{path}/*.{_G.PlotFormat}")
  
RGB2GS_MAT = np.array([0.3,0.4,0.3]).T
def transform_rgb2gs(img):
  return np.dot(img[...,:3],RGB2GS_MAT)

def find_plot_window_length(file):
  img = cv2.imread(file)
  ar  = transform_rgb2gs(img)[_G.PlotYseekPos, :]
  candidates = []
  for i,v in enumerate(ar):
    if v <= _G.PlotWindowColorThreshold:
      candidates.append(i)
  return [candidates[0], candidates[-1]]
