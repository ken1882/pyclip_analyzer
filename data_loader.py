import _G
import argv_parse
import pickle as pk
from glob import glob

if __name__ == "__main__":
  argv_parse.init()
  _G.init()

  path  = input("Enter path: ")
  files = glob(f"{path}/*audio*.dat")
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
