import _G
import argv_parse
import numpy as np
import re
import json
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict
from pprint import pprint

VERBOSE = 1
N_JOBS  = 1
GRID_CV = 5
Category = 'rolloff'
TRAIN_SVM = False
TRAIN_KNN = False
TRAIN_RFR = True

if __name__ == "__main__":
  argv_parse.init()
  _G.init()
  N_JOBS = -1
  
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
x_train = []
y_train = []
base = 0
incom_idx = []

max_nsize = 0
cnt = 0
for file in data:
  parts  = re.split(r"\\|\/",file)
  if len(parts[2].split('_')[-1]) < 3:
    continue
  labels = load_postive_label(parts)
  dat    = _G.load_data(file)
  frame_len = len(dat)
  print(frame_len, file)
  for key in labels:
    tmp_y  = [1 if i in labels[key] else 0 for i in range(frame_len)]
    base = len(y_train)
    y_train.extend(tmp_y)
    for idx, frame in enumerate(dat):
      cnt += 1
    for idx,frame in enumerate(dat):
      infidx = np.where(np.isinf(frame[Category]))
      if len(infidx[0]) > 0:
        print(f"WARNING: INF value in frame#{idx} of {Category} in {file}")
        print("INF val idx: ", infidx)
        print(frame[Category][infidx])
        print("This frame will be discarded")
        incom_idx.append(base+idx)
        continue
      
      nlen = frame[Category].shape[0]
      max_nsize = max_nsize if max_nsize >= nlen else nlen
      x_train.append(frame[Category])

for i in reversed(incom_idx):
  del y_train[i]

# include negative samples
if _G.FLAG_TRAIN_NEGATIVE:
  print("Loading negative samples...")
  neg_files = _G.all_negative_files()
  for file in neg_files:
    frame = _G.load_data(file)[0][Category]
    nlen  = frame.shape[0]
    max_nsize = max_nsize if max_nsize >= nlen else nlen
    x_train.append(frame)
    y_train.append(0)

y_train = np.array(y_train).flatten()

print(f"Sample Size: {len(data)}")
print(f"Yt: {y_train.shape}\n{y_train}\n{np.nonzero(y_train)}\n\n")

for idx, freq_col in enumerate(x_train):
  nlen = freq_col.shape[0]
  if nlen >= max_nsize:
    continue
  x_train[idx] = np.vstack((freq_col, np.zeros((max_nsize - nlen, 1))))

kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

parm_svm = {'kernel':['linear', 'rbf', 'poly', 'sigmoid'], 'C':[0.01, 0.1, 1, 10]}
parm_knn = {'n_neighbors':[1,3,5,7,9], 'algorithm': ['ball_tree', 'kd_tree', 'brute']}
parm_rfr = {'n_estimators':[16,32,50,75,128,256], 'bootstrap': [True, False], 'max_depth':[None,3,5,7,10,16], 'min_samples_split': [2,3,5,10,20,30], 'random_state': [42]}

print("----- Training Proc -----")

clsier_svm = GridSearchCV(estimator=svm.SVC(), param_grid=parm_svm, scoring='accuracy',cv=5,verbose=VERBOSE,n_jobs=N_JOBS)
clsier_knn = GridSearchCV(estimator=KNeighborsClassifier(), param_grid=parm_knn, scoring='accuracy',cv=5,verbose=VERBOSE,n_jobs=N_JOBS)
clsier_rfr = GridSearchCV(estimator=RandomForestRegressor(), param_grid=parm_rfr, scoring='explained_variance',cv=GRID_CV,verbose=VERBOSE,n_jobs=N_JOBS)

x_train = np.array(x_train, dtype=object)
x_train = x_train.reshape(x_train.shape[0], x_train.shape[1]*x_train.shape[2])
print(f"Reshaped size: {x_train.shape}")


if TRAIN_SVM:
  print("Training SVM")
  clsier_svm.fit(x_train, y_train)
  print("Best params: ", clsier_svm.best_params_)
  print("Result:")
  pprint(clsier_svm.cv_results_)
  print("Dumping SVM data")
  _G.dump_data(clsier_svm, f"svm_rolloff.mod")

if TRAIN_KNN:
  print("Training KNN")
  clsier_knn.fit(x_train, y_train)
  print("Best params: ", clsier_knn.best_params_)
  print("Result:")
  pprint(clsier_knn.cv_results_)
  print("Dumping KNN data")
  _G.dump_data(clsier_knn, f"knn_rolloff.mod")

if TRAIN_RFR:
  print("Training Random Forest")
  clsier_rfr.fit(x_train, y_train)
  print("Best params: ", clsier_rfr.best_params_)
  print("Result:")
  pprint(clsier_rfr.cv_results_)
  _G.dump_data(clsier_rfr, f"rfr_rolloff.mod")
# exit()

print("===== Start Cross-Vaildating =====")

print(f"Cross-vaildating {Category}")
if TRAIN_SVM:
  score_svm = cross_val_score(clsier_svm, x_train, y_train, scoring='accuracy', cv=kfold, verbose=VERBOSE,n_jobs=N_JOBS)
  print("SVM score: ", score_svm)

if TRAIN_KNN:
  score_knn = cross_val_score(clsier_knn, x_train, y_train, scoring='accuracy', cv=kfold, verbose=VERBOSE,n_jobs=N_JOBS)
  print("KNN score: ", score_knn)

if TRAIN_RFR:
  score_rfr = cross_val_score(clsier_rfr, x_train, y_train, scoring='explained_variance', cv=kfold, verbose=VERBOSE,n_jobs=N_JOBS)
  print("Random Forest Regressor score: ", score_rfr)