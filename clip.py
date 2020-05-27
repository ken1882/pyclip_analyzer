import _G
import numpy as np
import moviepy.editor as mp
import sys
import argv_parse
import os
from threading import Thread

if __name__ == "__main__":
  argv_parse.init()
  _G.init()
  
def load_video(filename):
  return mp.VideoFileClip(filename)

def export_audio(audio, filename):
  audio.write_audiofile(filename)

def generate_audio_clips(audio, out_folder):
  t_clips  = np.arange(0, _G.video_length, _G.TimeWindowSize, dtype=np.int32)
  t_clips  = np.append(t_clips, int(_G.video_length))
  t_len    = len(t_clips)
  subclips = []
  dec      = 2 if int(audio.duration) % _G.TimeWindowSize == 0 else 1
  print(dec)
  for i in range(t_len - dec):
    subclips.append(audio.subclip(t_clips[i], t_clips[i+1]))

  for i, clip in enumerate(subclips):
    filename = f"{out_folder}/{_G.audio_filename(i)}"
    print(f"Exporting {filename}")
    export_audio(clip, filename)
  _G.wait(0.5)
  for clip in subclips:
    clip.close()
  audio.close()

def extandclip_video(vfilename, out_folder=None):
  if not out_folder:
    if _G.FLAG_SAMPLE_PROC:
      out_folder = _G.PositiveSamplePath
    else:
      out_folder = _G.StreamAudioPath
  _G.VideoFilename = vfilename
  _G.ensure_dir_exist(f"{out_folder}/_.mp3")
  video = load_video(vfilename)
  _G.video_length = vlen = video.duration
  generate_audio_clips(video.audio, out_folder)
  video.close()

def spawn_extracting_proc(idx, slug, hostname, sample_proc):
  cmd = f"py clip.py -i {idx} -c {slug} --host-name {hostname}"
  if sample_proc:
    cmd += " -s"
  _th = Thread(target=_G.system_command, args=(cmd,))
  _th.start()
  _th.join()

if __name__ == "__main__":
  filename = _G.VideoFilename
  if _G.FLAG_SAMPLE_PROC:
    filename = f"{_G.PositiveSamplePath}/{_G.ClipName}.{_G.VideoFormat}"
  print(f"Extract and lipping file {filename}")
  extandclip_video(filename)