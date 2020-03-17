import _G
import numpy as np
import moviepy.editor as mp

def load_video(filename):
  return mp.VideoFileClip(filename)

def export_audio(audio, filename):
  audio.write_audiofile(filename)

def generate_audio_clips(audio):
  t_clips  = np.arange(0, _G.video_length, _G.TimeWindowSize, dtype= np.int32)
  t_clips  = np.append(t_clips, int(_G.video_length))
  t_len    = len(t_clips)
  subclips = []
  for i in range(t_len - 1):
    subclips.append(audio.subclip(t_clips[i], t_clips[i+1]))

  for i, clip in enumerate(subclips):
    filename = f"{_G.AudioFolder}/{_G.StreamFilePrefix}"
    filename += f"{_G.AudioClipSuffix.format(i)}.{_G.AudioFormat}"
    print(f"Exporting {filename}")
    export_audio(clip, filename)
  

video = load_video(_G.VideoFilename)
_G.video_length = vlen = video.duration
generate_audio_clips(video.audio)
# export_vaudio(video, f"{_G.AudioFolder}/{_G.VideoFileStem}.{_G.AudioFormat}")