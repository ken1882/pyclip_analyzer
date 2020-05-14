import requests
import urllib.request
import json
import os
import re
from bs4 import BeautifulSoup
from random import randint
from pprint import PrettyPrinter
from threading import Thread
import moviepy.editor as mp

import _G
import argv_parse
import clip
import analyzer

if __name__ == "__main__":
  argv_parse.init()
  _G.init()

NewHeader = {
  'Client-ID': '5rd8s9anlosatjam43lh289svux4p3',
  'Authorization': 'Bearer g1efsf63d24sal5syoeyqshp81i3ue',
  'Accept': 'application/vnd.twitchtv.v5+json'
}


OldHeaders = {
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
  return requests.get(url, headers=NewHeader, params=params)

def getkarkan_clip_info(slug):
  url = f"https://api.twitch.tv/kraken/clips/{slug}"
  return requests.get(url, headers=NewHeader)

def get_video_info(id):
  url = "https://api.twitch.tv/helix/videos"
  params = {
    'id': id
  }
  return requests.get(url, headers=NewHeader, params=params)

def get_m3u8_info(id):
  url = f"https://api.twitch.tv/api/vods/{id}/access_token"
  response = requests.get(url, headers=OldHeaders).json()
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

def _download_m3u8(id, info, start_t, duration):
  filename = f"{_G.StreamFolder}/{_G.StreamFilePrefix}_vod{id}.{_G.VideoFormat}"
  cmd = _G.FFmpegDownloadCmd.format(start_t, info[2], duration, filename)
  os.system(f"echo {cmd}")

def download_m3u8_async(id, start_t, duration):
  _G.ensure_dir_exist(f"{_G.StreamFolder}/")
  info = get_m3u8_info(id)
  Thread(target=_download_m3u8, args=(id,info,start_t,duration)).start()

def download_clip(id, slug):
  data = get_helixclip_info(slug).json()
  data = data['data'][0]
  print(f"Retrived data: {data}")
  
  video_uri = f"{data['thumbnail_url'].split('-preview')[0]}.{_G.VideoFormat}"
  filename = f"{_G.PositiveSampleFolder}/{_G.StreamFilePrefix}/_vod{id}/{slug}.{_G.VideoFormat}"
  _G.ensure_dir_exist(filename)
  
  with open(filename, 'wb') as file:
    print(f"Downloading {video_uri} to {filename}...")
    file.write(requests.get(video_uri).content)
  return filename

# data: Karken clip data
def get_ori_timestamp(data):
  return hms2sec(data['vod']['url'].split('t=')[1])

def download_ori_partial(id, slug):
  data = getkarkan_clip_info(slug).json()
  start_t = hms2sec(data['vod']['url'].split('t=')[1])
  start_t, duration = _G.get_download_timeinfo(start_t)
  print(start_t, duration)

def get_id_from_data(data):
  return data['vod']['id']

def get_id_from_slug(slug):
  data = getkarkan_clip_info(slug).json()
  return data['vod']['id']

def generate_label(clip_fname, start_t):
  label_filename = f"{_G.PositiveSamplePath}/{_G.PostiveLabelFilename}"
  duration = int(clip.load_video(clip_fname).duration + 0.5)
  start_t  = start_t - _G.get_download_timeinfo(start_t)[0]
  with open(label_filename, 'w') as file:
    file.write(f"{start_t}:{duration}")


def start_sample_process():
  slug = _G.ClipName
  data = getkarkan_clip_info(slug).json()
  id   = get_id_from_data(data)
  start_t = get_ori_timestamp(data)
  
  _G.StreamFileIndex = int(id)
  _G.init()

  clip_fname = download_clip(id, slug)
  generate_label(clip_fname, start_t)
  
  # ori_st, duration = _G.get_download_timeinfo(start_t)
  # download_m3u8_async(id, ori_st, duration)

# download_m3u8(_G.StreamFileIndex, 0, 30)
# print(get_helixclip_info("SecretiveLazyVelociraptorBCWarrior").json())
# download_clip("SecretiveLazyVelociraptorBCWarrior")
# download_ori_partial(0, "SecretiveLazyVelociraptorBCWarrior")
# print(get_id_from_slug("SecretiveLazyVelociraptorBCWarrior"))

if __name__ == "__main__":
  start_sample_process()