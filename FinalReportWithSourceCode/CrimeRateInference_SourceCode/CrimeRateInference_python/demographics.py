'''
Generate demographic features from demographics.csv.
Retrieve crime rate Y from this file.

Yang Guo
'''
import numpy as np
import csv

def generate_demographics_feature(leaveOut = -1):
    f = open('data/demographics.csv')
    reader_demo = csv.DictReader(f)
    features = []
    flag = 0
    for row in reader_demo:
        if int(row['Community #']) > flag:
            features.append([row['Total_Population'], row['NHW_P'], row['NHB_P'], row['Poverty_P']])
            flag += 1

    features = np.asarray(features, dtype=np.float)

    if leaveOut > 0:
        features = np.delete(features, leaveOut - 1, 0)

    return features

def retrieve_crimerate(year = '2013'):
    f = open('data/demographics.csv')
    reader_demo = csv.DictReader(f)
    y = []  # y is crime rate vecctor
    flag = 0
    for row in reader_demo:
        if int(row['Community #']) > flag:
            y.append(row['crime_rate'])
            flag += 1

    y = np.asarray(y, dtype=np.float)

    return y

if __name__ == '__main__':
    demos = generate_demographics_feature()
    y = retrieve_crimerate()

    print(demos.shape)
    print(y.shape)