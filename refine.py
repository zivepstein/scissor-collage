from __future__ import division
import os, json, colorsys, bisect, math
import networkx as nx
from scipy.spatial import distance
from scipy import misc
import numpy as np
from werkzeug.utils import secure_filename
from image_processing.color_cluster import cluster_color
from PIL import Image

EPSILON = 10
NUM_COLORS = 5
AREA = 50000

def test():
    source = Image.open("source.jpg")
    source_area = source.size[0] * source.size[1]
    alpha = math.sqrt(AREA/source_area)
    source = source.resize((int(alpha*source.size[0]), int(alpha*source.size[1])), Image.BILINEAR)
    source.save("source.jpg")

    target = Image.open("target.jpg")
    target_area = target.size[0] * target.size[1]
    alpha = math.sqrt(AREA/target_area)
    target = target.resize((int(alpha*target.size[0]), int(alpha*target.size[1])), Image.BILINEAR)
    target.save("target.jpg")

    source = misc.imread("source.jpg")
    target = misc.imread("target.jpg")
    os.system('node triangulate.js source.jpg 1')
    os.system('node triangulate.js target.jpg 2')
    with open('json-out/1.json') as source_file:
        with open('json-out/2.json') as target_file:
            source_data = json.load(source_file)
            source_clusters = cluster_color(source, NUM_COLORS)
            source_clusters.sort(key=lambda t: colorsys.rgb_to_hsv(*t))
            target_data = json.load(target_file)
            target_clusters = cluster_color(target, NUM_COLORS)
            target_clusters.sort(key=lambda t: colorsys.rgb_to_hsv(*t))
            pairs = pair_colors(source_clusters, target_clusters)

            source_data, target_data = rescale(source_data, target_data)

            source_triangulation, source_bins = recolor_triangulation(source_data, source_clusters)
            source_triangulation, source_bins = balance_bins(source_bins, source_data, source_clusters)

            target_triangulation, target_bins = recolor_triangulation(target_data, target_clusters)
            target_triangulation, target_bins = balance_bins(target_bins, target_data, target_clusters)

            for t in source_triangulation:
                t['fill'] = rgb_tup_to_str(target_clusters[pairs[t['label']]-NUM_COLORS])

            source_triangulation.sort(key=lambda t: colorsys.rgb_to_hsv(*rgb_str_to_tup(t['fill'])))
            target_triangulation.sort(key=lambda t: colorsys.rgb_to_hsv(*rgb_str_to_tup(t['fill'])), reverse=True)

            areas = [sum(area for area, _ in b) for b in target_bins]
            goal_area = sum(areas)/len(target_bins)
            print [(a-goal_area)/a for a in areas]
            areas2 = [sum(area for area, _ in b) for b in source_bins]
            print [a-goal_area for a in areas2]
            spectrum = [{'area': a, 'fill': rgb_tup_to_str(target_clusters[i])} for i, a in enumerate(areas)]

            data = {
                    'spectrum': spectrum,
                    'source-triangles': source_triangulation,
                    'target-triangles': target_triangulation
                    }

            with open('json-out/test.json', 'w') as outfile:
                json.dump(data, outfile)


def rescale(tri1, tri2):
    area1 = sum(poly_area(*zip(*tri_to_tups(t))) for t in tri1)
    area2 = sum(poly_area(*zip(*tri_to_tups(t))) for t in tri2)
    while abs(area1-AREA) > 10*EPSILON:
        for t in tri1:
            for p in ['a','b','c']:
                for x in ['x','y']:
                    t[p][x] *= 1 + 0.01 * (2*(AREA-area1 > 0)-1)
        area1 = sum(poly_area(*zip(*tri_to_tups(t))) for t in tri1)

    while abs(area2-AREA) > EPSILON:
        for t in tri2:
            for p in ['a','b','c']:
                for x in ['x','y']:
                    t[p][x] *= 1 + 0.01 * (2*(AREA-area2 > 0)-1)
        area2 = sum(poly_area(*zip(*tri_to_tups(t))) for t in tri2)

    return tri1, tri2



def balance_bins(bins, triangulation, clusters):
    while True:
        modified = False
        areas = [sum(area for area, _ in b) for b in bins]
        goal_area = sum(areas)/len(bins)
        for i, area in enumerate(areas):
            if area > goal_area and any([goal_area - a > EPSILON for a in areas]):
                smallest_area, smallest_tri = bins[i][0]
                if area - goal_area > smallest_area:
                    tri_area, tri = bins[i][0]
                    bins[i] = bins[i][1:]
                    triangulation, bins = relabel(tri_area, tri, bins, goal_area, triangulation, clusters)
                    modified = True
                    break
                else:
                    biggest_area, biggest_tri = bins[i].pop()
                    excess = area - goal_area
                    excess_tri, good_tri = split_tri(tri_to_tups(triangulation[biggest_tri]), excess)

                    a, b, c = good_tri
                    triangulation[biggest_tri]['a']['x'] = a[0]
                    triangulation[biggest_tri]['a']['y'] = a[1]
                    triangulation[biggest_tri]['b']['x'] = b[0]
                    triangulation[biggest_tri]['b']['y'] = b[1]
                    triangulation[biggest_tri]['c']['x'] = c[0]
                    triangulation[biggest_tri]['c']['y'] = c[1]

                    d, e, f = excess_tri
                    bisect.insort_right(bins[i], (poly_area(*zip(*tri_to_tups(triangulation[biggest_tri]))), biggest_tri))

                    triangulation.append({
                        'a': {'x': d[0], 'y': d[1]},
                        'b': {'x': e[0], 'y': e[1]},
                        'c': {'x': f[0], 'y': f[1]},
                        'fill': triangulation[biggest_tri]['fill'],
                        'label': triangulation[biggest_tri]['label']
                        })
                    triangulation, bins = relabel(poly_area(*zip(*tri_to_tups(triangulation[len(triangulation)-1]))), len(triangulation)-1, bins, goal_area, triangulation, clusters)
                    modified = True

                    break
        if not modified: break
    return triangulation, bins

def tri_to_tups(tri):
    return [(tri[p]['x'], tri[p]['y']) for p in ['a', 'b', 'c']]

def relabel(tri_area, tri, bins, goal_area, triangulation, clusters):
    min_dist = float('inf')
    label = None
    for i, b in enumerate(bins):
        if sum(area for area, _ in b) < goal_area - EPSILON:
            d = distance.euclidean(rgb_str_to_tup(triangulation[tri]['fill']), clusters[i])
            if d < min_dist:
                min_dist = d
                label = i

    triangulation[tri]['fill'] = rgb_tup_to_str(clusters[label])
    triangulation[tri]['label'] = label
    bisect.insort_right(bins[label], (tri_area, tri))

    return triangulation, bins

def recolor_triangulation(triangulation, clusters):
    bins = [[] for _ in range(len(clusters))]
    for i, tri in enumerate(triangulation):
        label = closest_color(rgb_str_to_tup(tri['fill']), clusters)
        triangulation[i]['fill'] = rgb_tup_to_str(clusters[label])
        triangulation[i]['label'] = label
        area = poly_area([tri[p]['x'] for p in ['a', 'b', 'c']], [tri[p]['y'] for p in ['a', 'b', 'c']])
        bisect.insort_right(bins[label], (area, i))
    return triangulation, bins

def rgb_str_to_tup(rgb):
    rgb = rgb.split(', ')[:-1]
    rgb[0] = rgb[0][5:]
    return [int(c) for c in rgb]

def rgb_tup_to_str(rgb):
    rgb = [str(int(c)) for c in rgb]
    return "rgba({}, 1)".format(', '.join(rgb))

def closest_color(color1, colors):
    min_dist = float('inf')
    best = None
    for i, color2 in enumerate(colors):
        d = distance.euclidean(color1, color2)
        if d < min_dist:
            min_dist = d
            best = i
    return best


def pair_colors(colors1, colors2):
    G = nx.Graph()
    G.add_nodes_from(range(len(colors1)))
    G.add_nodes_from([n + len(colors1) for n in range(len(colors2))])
    for i, a in enumerate(colors1):
        for j, b in enumerate(colors2):
            G.add_edge(i, len(colors1)+j, weight=1000-distance.euclidean(a,b))
    return nx.max_weight_matching(G)

def poly_area(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def split_tri(tri, area):
    a = distance.euclidean(tri[0], tri[1])
    b = distance.euclidean(tri[1], tri[2])
    c = distance.euclidean(tri[0], tri[2])
    ab = angle(a, b, c)
    ac = angle(a, c, b)
    bc = angle(b, c, a)
    theta = max(ab, ac, bc)
    if theta == ab:
        a = tri[0]
        b = tri[2]
        c = tri[1]
    elif theta == ac:
        a = tri[1]
        b = tri[2]
        c = tri[0]
    else:
        a = tri[0]
        b = tri[1]
        c = tri[2]

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    delta = float('inf')
    for alpha in range(0, 500):
        alpha /= 500.0
        new_area = poly_area([c[0], a[0], alpha*b[0] + (1-alpha)*a[0]],  [c[1], a[1], alpha*b[1] + (1-alpha)*a[1]])
        new_delta = abs(new_area - area)
        if new_delta < delta:
            delta = new_delta
        else: break

    return [(a[0], a[1]), ((1-alpha)*a[0] + alpha*b[0], alpha*b[1] + (1-alpha)*a[1]), (c[0], c[1])], [(b[0], b[1]), (alpha*b[0] + (1-alpha)*a[0], alpha*b[1] + (1-alpha)*a[1]), (c[0], c[1])]


def angle(a, b, c):
    return math.acos((c**2 - b**2 - a**2)/(-2.0 * a * b))

test()

# sort(data, key=lambda d: colorsys.rgb_to_hsv(*rgb_str_to_tup(d['fill']))[0])
