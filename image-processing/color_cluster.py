
# coding: utf-8

# In[1]:

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin
from sklearn.datasets import load_sample_image
from sklearn.utils import shuffle
from time import time


# In[23]:

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
    return kmeans.cluster_centers_


# In[ ]:

def eqsc(X, K=None, G=None):
    "equal-size clustering based on data exchanges between pairs of clusters"
    from scipy.spatial.distance import pdist, squareform
    from matplotlib import pyplot as plt
    from matplotlib import animation as ani    
    from matplotlib.patches import Polygon   
    from matplotlib.collections import PatchCollection
    def error(K, m, D):
        """return average distances between data in one cluster, averaged over all clusters"""
        E = 0
        for k in range(K):
            i = np.where(m == k)[0] # indeces of datapoints belonging to class k
            E += np.mean(D[np.meshgrid(i,i)])
        return E / K
    np.random.seed(0) # repeatability
    N, n = X.shape
    if G is None and K is not None:
        G = N // K # group size
    elif K is None and G is not None:
        K = N // G # number of clusters
    else:
        raise Exception('must specify either K or G')
    D = squareform(pdist(X)) # distance matrix
    m = np.random.permutation(N) % K # initial membership
    E = error(K, m, D)
    # visualization
    #FFMpegWriter = ani.writers['ffmpeg']
    #writer = FFMpegWriter(fps=15)
    #fig = plt.figure()
    #with writer.saving(fig, "ec.mp4", 100):
    t = 1
    while True:
        E_p = E
        for a in range(N): # systematically
            for b in range(a):
                m[a], m[b] = m[b], m[a] # exchange membership
                E_t = error(K, m, D)
                if E_t < E:
                    E = E_t
                    print("{}: {}<->{} E={}".format(t, a, b, E))
                    #plt.clf()
                    #for i in range(N):
                        #plt.text(X[i,0], X[i,1], m[i])
                    #writer.grab_frame()
                else:
                    m[a], m[b] = m[b], m[a] # put them back
        if E_p == E:
            break
        t += 1           
    fig, ax = plt.subplots()
    patches = []
    for k in range(K):
        i = np.where(m == k)[0] # indeces of datapoints belonging to class k
        x = X[i]        
        patches.append(Polygon(x[:,:2], True)) # how to draw this clock-wise?
        u = np.mean(x, 0)
        plt.text(u[0], u[1], k)
    p = PatchCollection(patches, alpha=0.5)        
    ax.add_collection(p)
    plt.show()

if __name__ == "__main__":
    N, n = 100, 2    
    X = np.random.rand(N, n)
    eqsc(X, G=3)


# In[ ]:

eqsc(X, G=3)


# In[ ]:



