import _G
import re
import numpy as np
import argv_parse
import sklearn.svm
from collections import defaultdict

SINGLE_PREDICT = True

argv_parse.init()
_G.init()

# parts: splited path of the origin data
#        used to locate postive label file path
def load_postive_label(parts):
  broardcaster = parts[1]
  episode = parts[2]
  filename = f"{_G.PositiveSampleFolder}/{broardcaster}/{episode}/{_G.PostiveLabelFilename}"
  ret = []
  with open(filename, 'r') as fp:
    for line in fp:
      st, ed = line.split(':')
      st = int(st) // _G.TimeWindowSize
      ed = int(ed) // _G.TimeWindowSize
      for i in range(st,ed+1):
        ret.append(i)
  return ret

models = {}
for cat in _G.Categories:
  models[cat] = _G.load_data(f"{cat}.mod")

data = _G.all_data_files()

if SINGLE_PREDICT:
  for file in data:
    parts   = re.split(r"\\|\/",file)
    labels  = load_postive_label(parts)
    dat     = _G.load_data(file)
    twlen   = len(dat)
    y_train = [1 if i in labels else 0 for i in range(twlen)]
    result  = defaultdict(list)
    for frame in dat:
      for cat, val in frame.items():
        train = val.reshape(1, -1)
        result[cat].append(models[cat].predict(train)[0])
    
    for k,ar in result.items():
      print(k)
      printed = False
      for i,v in enumerate(ar):
        if v != 0:
          print(i, v)
          printed = True
      if not printed:
        print(ar)
      print('-'*10)
    print("Expected:")
    for i,v in enumerate(y_train):
      if v != 0:
        print(i)
    print('='*10)
else:
  x_train  = defaultdict(list)
  y_train  = []
  for file in data:
    parts  = re.split(r"\\|\/",file)
    labels = load_postive_label(parts)
    dat    = _G.load_data(file)
    twlen  = len(dat)
    y_train.extend([1 if i in labels else 0 for i in range(twlen)])
    result  = defaultdict(list)
    for frame in dat:
      for cat, val in frame.items():
        x_train[cat].append(val)
  y_train = np.nonzero(y_train)
  for k,v in x_train.items():
    print(k)
    train = np.array(v)
    train = train.reshape(train.shape[0], train.shape[1]*train.shape[2])
    print(np.nonzero(models[k].predict(train)))
    print('-'*10)
    print("Expected:")
    print(y_train)
