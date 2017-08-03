import numpy as np
import csv
import fiona
from shapely.geometry import Point, asShape, shape

def generate_poiCount():
    f_shape = fiona.open('shapeFile_Chicago/geo_export_01.shp')

    # point = Point( -87.805336, 41.980726)
    # for feature in f_shape:
    #     s = asShape(feature['geometry'])
    #     if s.contains(point):
    #         print(feature['properties']['community'])
    #         print(feature['properties']['area_numbe'])

    f_poi = open('data/poi_original.csv')
    reader_poi = csv.reader(f_poi, delimiter = ',')

    matrix_poi = np.zeros((77,9))
    # only one event poi, so just use 9 poi features
    index_poi = {'Food':0, 'Residence':1, 'Travel & Transport':2, 'Arts & Entertainment':3, 'Outdoors & Recreation':4,
             'College & University':5, 'Nightlife Spot':6, 'Professional & Other Places':7, 'Shop & Service':8}

    for row in reader_poi:
        point = Point(float(row[1]), float(row[0]))
        for community_shape in f_shape:
            s = asShape(community_shape['geometry'])
            if s.contains(point):
                matrix_poi[int(community_shape['properties']['area_numbe'])-1][index_poi[row[2]]] += 1
                break

    np.savetxt('data/poi_cnt_matrix.csv', matrix_poi, delimiter= ',')
    print(matrix_poi)


def getPOICount(leaveOut = -1):
    matrix_poi = np.loadtxt('data/poi_cnt_matrix.csv', delimiter= ',')

    if leaveOut > 0:
        matrix_poi = np.delete(matrix_poi, leaveOut-1, 0)

    return matrix_poi

if __name__ == '__main__':
    # generate_poiCount()   # it takes very long to run this method.
    m = getPOICount()
    print(m)


