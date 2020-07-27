import _G
import argv_parse
import pickle as pk
from glob import glob

# positive_samples/ESL_DOTA2/_vod580483021_ClumsyTangibleElkDogFace
# positive_samples/ESL_DOTA2/_vod73096810_ConcernedSmellyWaterKlappa

if __name__ == "__main__":
  argv_parse.init()
  _G.init()
  print(_G.positive_audios())
  path  = input("Enter path: ")
  files = sorted(glob(f"{path}/*audio*.dat"))
  for file in files:
    print(f"Loading {file}")
    data = _G.load_data(file)  
    dlen = len(data)
    for i, dat in enumerate(data):
      print(f"Window {i+1}/{dlen}")
      for k, v in dat.items():
        print(f"{k} has {len(v)} items, shape={v.shape}")
        print(v)
        print("-"*10)
