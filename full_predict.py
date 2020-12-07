import json
import re
from collections import defaultdict
from pprint import pprint

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import (GridSearchCV, StratifiedKFold,
                                     cross_val_score)

import _G
import argv_parse

Model = {
  "RFR_MFCC": _G.load_data("rfr_mfcc.mod"),
  "RFR_ROLLOFF": _G.load_data("rfr_rolloff.mod"),
}

def getframe_timestamp_period(idx):
  return [idx * _G.TimeWindowSize, (idx+1) * _G.TimeWindowSize]

def process_rfr_result(result):
  score_dict = {}
  for i, v in enumerate(result):
    score_dict[i] = v
  score_dict = {k: v for k, v in sorted(score_dict.items(), key=lambda p: p[1], reverse=True)}
  print("Sorted result:")
  for i,v in score_dict.items():
    print(i, v)

def preprocessing(category, train_n, values):
  if category == "RFR_MFCC":
    dim_n = train_n // values.shape[0] - values.shape[-1]
    
    # Fill incomplete with zero
    values = np.hstack((values, np.zeros((values.shape[0], dim_n))))
    
    return values.reshape(1, -1)
  elif category == "RFR_ROLLOFF":
    dim_n = train_n - values.shape[0]
    if dim_n > 0:
      # Fill incomplete with zero
      values = np.vstack((values, np.zeros((dim_n, 1))))

    return values.reshape(1, -1)
  else:
    print(f"WARNING: {category} has no preprocessing method defined, return original values")
    return values

def predict(file):
  data = _G.load_data(file)
  print(f"Predicting {file}")
  for mod_name, model in Model.items():
    print(f"=== {mod_name} ===")
    result = defaultdict(list)
    for frame in data:
      for category, values in frame.items():
        if category in _G.IgnoredCategories:
          continue
        elif category.upper() not in mod_name:
          continue
        
        if "RFR" in mod_name:
          train_n = model.best_estimator_.n_features_
        else:
          print("WARNING: Unknown estimator", mod_name)
          break
        
        train = preprocessing(mod_name, train_n, values)
        
        try:
          result[mod_name].append(model.predict(train)[0])
        except ValueError:
          result[mod_name].append(0)
    # end for frame in data
    for mod_name in result:
      if "RFR" in mod_name:
        process_rfr_result(result[mod_name])

def load_test_data(file=None):
  if not file:
    file = _G.all_test_files()
    for f in file:
      predict(f)
  else:
    predict(file)

if __name__ == "__main__":
  argv_parse.init()
  _G.init()
  _G.IgnoredCategories += ['zcr']
  load_test_data(_G.FullVodPath)

