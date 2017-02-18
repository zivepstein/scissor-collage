
# coding: utf-8

# In[113]:

from PIL import Image
from sklearn.preprocessing import normalize
import numpy as np


# In[114]:

black = Image.open('data/black.png')
blue = Image.open('data/blue.png')
brown = Image.open('data/brown.png')
grey = Image.open('data/grey.png')
green = Image.open('data/green.png')
pink = Image.open('data/pink.png')
purple = Image.open('data/purple.png')
teal = Image.open('data/teal.png')
white = Image.open('data/white.png')
yellow = Image.open('data/yellow.png')
raw_spectrum = [black,blue,brown,grey,green,pink,purple,teal,white,yellow]
raw_spectrum_map = ["black","blue","brown","grey","green","pink","purple","teal","white","yellow"]


# In[115]:

def norm(x):
    return x / np.linalg.norm(x)
def dist(x,y):
    return  sum([abs(a-b) for (a,b) in zip(norm(x.histogram()),norm(y.histogram()))])


# In[116]:

im = Image.open('data/dima.jpg')
def find_closest_color(im):
    min_distance = float("inf")
    ind = 0
    for (i,c) in enumerate(raw_spectrum):
        d = dist(im,c)
        if d < min_distance:
            ind = i
            min_distance = d 
    return raw_spectrum_map[ind]


# In[117]:

find_closest_color(im)


# In[ ]:



