# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 23:05:21 2016

@author: SISQUAKE
"""

import numpy as np
from time import time
from operator import itemgetter
from scipy.stats import randint as sp_randint
from sklearn.grid_search import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from numpy import genfromtxt

print(__doc__)

train_mat = genfromtxt('training.csv', delimiter=',')
y = train_mat[:, 0]
X = train_mat[:, 1:]

# build a classifier
clf = RandomForestClassifier(n_estimators=50)

# Utility function to report best scores


def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
            score.mean_validation_score,
            np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")


# specify parameters and distributions to sample from
param_dist = {"max_depth": [3, None],
              "max_features": sp_randint(1, 11),
              "min_samples_split": sp_randint(1, 11),
              "min_samples_leaf": sp_randint(1, 11),
              "bootstrap": [True, False],
              "criterion": ["gini", "entropy"]}

# run randomized search
n_iter_search = 20
random_search = RandomizedSearchCV(clf, param_distributions=param_dist, n_iter=n_iter_search, n_jobs=2)
start = time()
random_search.fit(X, y)
print("RandomizedSearchCV took %.2f seconds for %d candidates"
      " parameter settings." % ((time() - start), n_iter_search))

# report(random_search.grid_scores_)
inst = genfromtxt('instance.csv', delimiter=',')
out = random_search.predict(inst[:, 1:])
s = np.vstack([map(lambda x:(int(x)), inst[:, 0]), map(lambda x:(int(x)), out)]).T
pred = map(lambda x: [str(x[0]), str(x[1])], s)
np.savetxt("pred.csv", pred, delimiter=",", fmt="%s")
