import _G
import argv_parse
import pickle as pk

if __name__ == "__main__":
  argv_parse.init()
  _G.init()

if _G.FLAG_SAMPLE_PROC:
  files = _G.positive_data()
  dlen  = len(files)
  print(files)
  for i, file in enumerate(files):
    print(f"Loading positve data {i+1}/{dlen}")
    data = _G.load_data(file)
    print(data)
else:
  data = _G.load_data(_G.get_stream_adump_filename())
  dlen = len(data)
  for i, dat in enumerate(data):
    print(f"Window {i+1}/{dlen}")
    for k, v in dat.items():
      print(f"{k} has {len(v)} items, shape={v.shape}")
