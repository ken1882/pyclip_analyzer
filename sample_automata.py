import requests
import urllib.request
import json
import os
import re
import timeit
from bs4 import BeautifulSoup
from random import randint
from pprint import PrettyPrinter
from threading import Thread
import moviepy.editor as mp
import traceback
import time

import _G
import argv_parse
import clip
import analyzer
import oauth

ERRNO_OK    = 0
ERRNO_EXIST = 1

THRET_VAL   = {}

if __name__ == "__main__":
  argv_parse.init()
  _G.init()

APIHeader = {}

# Load API Header settings
with open("twitch_api.key", 'r') as fp:
  for line in fp:
    if not line.strip():
      continue
    key, val = line.split(":")
    APIHeader[key.strip()] = val.strip()

MediaHeaders = {
  'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko'
}

pp = PrettyPrinter(indent=2)

def hms2sec(text):
  text = re.split(r"(\d+)", text)
  ret  = 0
  mul  = 1
  _len = len(text)
  for i in range(_len-1,-1,-1):
    try:
      n = int(text[i])
      ret += n * mul
      mul *= 60
    except ValueError:
      pass
  return ret

def get_helixclip_info(id):
  url = "https://api.twitch.tv/helix/clips"
  params = {
    'id': id
  }
  return requests.get(url, headers=APIHeader, params=params)

def getkarkan_clip_info(slug):
  url = f"https://api.twitch.tv/kraken/clips/{slug}"
  return requests.get(url, headers=APIHeader)

def get_video_info(id):
  url = "https://api.twitch.tv/helix/videos"
  params = {
    'id': id
  }
  return requests.get(url, headers=APIHeader, params=params)

def get_m3u8_info(id):
  url = f"https://api.twitch.tv/api/vods/{id}/access_token"
  response = requests.get(url, headers=MediaHeaders).json()
  token = response['token']
  sig = response['sig']
  m3u8url = f"https://usher.ttvnw.net/vod/{id}.m3u8?player=twitchweb&nauth={token}&" + \
    f"nauthsig={sig}&$allow_audio_only=true&allow_source=true&type=any&p={randint(1,9999)}"
  data = urllib.request.urlopen(m3u8url).read()
  uris = data.decode('utf-8')
  ret  = []
  for uri in uris.split("\n"):
    if "https:" in uri:
        ret.append(uri.strip())
  print(f"Target URI list: {len(ret)}")
  return ret

def _download_m3u8(id, slug, info, start_t, duration, thread_id):
  global THRET_VAL
  filename = f"{_G.StreamFolder}/{_G.StreamFilePrefix}_vod{id}_{slug}.{_G.VideoFormat}"
  if os.path.exists(filename):
    print(f"[Thread] video {id}, {slug} already exists, skipping")
    THRET_VAL[thread_id] = [ERRNO_EXIST, filename]
    return ERRNO_EXIST
  else:
    cmd = _G.FFmpegDownloadCmd.format(start_t, info[2], duration, filename)
    os.system(cmd)
    THRET_VAL[thread_id] = [ERRNO_OK, filename]
    return ERRNO_OK

def download_m3u8(id, slug, start_t, duration, _async=False, thread_id=0):
  _G.ensure_dir_exist(f"{_G.StreamFolder}/")
  info = get_m3u8_info(id)
  print(f"Downloading {id}")
  _th = Thread(target=_download_m3u8, args=(id,slug,info,start_t,duration,thread_id))
  _th.start()
  if not _async:
    _th.join()  

def download_clip(id, slug):
  print("Refreshing Twitch API...")
  access_token = oauth.refresh_token()['access_token']
  APIHeader['Authorization'] = f"Bearer {access_token}"

  print("Waiting Twitch API...")
  data = get_helixclip_info(slug).json()
  data = data['data'][0]
  print(f"Retrived data: {data}")
  
  video_uri = f"{data['thumbnail_url'].split('-preview')[0]}.{_G.VideoFormat}"
  
  filename = f"{_G.PositiveSamplePath}/{slug}.{_G.VideoFormat}"
  _G.ensure_dir_exist(filename)
  
  if os.path.exists(filename):
    return ERRNO_EXIST,filename

  with open(filename, 'wb') as file:
    print(f"Downloading {video_uri} to {filename}...")
    file.write(requests.get(video_uri).content)
  return ERRNO_OK,filename

# data: Karken clip data
def get_ori_timestamp(data):
  return hms2sec(data['vod']['url'].split('t=')[1])

def get_id_from_data(data):
  return data['vod']['id']

def get_id_from_slug(slug):
  data = getkarkan_clip_info(slug).json()
  return data['vod']['id']

def generate_label(clip_fname, slug, start_t):
  label_filename = f"{_G.PositiveSamplePath}/{_G.PostiveLabelFilename}"
  duration = int(clip.load_video(clip_fname).duration + 0.5)
  start_t  = start_t - _G.get_download_timeinfo(start_t)[0]
  f_mode = 'a'
  dat = {'slug': slug, 'start_t': start_t, 'duration': duration}
  if not os.path.exists(label_filename):
    with open(label_filename, 'w') as fp:
      json.dump([dat], fp)
  else:
    all_data = []
    with open(label_filename, 'r') as fp:
      all_data = json.load(fp)
    
    # overwrite exist item
    for idx, item in enumerate(all_data):
      if item['slug'] == slug:
        all_data[idx]['start_t'] = start_t
        all_data[idx]['duration'] = duration
        return
    
    # append new item
    all_data.append(dat)
    with open(label_filename, 'w') as fp:
      json.dump(all_data, fp)    

def start_sample_process():
  global THRET_VAL

  st_time = timeit.default_timer()

  slug = _G.ClipName
  data = None
  _cnt = 0
  
  while not data and _cnt < 3:
    _cnt += 1
    data  = getkarkan_clip_info(slug).json()
    if not data:
      print(f"Failed to get clip data ({data})...retry({_cnt})")
      time.sleep(1)
  if not data['vod']:
    print("Source unavailable, throwing")
    raise RuntimeError("Source VOD unavailable")

  id = get_id_from_data(data)
  start_t = get_ori_timestamp(data)
  
  _G.StreamFileIndex  = int(id)
  _G.StreamFilePrefix = data['broadcaster']['name'].upper()
  _G.FLAG_SAMPLE_PROC = True
  _G.init()
  
  errno,clip_fname = download_clip(id, slug)
  
  inp = ''
  if _G.FLAG_ALWAYS_YES:
    inp = 'Y'
  elif _G.FLAG_ALWAYS_NO:
    inp = 'N'
  
  if errno == ERRNO_EXIST:
    print(f"{clip_fname} already downloaded, skip")
    while inp != 'Y' and inp != 'N':
      inp = input("Process clip anyway? (Y/N): ").upper()
  
  if errno == ERRNO_OK or inp == 'Y':
    print("Generating labels...")
    generate_label(clip_fname, slug, start_t)
  
    print("Extracting clips audio")
    _G.wait(1)
    clip.spawn_extracting_proc(_G.StreamFileIndex, slug, _G.StreamFilePrefix, _G.PROC_SAMPLE)
    
    print("Analyzing clip...")
    _G.wait(1)
    analyzer.spawn_analyze_proc(_G.StreamFileIndex, slug, _G.StreamFilePrefix, _G.PROC_SAMPLE)

  ori_st, duration = _G.get_download_timeinfo(start_t)
  print(f"Ori. start time/duraiton: ", ori_st, duration)
  THRET_VAL = {}
  download_m3u8(id, slug, ori_st, duration)
  
  errno, stream_filename = None, ''
  while True:
    try:
      errno, stream_filename = THRET_VAL[0]
      break
    except Exception:
      _G.wait(0.3)
  
  inp = ''
  if _G.FLAG_ALWAYS_YES:
    inp = 'Y'
  elif _G.FLAG_ALWAYS_NO:
    inp = 'N'
    
  if errno == ERRNO_EXIST:
    while inp != 'Y' and inp != 'N':
      inp = input("Stream video already exists, process anyway? (Y/N): ").upper()
  
  if errno == ERRNO_OK or inp == 'Y':
    _G.wait(1)
    clip.spawn_extracting_proc(_G.StreamFileIndex, slug, _G.StreamFilePrefix, False)
    _G.wait(1)
    analyzer.spawn_analyze_proc(_G.StreamFileIndex, slug, _G.StreamFilePrefix, False)
  
  print("Complete, time taken: ", timeit.default_timer() - st_time)


# py sample_automata.py -c SecretiveLazyVelociraptorBCWarrior
if __name__ == "__main__":
  try:
    start_sample_process()
  except Exception as err:
    print("An error occurred while downloading!")
    print(err, traceback.format_exc())
    with open("error_download.txt", 'a') as fp:
      fp.write(f"{_G.ClipName} {err}\n")
