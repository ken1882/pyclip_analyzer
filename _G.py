import os

PixPerInch = 96
DPI = 600
PixelPerCol = 1024
PixelPerRow = 512

def inch2pixel(inch):
  return inch * PixPerInch

def pixel2inch(pix):
  return pix / PixPerInch

def get_figsize(row, col):
  return (int(pixel2inch(col * PixelPerCol)), int(pixel2inch(row * PixelPerRow)))

StreamFolder  = "stream"
AudioFolder   = "audio"
PlotFolder    = "plot"

VideoFormat   = "mp4"
AudioFormat   = "mp3"
PlotFormat    = "jpg"

StreamFileIndex  = 1
StreamFilePrefix = "5fw_skyfactory"
StreamFileSuffix = "_ep{0:03}".format(StreamFileIndex)
PlotFileSuffix   = "_plt{0:03}"

VideoFileStem    = f"{StreamFilePrefix}{StreamFileSuffix}"
VideoFilename    = f"{StreamFolder}/{VideoFileStem}.{VideoFormat}"
AudioClipSuffix  = "_clp{0:03}"

N_FFT          = 1024
N_MELS         = 128
N_MFCC         = 40
HopLen         = 512
RollPercent    = 0.95
ZCR_Offset     = 0.0001
ZCR_FrameLen   = 2048
TimeWindowSize = 30

def ensure_dir_exist(path):
  path = path.split('/')
  path.pop()
  if len(path) == 0:
    return
  pwd = ""
  for i, dir in enumerate(path):
    pwd += f"{dir}/"
    if not os.path.exists(pwd):
      os.mkdir(pwd)

def plot_filename(idx):
  return f"{PlotFolder}/{StreamFilePrefix}/{StreamFileSuffix}/{PlotFileSuffix.format(idx)}.{PlotFormat}"

def audio_filename(idx):
  return f"{AudioFolder}/{StreamFilePrefix}/{StreamFileSuffix}/{AudioClipSuffix.format(idx)}.{AudioFormat}"

video_length    = 0

