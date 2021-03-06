import os
import requests

FLAG_REFRESH = True
APIHeader = {}


# Load API Header settings
with open("twitch_api.key", 'r') as fp:
  for line in fp:
    if not line.strip():
      continue
    key, val = line.split(":")
    if key == "Client-ID":
      APIHeader['client_id'] = val.strip()
    elif key == "Refresh":
      APIHeader['refresh_token'] = val.strip()

APIHeader['client_secret'] = os.environ['TWITCHAPI_SECRET']

CodeHeader = {
  "client_id": APIHeader['client_id'],
  "redirect_uri": "http://localhost",
  "response_type": 'code',
  "scope": "viewing_activity_read"
}

def refresh_token():
  APIHeader['grant_type'] = "refresh_token"
  resp = requests.post("https://id.twitch.tv/oauth2/token", data=APIHeader)
  return resp.json()

if __name__ == "__main__":
  if not FLAG_REFRESH:
    CodeUri = "https://id.twitch.tv/oauth2/authorize?" + \
            f"client_id={APIHeader['client_id']}&" + \
            f"redirect_uri=http://localhost&" + \
            f"response_type=code&" + \
            f"scope=viewing_activity_read"

    print(CodeUri)
    APIHeader['code'] = input("Please enter the code: ").strip()
    APIHeader['redirect_uri'] = "http://localhost"
    APIHeader['grant_type'] = "authorization_code"
    print(APIHeader)
    resp = requests.post("https://id.twitch.tv/oauth2/token", data=APIHeader)
    print(resp.json())
  else:
    print(APIHeader)
    print(refresh_token())