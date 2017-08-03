'''
Use linear model to do crime rate inference.

Yang Guo
'''
from sklearn.model_selection import LeaveOneOut
from sklearn import linear_model
import csv
import numpy as np

from POI import getPOICount
from geographic_influence import generate_geographical_influence
from demographics import generate_demographics_feature, retrieve_crimerate
from taxi_flow import getTaxiFlow

def linearRegression(features, Y):
    model_linear = linear_model.LinearRegression()
    res = model_linear.fit(features, Y)
    return res

def generateFeatures(features = ['demos', 'poi', 'geo', 'tf'], leaveOut = -1):
    Y = retrieve_crimerate()
    Y = Y.reshape((-1,1))

    if leaveOut > 0:
        Y = np.delete(Y, leaveOut-1, 0)

    if 'demos' in features:
        demos = generate_demographics_feature(leaveOut)

    if 'poi' in features:
        poi = getPOICount(leaveOut)

    if 'geo' in features:
        geo = generate_geographical_influence(leaveOut)
        f_geo = np.dot(geo, Y)

    if 'tf' in features:
        tf = getTaxiFlow(leaveOut, 'byDestination')
        f_taxi = np.dot(tf, Y)



    F = np.ones(f_geo.shape)
    if 'demos' in features:
        F = np.concatenate((F, demos), axis= 1)
    if 'poi' in features:
        F = np.concatenate((F, poi), axis= 1)
    if 'geo' in features:
        F = np.concatenate((F, f_geo), axis= 1)
    if 'tf' in features:
        F = np.concatenate((F, f_taxi), axis= 1)

    return F, Y

def crimeLR():
    F, Y = generateFeatures()
    err = []

    for i in range(len(Y)):
        F_train, Y_train = generateFeatures(leaveOut=i+1)

        mod = linearRegression(F_train, Y_train)
        y_predict = mod.predict(F[i,])
        err.append(abs(Y[i]-y_predict))

        print(i+1)
        print(y_predict)

    print(np.mean(err))

def LRTraining(features, Y):
    errors = []
    loo = LeaveOneOut()
    for train_index, test_index in loo.split(Y):
        train_Y = Y[train_index]
        train_features = features[train_index]
        model_LR = linearRegression(train_features, train_Y)
        y_predict = model_LR.predict(features[test_index])
        errors.append(abs(y_predict - Y[test_index]))

    return np.mean(errors), np.mean(errors)/np.mean(Y)



if __name__ == '__main__':
    crimeLR()

    # f, y = generateFeatures(leaveOut=3)
    # print(y)
    # print(f)