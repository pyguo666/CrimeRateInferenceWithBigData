'''
Generate taxi flow using taxi trips dataset.
Normalize it by destination or by source.
Choose normalization method and get the taxi flow matrix for inference model.

Yang Guo
'''
import csv
import numpy as np

def generateTFCount():
    f = open('data/Taxi_Trips.csv')   # This file is too large, so we provide link of it in report.
    reader = csv.DictReader(f)
    matrix_count = np.zeros((77,77))
    for row in reader:
        matrix_count[int(row['Pickup Community Area'])-1, int(row['Dropoff Community Area'])-1] += 1

    outfile = open('data/taxi_flow_count.csv', 'w')
    writer = csv.writer(outfile, delimiter=';', quotechar='"')
    writer.writerows(matrix_count)
    outfile.close()

def generateTFMatrix():
    f = open('data/taxi_flow_count.csv')
    reader = csv.reader(f, delimiter = ';')
    matrixTF = np.zeros((77,77))
    rowNum = 0
    for row in reader:
        matrixTF[rowNum] = row
        matrixTF[rowNum][rowNum] = 0
        rowNum += 1

    outfile = open('data/taxi_flow_matrix.csv', 'w')
    writer = csv.writer(outfile, delimiter=';', quotechar='"')
    writer.writerows(matrixTF)
    outfile.close()


def getTaxiFlow(leaveOut=-1, normalization='byDestination'):
    f_matrix = np.loadtxt('data/taxi_flow_matrix.csv', delimiter=';')
    n = f_matrix.shape[0]
    # print(n)

    if leaveOut > 0:
        f_matrix = np.delete(f_matrix, leaveOut - 1, 0)
        f_matrix = np.delete(f_matrix, leaveOut - 1, 1)

    n = f_matrix.shape[0]
    # print(n)

    return taxiFlowNormalization(f_matrix, normalization)


def taxiFlowNormalization(tf_matrix, method='byDestination'):
    '''
    :param tf_matrix: taxi_flow_matrix, may be modified by leaveOut factor
    :param method: you can choose normalization method between: byDestination, bySource or byCount
    :return: normalized matrix
    '''
    n = tf_matrix.shape[0]
    tf_matrix = tf_matrix.astype(float)
    if method == "byDestination":
        tf_matrix = np.transpose(tf_matrix)
        fsum = np.sum(tf_matrix, axis=1, keepdims=True)
        fsum[fsum == 0] = 1
        assert fsum.shape == (n, 1)
        tf_matrix = tf_matrix / fsum
        np.testing.assert_almost_equal(tf_matrix.sum(), n)
        np.testing.assert_almost_equal(tf_matrix.sum(axis=1)[n - 1], 1)
    elif method == "bySource":
        fsum = np.sum(tf_matrix, axis=1, keepdims=True)
        fsum[fsum == 0] = 1
        tf_matrix = tf_matrix / fsum
        assert fsum.shape == (n, 1)
        np.testing.assert_almost_equal(tf_matrix.sum(axis=1)[n - 1], 1)
    elif method == "byCount":
        pass

    return tf_matrix

if __name__ == '__main__':
    generateTFMatrix()
    m = getTaxiFlow()
    print(m)

    # generateTFCount()