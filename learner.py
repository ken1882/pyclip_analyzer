import _G
import argv_parse
import numpy as np
import re
import json
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from collections import defaultdict

VERBOSE = 1
N_JOBS  = -1

if __name__ == "__main__":
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
  return ret

data = _G.all_data_files()
x_train = defaultdict(list)
y_train = []
base = 0
incom_idx = []
for file in data:
  parts  = re.split(r"\\|\/",file)
  labels = load_postive_label(parts)
  dat    = _G.load_data(file)
  twlen  = len(dat)
  for key in labels:
    tmp_y  = [1 if i in labels[key] else 0 for i in range(twlen)]
    base = len(y_train)
    y_train.extend(tmp_y)
    for idx,frame in enumerate(dat):
      if frame[_G.Categories[0]].shape != dat[0][_G.Categories[0]].shape:
        print(f"Frame#{base+idx} is incomplete, discard")
        incom_idx.append(base+idx)
        continue
      
      data_ok = False
      for cat in _G.Categories:
        infidx = np.where(np.isinf(frame[cat]))
        if len(infidx[0]) > 0:
          print(f"WARNING: INF value in frame#{idx} of {cat} in {file}")
          print("INF val idx: ", infidx)
          print(frame[cat][infidx])
          print("This frame will be discarded")
          incom_idx.append(base+idx)
          break
        x_train[cat].append(frame[cat])
      
      if not data_ok:
        continue

for i in reversed(incom_idx):
  del y_train[i]

y_train = np.array(y_train).flatten()

print(f"Yt: {y_train.shape}\n{y_train}")

kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
parm_svm = {'kernel':['linear', 'rbf', 'poly', 'sigmoid'], 'C':[0.01, 0.1, 1, 10]}
parm_knn = {'n_neighbors':[1,3,5,7]}

clsier_svm = {}
clsier_knn = {}

print("----- Training Proc -----")
for cat in _G.Categories:
  if cat in _G.IgnoredCategories:
    continue
  if cat == 'mfcc':
    continue
  clsier_svm[cat] = GridSearchCV(estimator=svm.SVC(), param_grid=parm_svm, scoring='accuracy',cv=5,verbose=VERBOSE,n_jobs=N_JOBS)
  clsier_knn[cat] = GridSearchCV(estimator=KNeighborsClassifier(), param_grid=parm_knn, scoring='accuracy',cv=5,verbose=VERBOSE,n_jobs=N_JOBS)
  print(cat)
  train = np.array(x_train[cat])
  print(train.shape)
  train = train.reshape(train.shape[0], train.shape[1]*train.shape[2])
  print(train.shape)
  
  print("Training SVM")
  clsier_svm[cat].fit(train, y_train)
  print("Best params: ", clsier_svm[cat].best_params_)
  
  # print("Training KNN")
  # clsier_knn[cat].fit(train, y_train)
  # print("Best params: ", clsier_knn[cat].best_params_)
  
print("Dumping data")
_G.dump_data(clsier_svm, f"svm2.mod")
# _G.dump_data(clsier_knn, f"knn.mod")
# for cat in _G.Categories:
#   if cat in _G.IgnoredCategories:
#     continue
#   print("Cross-vaildating")
#   score_svm = cross_val_score(clsier_svm[cat], train, y_train, scoring='accuracy', cv=kfold, verbose=VERBOSE,n_jobs=N_JOBS)
#   score_knn = cross_val_score(clsier_knn[cat], train, y_train, scoring='accuracy', cv=kfold, verbose=VERBOSE,n_jobs=N_JOBS)
#   print("SVM score: ", score_svm)
#   print("KNN score: ", score_knn)