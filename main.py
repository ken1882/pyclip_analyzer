from matplotlib import get_backend
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import librosa
import librosa.display as rdis
import librosa.feature as rft
from glob import glob
from os import path
import _G

def show_fullscreen():
  plt.tight_layout()
  mng = plt.get_current_fig_manager()
  mng.full_screen_toggle()
  plt.show()

def save_plot(filename):
  backend = get_backend()
  mng = plt.get_current_fig_manager()
  if backend == 'wxAgg':
    mng.frame.Maximize(True)
  elif backend == 'Qt4Agg' or backend == 'Qt5Agg':
    mng.window.showMaximized()
  elif backend == 'TkAgg':
    mng.window.state('zoomed')
  else:
    print("Unrecognized backend: ",backend)
  plt.tight_layout(True)
  plt.savefig(filename)

def get_colorbar_axis():
  ax = plt.gca()
  divider = make_axes_locatable(ax)
  return divider.append_axes("bottom", size="5%", pad=0.5)

def plot_waveplot(y, smp_rate, raw=3, col=1, idx=1, **kwargs):
  ax = plt.subplot(raw, col, idx)
  print(ax.get_xbound())
  rdis.waveplot(y, sr=smp_rate)
  # plt.title('Waveplot')
  return y

def plot_rolloff(y, smp_rate, row=3, col=1, idx=3, **kwargs):
  rf = rft.spectral_rolloff(y, smp_rate, n_fft=_G.N_FFT, roll_percent=_G.RollPercent, hop_length=_G.HopLen)
  plt.subplot(row, col, idx)
  plt.semilogy(rf.T, label='Roll-off freq.')
  plt.ylabel('Hz')
  plt.xticks([])
  plt.xlim([0, _G.PLT_XLIM])
  plt.legend()
  # plt.title('Specreal Roll-off')
  return np.log10(rf.T)

def plot_melspec(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  spec = rft.melspectrogram(y, sr=smp_rate, n_mels=_G.N_MELS, n_fft=_G.N_FFT, hop_length=_G.HopLen)
  plt.subplot(row, col, idx)
  plt.semilogy(abs(spec))
  sdb = librosa.power_to_db(spec)
  rdis.specshow(sdb, sr=smp_rate, x_axis='time', y_axis='mel')
  cax = get_colorbar_axis()
  plt.colorbar(format='%+2.0f dB', orientation='horizontal', cax=cax)
  # plt.title('Mel-Spectrogram')
  return sdb

def plot_zcr(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  zcrs = rft.zero_crossing_rate(y, hop_length=_G.HopLen, frame_length=_G.ZCR_FrameLen, center=_G.ZCR_Center)
  plt.subplot(row, col, idx)
  plt.plot(zcrs[0])
  plt.xticks([])
  plt.xlim([0, _G.PLT_XLIM])
  # plt.title('Zero-crossing Rate')
  zcs = librosa.zero_crossings(y, pad=False)
  return zcrs

def plot_mfcc(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  mfccs = rft.mfcc(y, sr=smp_rate, n_mfcc=_G.N_MFCC)
  plt.subplot(row, col, idx)
  rdis.specshow(mfccs, x_axis='time')
  cax = get_colorbar_axis()
  plt.colorbar(orientation='horizontal', cax=cax)
  # plt.title("MFCC")
  return mfccs

def plot_all(y, smp_rate):
  cnt_col = 1
  plot_func = [plot_waveplot, plot_melspec, plot_rolloff, plot_zcr, plot_mfcc]
  cnt_row = len(plot_func)
  plt.figure(figsize=_G.get_figsize(cnt_row, cnt_col))
  for i, func in enumerate(plot_func):
    func(y, smp_rate, cnt_row, cnt_col, i+1)

def analyze_and_plot_audio(filename, out_filename, overwrite=False):
  if path.exists(out_filename) and not overwrite:
    print(f"{out_filename} already exists, skipping")
    return
  y, smp_rate = librosa.load(filename)
  print("Audio loaded")
  plot_all(y, smp_rate)
  save_plot(out_filename)
  plt.close()
  # show_fullscreen()

def get_audio_files(prefix, episode):
  return glob(f"{_G.AudioFolder}/{prefix}/{episode}/*.{_G.AudioFormat}")

_G.ensure_dir_exist(_G.plot_filename(0))
files = get_audio_files(_G.StreamFilePrefix, _G.StreamFileSuffix)
flen  = len(files)
for i, file in enumerate(files):
  print(f"Analyzing {i+1}/{flen}")
  analyze_and_plot_audio(file, _G.plot_filename(i), True)
  # if i >= 2:
  #   break