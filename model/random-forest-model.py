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
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

from numpy import genfromtxt
from optparse import OptionParser

print(__doc__)

TRAINING_INPUT_DIRECTORY = '../../traing_data'

parser = OptionParser()
parser.add_option("-t", dest="TRAINING_INPUT_DIRECTORY")
(options, args) = parser.parse_args()

if options.TRAINING_INPUT_DIRECTORY is not None:
    TRAINING_INPUT_DIRECTORY = options.TRAINING_INPUT_DIRECTORY

# From demonstration , we only used  4 of 5 histrical data for training
train_mat = genfromtxt(TRAINING_INPUT_DIRECTORY+'/training_matrix.csv', delimiter=',')
# First column is the lable column
y = train_mat[:, 0]
X = train_mat[:, 1:]

# build a classifier, in this demo we use Random Forest, you can switch to any other classifier
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
param_dister = {"max_depth": [3, None],
                "max_features": sp_randint(1, 11),
                "min_samples_split": sp_randint(1, 11),
                "min_samples_leaf": sp_randint(1, 11),
                "bootstrap": [True, False],
                "criterion": ["gini", "entropy"]}

# run randomized search
n_iter_search = 20
random_search = RandomizedSearchCV(clf, param_distributions=param_dister, n_iter=n_iter_search, n_jobs=2)
start = time()
random_search.fit(X, y)

print("RandomizedSearchCV took %.2f s for %d candidates"" parameter settings." % ((time() - start), n_iter_search))

report(random_search.grid_scores_)

# Load the testing data
test_mat = genfromtxt(TRAINING_INPUT_DIRECTORY+'/testing_matrix.csv', delimiter=',')

test_y = test_mat[:, 0]
test_x = test_mat[:, 1:]

y_true, y_pred = test_y, random_search.predict(test_x)

print("Raw metirc result :")
print(classification_report(y_true, y_pred))
print('Accuracy : ' + str(accuracy_score(y_true, y_pred)) + '\n')

mod_y_pred = map(lambda x: x if x == 1 else -1, y_pred)
mod_y_true = map(lambda x: x if x == 1 else -1, y_true)

print("More reasonable metirc result : ")
print(classification_report(mod_y_true, mod_y_pred))
print('Accuracy : ' + str(accuracy_score(mod_y_true, mod_y_pred)) + '\n')
