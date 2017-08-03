'''
Use NB model.

Yang Guo
'''

from sklearn.model_selection import LeaveOneOut
import csv
import numpy as np
from linearRegression import  generateFeatures
from POI import getPOICount
from geographic_influence import generate_geographical_influence
from demographics import generate_demographics_feature, retrieve_crimerate
from taxi_flow import getTaxiFlow
from scipy.stats import nbinom
from statsmodels.base.model import GenericLikelihoodModel
import statsmodels.api as sm

def NBTraining(features, Y):
    '''
    Use statsmodels library.
    '''
    errors = []
    loo = LeaveOneOut()
    for train_index, test_index in loo.split(Y):
        train_Y = Y[train_index]
        train_features = features[train_index]
        model_NB = sm.GLM(train_Y, train_features, family=sm.families.NegativeBinomial())
        model_res = model_NB.fit()
        y_predict = model_NB.predict(model_res.params, features[test_index])
        errors.append(abs(y_predict - Y[test_index]))

    return np.mean(errors), np.mean(errors)/np.mean(Y)


def test_crime():
    F, Y = generateFeatures()
    e = NBTraining(F, Y)
    print(e)

if __name__ == '__main__':
    test_crime()

