'''
Generate geographic influence matrix using centroids of each community area.
Use it to form the feature of inference model.

Yang Guo
'''
import csv
import numpy as np
import heapq
from math import sqrt
import fiona
from shapely.geometry import Point, asShape, shape,Polygon



def generate_geographical_influence(leaveOut = -1):
    '''
    :param leaveOut: select community area and remove from the training set
    :return: 1/distance matrix
    '''
    f_Chicago = fiona.open('shapeFile_Chicago/geo_export_01.shp')
    centroids = csv.reader(open('data/centroid_community.csv'), delimiter = ';')
    cas = {}

    for row in centroids:
        # print(row[2])
        # cas.append({int(row[0]): [row[1], row[2]]})
        cas[int(row[0])] = [float(row[1]), float(row[2])]

    cSet = list(range(1, 78))
    if leaveOut > 0:
        cSet.remove(leaveOut)
    # print(cSet)

    centers = {}
    for i in cSet:
        centers[i] = cas[i]

    W = np.zeros((len(cSet),len(cSet)))
    for i in cSet:
        for j in cSet:
            if i != j:
                if leaveOut < 0:
                    W[i-1][j-1] = 1 / sqrt((1000*(centers[i][0]-centers[j][0]))**2 + (1000*(centers[i][1]-centers[j][1]))**2)
                elif leaveOut > 0:
                    k = i
                    l = j
                    if i > leaveOut:
                        k -= 1
                    if j > leaveOut:
                        l -= 1
                    W[k - 1][l - 1] = 1 / sqrt(
                         (1000 * (centers[i][0] - centers[j][0])) ** 2 + (1000 * (centers[i][1] - centers[j][1])) ** 2)

    for i in range(len(cSet)):
        # find largest 6 value
        threshold = heapq.nlargest(6, W[i, :])[-1]
        for j in range(len(cSet)):
            if W[i ][j] < threshold:
                W[i][j] = 0
    return W




if __name__ == '__main__':
    #test
    w = generate_geographical_influence(3)

    print(w.shape)
    for row in w:
        print(row)
