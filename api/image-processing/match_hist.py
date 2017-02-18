
# coding: utf-8

# In[1]:

from matplotlib import pyplot as plt
from scipy.misc import lena, ascent
import numpy as np
from PIL import Image
from scipy.misc import imread

def hist_match(source, template):
    """
    Adjust the pixel values of a grayscale image such that its histogram
    matches that of a target image

    Arguments:
    -----------
        source: np.ndarray
            Image to transform; the histogram is computed over the flattened
            array
        template: np.ndarray
            Template image; can have different dimensions to source
    Returns:
    -----------
        matched: np.ndarray
            The transformed output image
    """

    oldshape = source.shape
    source = source.ravel()
    template = template.ravel()

    # get the set of unique pixel values and their corresponding indices and
    # counts
    s_values, bin_idx, s_counts = np.unique(source, return_inverse=True,
                                            return_counts=True)
    t_values, t_counts = np.unique(template, return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    return interp_t_values[bin_idx].reshape(oldshape)
source = lena()
template = ascent()
matched = hist_match(source, template)



# In[2]:

source  = imread("data/source.jpg")
target  = imread("data/target.jpg")


# In[3]:

def flat_color_from_ind(im,ind):
    x = np.zeros((im.shape[0], im.shape[1]))
    for (i,val1) in enumerate(im):
        for (j,val2) in enumerate(val1):
            x[i][j] = val2[ind]
    return x

rs = flat_color_from_ind(source,0)
gs = flat_color_from_ind(source,1)
bs = flat_color_from_ind(source,2)
rt = flat_color_from_ind(target,0)
gt = flat_color_from_ind(target,1)
bt = flat_color_from_ind(target,2)

rm = hist_match(rs, rt)
gm = hist_match(gs, gt)
bm = hist_match(bs, bt)


# In[30]:

matched_target  = np.zeros((source.shape[0], source.shape[1],3))
for i in range(0,matched_target.shape[0]):
    for j in range(0,matched_target.shape[1]):
        matched_target[i][j] = [int(rm[i][j]),int(bm[i][j]),int(gm[i][j])]


# In[31]:

img = Image.fromarray(matched_target)
img.show()


# In[41]:

img = Image.fromarray(matched_target.astype('uint8'),'RGB')
img.show()


# In[42]:

img = Image.fromarray(target,'RGB')
img.show()


# In[25]:

matched_target


# In[ ]:



