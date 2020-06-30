import os
from glob import glob
import pickle as pk
import time

PixPerInch = 96
DPI = 600
PixelPerCol = 1024
PixelPerRow = 346

def inch2pixel(inch):
  return inch * PixPerInch

def pixel2inch(pix):
  return pix / PixPerInch

def get_figsize(row, col):
  return (int(pixel2inch(col * PixelPerCol)), int(pixel2inch(row * PixelPerRow)))

StreamFolder  = "stream"
AudioFolder   = "audio"
PlotFolder    = "plot"
PositiveSampleFolder = "positive_samples"

VideoFormat   = "mp4"
AudioFormat   = "mp3"
PlotFormat    = "png"
OutFormat     = "mkv"
DataFormat    = "dat"

StreamFileIndex  = 580483021
StreamFilePrefix = "ESL_DOTA2"
PlotFileSuffix   = "_plt{0:04}"
AudioClipSuffix  = "_clp{0:03}"

StreamFileSuffix = ''
VideoFileStem    = ''
VideoFilename    = ''
FullAudioFilename  = ''
PositiveSamplePath = ''
PositiveLabelString = ""
ClipName = ""
StreamAudioPath = ''

def init():
  global StreamFileSuffix, VideoFileStem, VideoFilename, FullAudioFilename
  global PositiveSamplePath, ClipName, StreamAudioPath
  StreamFileSuffix = f"_vod{StreamFileIndex}_{ClipName}"
  VideoFileStem    = f"{StreamFilePrefix}{StreamFileSuffix}"
  VideoFilename    = f"{StreamFolder}/{VideoFileStem}.{VideoFormat}"
  StreamAudioPath    = f"{AudioFolder}/{StreamFilePrefix}/{StreamFileSuffix}"
  FullAudioFilename  = f"{StreamAudioPath}/{VideoFileStem}.{AudioFormat}"
  PositiveSamplePath = f"{PositiveSampleFolder}/{StreamFilePrefix}/{StreamFileSuffix}"
  PlotPlaybackFilename = f"{PlotFolder}/{StreamFilePrefix}/{StreamFileSuffix}/playback{StreamFileSuffix}.dat"

DefaultSR      = 22050
N_FFT          = 1024
N_MELS         = 128
N_MFCC         = 40
HopLen         = 512
RollPercent    = 0.95
ZCR_Offset     = 0
ZCR_FrameLen   = 512
ZCR_Center     = True
TimeWindowSize = 30

PLT_XLIM = int(DefaultSR * TimeWindowSize / HopLen + 0.5)

PlotXTimeStartPos = 179
PlotXTimeEndPos   = 1874

FPS = 30
ContextSwitchOffset = 5
AbsUPS = 1 / FPS
UPMS   = int(1000 / (FPS + ContextSwitchOffset))
UPS    = UPMS / 1000
SubThreadUPS = 0.1

SyncAutoPauseThreshold = 12
AutoSyncThreshold = 4

def set_fps(n):
  global FPS, UPS, UPMS, AbsUPS
  FPS    = n
  AbsUPS = 1 / FPS
  UPMS   = int(1000 / (FPS + ContextSwitchOffset))
  UPS    = UPMS / 1000

VK_ESC   = 27
VK_SPACE = 32

VK_S = 83
VK_s = 115
VideoBufferSize = 2

VideoCodec = 'h264'
MaxQueueSize = 128

TrackbarName   = "frame no."

FLAG_STOP  = False
FLAG_PAUSE = False

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
  return f"{AudioClipSuffix.format(idx)}.{AudioFormat}"

def out_filename(idx):
  return f"{StreamFolder}/{VideoFileStem}_out.{OutFormat}"

def positive_videos():
  pattern = f"{PositiveSamplePath}/*.{VideoFormat}"
  files = glob(pattern)
  return [file.replace("\\", "/") for file in files]

def positive_audios():
  pattern = f"{PositiveSamplePath}/*.{AudioFormat}"
  files = glob(pattern)
  return [file.replace("\\", "/") for file in files]

def positive_data():
  pattern = f"{PositiveSamplePath}/*.{DataFormat}"
  files = glob(pattern)
  return [file.replace("\\", "/") for file in files]

def make_positive_afilename(idx):
  return f"{PositiveSamplePath}/{idx}.{AudioFormat}"

def make_positive_dataname(idx):
  return f"{PositiveSamplePath}/positive_audio_{idx}.{DataFormat}"

def positive_plot_filename(idx):
  return f"{PositiveSamplePath}/plt_{idx}.{PlotFormat}"

def dump_data(data, fname):
  with open(fname, 'wb') as fp:
    pk.dump(data, fp)

def load_data(fname):
  with open(fname, 'rb') as fp:
    return pk.load(fp)

def all_positive_files():
  pattern = f"{PositiveSampleFolder}/**/*.dat"
  return glob(pattern, recursive=True)

def all_data_files():
  pattern = f"{PlotFolder}/**/*data.dat"
  return glob(pattern, recursive=True)

def get_stream_adump_filename():
  return f"{PlotFolder}/{StreamFilePrefix}/{StreamFileSuffix}/audio_data.{DataFormat}"

def resume(fiber):
  try:
    ret = next(fiber)
    return fiber, ret
  except StopIteration:
    return None, None

PlotXseekPos = [175, 1850]
PlotYseekPos = 20
PlotWindowColorThreshold = 0xFF - 0xE0
IndicatorColor = (0,0,0)

PreCacheTime = 3 # sec

FLAG_SAMPLE_PROC = False
FLAG_RETRAIN = False
FLAG_ALWAYS_YES = False
FLAG_ALWAYS_NO = False

Categories = ['melspec', 'rolloff', 'zcr', 'mfcc']
IgnoredCategories = ['waveplot', 'melspec']
PostiveLabelFilename = "labels.dat"

FFmpegDownloadCmd = 'ffmpeg -protocol_whitelist "file,http,https,tcp,tls" -y -ss ' + \
  '{:d} -i {:s} -c copy -t {:d} {:s}'

StartDownloadTimestamp = 0
DownloadTimeOffset = [15 * 60, 15 * 60]

def get_download_timeinfo(t):
  return [max(0, t-DownloadTimeOffset[0]), DownloadTimeOffset[0]+DownloadTimeOffset[1]]

def wait(t):
  time.sleep(t)

def system_command(cmd):
  os.system(cmd)