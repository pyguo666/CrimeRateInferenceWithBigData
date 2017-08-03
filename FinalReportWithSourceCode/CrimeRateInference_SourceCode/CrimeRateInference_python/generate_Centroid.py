'''
Extract centroid of each community area using a part of taxi trips dataset.
Save it in 'data/centroid_community.csv'

Yang Guo
'''
import csv

f = open('data/taxiTripsPart.csv')
reader = csv.DictReader(f)

res = []
flag = 0
for row in reader:
    if int(row['Pickup Community Area']) > flag:
        res.append([row['Pickup Community Area'], row['Pickup Centroid Latitude'], row['Pickup Centroid Longitude']])
        flag += 1


outfile = open('data/centroid_community.csv','w')
writer = csv.writer(outfile, delimiter=';', quotechar='"')
writer.writerows(res)
outfile.close()