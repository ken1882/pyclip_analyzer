import _G
import re
import numpy as np
import argv_parse
import sklearn.svm
from sklearn.neighbors import KNeighborsClassifier
import json
from collections import defaultdict

# If sample score is above average multiple this value
# then it'll be selected
RFR_OKTHRESHOLD = 1 

if __name__ == "__main__":
  argv_parse.init()
  _G.init()
  _G.IgnoredCategories += ['zcr', 'mfcc']

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
  "SVM": _G.load_data("svm_rolloff.mod"),
  "KNN": _G.load_data("knn_rolloff.mod"),
  "RFR": _G.load_data("rfr_rolloff.mod")
}

for mod_name, model in models.items():
  print(f"=== {mod_name} ===")
  ok_cnt = 0
  nonok_cnt = 0
  total_frame = 0
  real_ok_cnt = 0
  for file in data:
    parts   = re.split(r"\\|\/",file)
    if len(parts[2].split('_')[-1]) < 3:
      continue
    labels  = load_postive_label(parts)
    dat     = _G.load_data(file)
    twlen   = len(dat)
    y_train = [1 if i in labels else 0 for i in range(twlen)]
    result  = defaultdict(list)
    for frame in dat:
      for cat, val in frame.items():

        if cat in _G.IgnoredCategories:
          continue
        
        if mod_name == "SVM":
          train_n = model.best_estimator_.shape_fit_[-1]
        elif mod_name == "KNN":
          train_n = model.best_estimator_._tree.data.shape[-1]
        elif mod_name == "RFR":
          train_n = model.best_estimator_.n_features_
          
        dim_n = train_n - val.shape[0]
        if dim_n > 0:
          val = np.vstack((val, np.zeros((dim_n, 1))))
        train = val.reshape(1, -1)
        try:
          result[cat].append(model.predict(train)[0])
        except ValueError:
          result[cat].append(0)
        
    print(file)
    passed_frame = []
    for k,ar in result.items():
      print(k)
      printed = False
      if mod_name == "RFR":
        ar = np.array(ar)
        pass_idx = np.nonzero(np.where(ar > np.average(ar[np.nonzero(ar)]) * RFR_OKTHRESHOLD, ar, 0))[0]
        if len(pass_idx) > 0:
          for i in pass_idx:
            print(i, ar[i])
            passed_frame.append(i)
          printed = True
      else:
        for i,v in enumerate(ar):
          if v != 0:
            print(i, v)
            passed_frame.append(i)
            printed = True
        if not printed:
          print(ar)
      print('-'*10)
    print("Expected:")
    total_frame += len(y_train)
    for i,v in enumerate(y_train):
      if v != 0:
        real_ok_cnt += 1
        print(i)
      if v != 0 and i in passed_frame:
        ok_cnt += 1
      if v == 0 and i in passed_frame:
        nonok_cnt += 1
    print('='*10)
  
  print("\nSummary:")
  print(f"True Positive: {ok_cnt}/{real_ok_cnt} ({ok_cnt/max(real_ok_cnt,1)})")
  print(f"False Positive: {nonok_cnt}/{total_frame - real_ok_cnt} ({nonok_cnt / (total_frame - real_ok_cnt)})")

