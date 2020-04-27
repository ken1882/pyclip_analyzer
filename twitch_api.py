import requests
import json
from pprint import PrettyPrinter

headers = {
  'Client-ID': '5rd8s9anlosatjam43lh289svux4p3'
}

pp = PrettyPrinter(indent=2)

def get_clip(id):
  url = "https://api.twitch.tv/helix/clips"
  params = {
    'id': id
  }
  requests.get(url, headers=headers, params=params)

def get_video(id):
  url = "https://api.twitch.tv/helix/videos"
  params = {
    'id': id
  }
  requests.get(url, headers=headers, params=params)


# respose = get_clip('OilyDignifiedPoxDansGame')
respose = get_video('596905684')

print(respose)
pp.pprint(eval(respose.text))