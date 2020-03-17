from matplotlib import get_backend
import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display as rdis
import librosa.feature as rft
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
  plt.savefig(filename, dpi=_G.DPI)

def plot_waveplot(y, smp_rate, raw=3, col=1, idx=1, **kwargs):
  plt.subplot(raw, col, idx)
  rdis.waveplot(y, sr=smp_rate)
  plt.title('Waveplot')

def plot_rolloff(y, smp_rate, row=3, col=1, idx=3, **kwargs):
  rf = rft.spectral_rolloff(y, smp_rate, n_fft=_G.N_FFT, roll_percent=0.95)
  plt.subplot(row, col, idx)
  plt.semilogy(rf.T, label='Roll-off freq.')
  plt.ylabel('Hz')
  plt.xticks([])
  plt.xlim([0, rf.shape[-1]])
  plt.legend()
  plt.title('Specreal Roll-off')

def plot_melspec(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  spec = rft.melspectrogram(y, sr=smp_rate)
  plt.subplot(row, col, idx)
  plt.semilogy(abs(spec))
  sdb = librosa.power_to_db(spec)
  rdis.specshow(sdb, sr=smp_rate, x_axis='time', y_axis='mel')
  plt.colorbar(format='%+2.0f dB')
  plt.title('Mel-Spectrogram')

def plot_transQ(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  fmin = librosa.midi_to_hz(36)
  amp = librosa.cqt(y, sr=smp_rate, fmin=fmin, n_bins=72)
  lgamp = librosa.amplitude_to_db(abs(amp))
  plt.subplot(row, col, idx)
  librosa.display.specshow(lgamp, sr=smp_rate, x_axis='time', y_axis='cqt_note', fmin=fmin, cmap='coolwarm')
  plt.colorbar(format='%+2.0f dB')
  plt.title('Const.Q Transform')

def plot_zcr(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  zcrs = rft.zero_crossing_rate(y + _G.ZCR_Offset)
  plt.subplot(row, col, idx)
  plt.plot(zcrs[0])
  plt.xticks([])
  plt.title('Zero-crossing Rate')

def plot_mfcc(y, smp_rate, row=3, col=1, idx=2, **kwargs):
  mfccs = rft.mfcc(y, sr=smp_rate)
  plt.subplot(row, col, idx)
  rdis.specshow(mfccs, x_axis='time')
  plt.colorbar()
  plt.title("MFCC")

def plot_all(y, smp_rate):
  cnt_col = 1
  plot_func = [plot_waveplot, plot_melspec, plot_rolloff, plot_zcr, plot_mfcc]
  cnt_row = len(plot_func)
  plt.figure(figsize=_G.get_figsize(cnt_row, cnt_col))
  for i, func in enumerate(plot_func):
    func(y, smp_rate, cnt_row, cnt_col, i+1)

def analyze_audio(filename, out_filename):
  y, smp_rate = librosa.load(filename)
  print("Audio loaded")
  plot_all(y, smp_rate)
  save_plot(out_filename)
  plt.close()

# FileCnt  = 10
# for i in range(FileCnt):
#   Filename = "sample/livestream_tmp{0:03}.mp3".format(i)
#   y, smp_rate = librosa.load(Filename)
#   print("Audio loaded")
#   plot_all(y, smp_rate)
#   save_plot("plot/plot{0:03}.jpg".format(i))
#   plt.close()
Index = 0
Filename = "audio/5fw_skyfactory_clp{0:03}.mp3".format(Index)
save_plot("plot/plot{0:03}.jpg".format(Index))
analyze_audio(Filename)