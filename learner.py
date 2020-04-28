import _G
import numpy as np
import re
from sklearn import svm
from collections import defaultdict

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

_G.init()
data = _G.all_data_files()
x_train = defaultdict(list)
y_train = []

for file in data:
  parts  = re.split(r"\\|\/",file)
  labels = load_postive_label(parts)
  dat    = _G.load_data(file)
  twlen  = len(dat)
  tmp_y  = [1 if i in labels else 0 for i in range(twlen)]
  y_train.append(tmp_y)
  for cat in _G.Categories:
    for frame in dat:
      x_train[cat].append(frame[cat])

y_train = np.array(y_train).flatten()
classifier = {k:svm.SVC() for k in _G.Categories}

for cat in _G.Categories:
  print(cat)
  train = np.array(x_train[cat])
  print(train.shape)
  train = train.reshape(train.shape[0], train.shape[1]*train.shape[2])
  print(train.shape)
  classifier[cat].fit(train, y_train)
  _G.dump_data(classifier[cat], f"{cat}.mod")