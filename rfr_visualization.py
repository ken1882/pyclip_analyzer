import sys
import os
from os import path
from glob import glob

import matplotlib
matplotlib.use('Agg')

from matplotlib import get_backend
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import numpy as np
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestRegressor
from IPython.display import Image
from sklearn.tree import export_graphviz
import pydotplus
from collections import defaultdict
from pprint import pprint

import _G
import argv_parse

if __name__ == "__main__":
  model = _G.load_data("rfr_rolloff.mod")
  model = model.best_estimator_
  print(model)
  print(model.min_samples_split)
  print(model.max_samples)
  #export_graphviz(model.estimators_[2], out_file='tree.dot')
  for i in range(50):
    export_graphviz(model.estimators_[i], out_file=f"visualization/tree_{i}.dot")
    os.system(f"dot -Tpng visualization/tree_{i}.dot -o visualization/tree_{i}.png")
