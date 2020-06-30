import _G
import re
import numpy as np
import argv_parse
import sklearn.svm
from sklearn.neighbors import KNeighborsClassifier
import json
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
  ret = {}
  with open(filename, 'r') as fp:
    sam_datas = json.load(fp)
    for sdata in sam_datas:
      slug = sdata['slug']
      st   = sdata['start_t']
      dur  = sdata['duration']
      ed = (st + int(dur)) // _G.TimeWindowSize
      st = int(st) // _G.TimeWindowSize
      ret[slug] = []
      for i in range(st,ed+1):
        ret[slug].append(i)
  return ret[next(iter(ret))]

data = _G.all_data_files()

models = {
  "SVM": _G.load_data("svm.mod"),
  "KNN": _G.load_data("knn.mod")
}

if SINGLE_PREDICT:
  for mod_name, model in models.items():
    print(f"=== {mod_name} ===")
    for file in data:
      parts   = re.split(r"\\|\/",file)
      labels  = load_postive_label(parts)
      dat     = _G.load_data(file)
      twlen   = len(dat)
      y_train = [1 if i in labels else 0 for i in range(twlen)]
      result  = defaultdict(list)
      for frame in dat:
        for cat, val in frame.items():
          if cat in _G.IgnoredCategories:
            continue
          try:
            train = val.reshape(1, -1)
            result[cat].append(model[cat].predict(train)[0])
          except Exception:
            pass
      print(file)
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
  for mod_name, model in models.items():
    print(f"=== {mod_name} ===")
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
          if cat in _G.IgnoredCategories:
            continue
          x_train[cat].append(val)
    y_train = np.nonzero(y_train)
    for k,v in x_train.items():
      print(k)
      train = np.array(v)
      train = train.reshape(train.shape[0], train.shape[1]*train.shape[2])
      print(np.nonzero(model[k].predict(train)))
      print('-'*10)
      print("Expected:")
      print(y_train)
