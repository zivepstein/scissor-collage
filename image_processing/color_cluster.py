import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin
from sklearn.datasets import load_sample_image
from sklearn.utils import shuffle
from time import time

def cluster_color(img,n_colors, subsample=True):
    img = np.array(img, dtype=np.float64) / 255
    w, h, d = original_shape = tuple(img.shape)
    assert d == 3
    image_array = np.reshape(img, (w * h, d))
    t0 = time()
    if subsample:
        image_array_sample = shuffle(image_array, random_state=0)[:1000]
        kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array_sample)
    else:
        kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array)
    return [255*x for x in kmeans.cluster_centers_]
