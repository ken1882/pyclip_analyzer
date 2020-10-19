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

# Thread return value
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

def refresh_token():
  print("Refreshing Twitch API...")
  access_token = oauth.refresh_token()['access_token']
  APIHeader['Authorization'] = f"Bearer {access_token}"

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

def make_fullvod_filename(id):
  return f"{_G.TestDataFolder}/{_G.StreamFilePrefix}_vod{id}.{_G.VideoFormat}"

def _download_m3u8_full(id, info, start_t, duration, thread_id):
  global THRET_VAL
  filename = f"{_G.TestDataFolder}/{_G.StreamFilePrefix}_vod{id}.{_G.VideoFormat}"
  if os.path.exists(filename):
    print(f"[Thread] video {id} already exists, skipping")
    THRET_VAL[thread_id] = [ERRNO_EXIST, filename]
    return ERRNO_EXIST
  else:
    cmd = _G.FFmpegDownloadCmd.format(start_t, info[2], duration, filename)
    os.system(cmd)
    THRET_VAL[thread_id] = [ERRNO_OK, filename]
    return ERRNO_OK

def download_full_vod(id, duration, _async=False, thread_id=0):
  _G.ensure_dir_exist(f"{_G.TestDataFolder}/")
  info = get_m3u8_info(id)
  print(f"Downloading {id}")
  _th = Thread(target=_download_m3u8_full, args=(id,info,0,duration,thread_id))
  _th.start()
  if not _async:
    _th.join()  

def get_id_from_data(data):
  return data['vod']['id']

def get_id_from_slug(slug):
  data = getkarkan_clip_info(slug).json()
  return data['vod']['id']

# Full process contain downloading full m3u8, clipping,
# feature processing and predicting
def start_full_process():
  global THRET_VAL
  vodid = _G.StreamFileIndex
  data = get_video_info(vodid)
  print(f"Retrieved vod data: {data}")
  data = data.json()['data'][0]
  print(f"VodId: {vodid}\n{data}")
  
  _G.StreamFilePrefix = data['user_name'].upper()
  _G.FLAG_SAMPLE_PROC = False
  duration = hms2sec(data['duration'])
  print(f"Duration: {data['duration']} ({duration})")

  download_full_vod(vodid, duration)

  

if __name__ == "__main__":
  refresh_token()
  start_full_process()