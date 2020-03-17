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

StreamFileIndex  = 1
StreamFilePrefix = "5fw_skyfactory"
StreamFileSuffix = "_ep{0:03}".format(StreamFileIndex)
VideoFileStem    = f"{StreamFilePrefix}{StreamFileSuffix}"
VideoFilename    = f"{StreamFolder}/{VideoFileStem}.{VideoFormat}"
AudioClipSuffix  = "_clp{0:03}"

N_FFT          = 1024
ZCR_Offset     = 0.0001
TimeWindowSize = 30

video_length    = 0

