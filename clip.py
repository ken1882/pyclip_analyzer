import _G
import numpy as np
import moviepy.editor as mp
import sys
import argv_parse

def load_video(filename):
  return mp.VideoFileClip(filename)

def export_audio(audio, filename):
  audio.write_audiofile(filename)

def generate_audio_clips(audio):
  t_clips  = np.arange(0, _G.video_length, _G.TimeWindowSize, dtype=np.int32)
  t_clips  = np.append(t_clips, int(_G.video_length))
  t_len    = len(t_clips)
  subclips = []
  dec      = 2 if int(audio.duration) % _G.TimeWindowSize == 0 else 1
  print(dec)
  for i in range(t_len - dec):
    subclips.append(audio.subclip(t_clips[i], t_clips[i+1]))

  for i, clip in enumerate(subclips):
    filename = _G.audio_filename(i)
    print(f"Exporting {filename}")
    export_audio(clip, filename)

argv_parse.init()
_G.init()
print(f"Clipping stream file index of {_G.StreamFileIndex}")

_G.ensure_dir_exist(_G.audio_filename(0))
video = load_video(_G.VideoFilename)
_G.video_length = vlen = video.duration
generate_audio_clips(video.audio)