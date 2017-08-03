import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import fiona
from shapely.geometry import Point, asShape, shape, MultiPolygon
import numpy as np
import csv
import tkinter

def visualize_community():
    mp_list = []

    f_shape = fiona.open('shapeFile_Chicago/geo_export_01.shp')

    for community_shape in f_shape:
        mp = shape(community_shape['geometry'])
        mp_list.append(mp)

    mp = MultiPolygon(mp_list)


    cm = plt.get_cmap('RdBu')
    num_colours = len(mp)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx, miny, maxx, maxy = mp.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)

    patches = []
    for idx, p in enumerate(mp):
        colour = cm(1. * idx / num_colours)
        patches.append(PolygonPatch(p, fc=colour, ec='#555555', alpha=1., zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shape of Chicago")
    # plt.savefig('data/Chicago_map.png', alpha=True, dpi=300)
    plt.show()

if __name__ == '__main__':
    visualize_community()