
from __future__ import absolute_import
import numpy as np
import scipy.signal
import amitgroup as ag
from amitgroup.features.features import array_bedges

# Builds a kernel along the edge direction
def _along_kernel(direction, radius):
    d = direction%4
    kern = None
    if d == 0: # S/N
        kern = np.zeros((radius*2+1,)*2, dtype=np.uint8)
        kern[radius,:] = 1
    elif d == 2: # E/W
        kern = np.zeros((radius*2+1,)*2, dtype=np.uint8)
        kern[:,radius] = 1
    elif d == 1: # SE/NW
        kern = np.eye(radius*2+1, dtype=np.uint8)[::-1]
    elif d == 3: # NE/SW
        kern = np.eye(radius*2+1, dtype=np.uint8)
            
    return kern

def bedges(images, k=6, inflate='box', radius=1, lastaxis=False):
    """
    Extracts binary edge features for each pixel according to [1].

    The function returns 8 different binary features, representing directed edges. Let us define a south-going edge as when it starts at high intensity and drops when going south (this would make south edges the lower edge of an object, if background is low intensity and the object is high intensity). By this defintion, the order of the returned edges is S, SE, E, NE, N, NW, W, SW.

    Parameters
    ----------
    images : ndarray
        Input an image of shape ``(rows, cols)`` or a list of images as an array of shape ``(N, rows, cols)``, where ``N`` is the number of images, and ``rows`` and ``cols`` the size of each image.
    k : int
        There are 6 contrast differences that are checked. The value `k` specifies how many of them must be fulfilled for an edge to be present. The default is all of them (`k` = 6) and gives more conservative edges.
    inflate : 'box', 'perpendicular', None 
        If set to `'box'` and `radius` is set to 1, then an edge will appear if any of the 8 neighboring pixels detected an edge. This is equivalent to inflating the edges area with 1 pixel. The size of the box is dictated by `radius`. 
        If `'perpendicular'`, then the features will be extended by `radius` perpendicular to the direction of the edge feature (i.e. along the edge).
    radius : int
        Controls the extent of the inflation, see above.
    lastaxis: bool
        If True, the images will be returned with the features on the last axis as ``(rows, cols, 8)`` instead of ``(8, rows, cols)``. 
    
    Returns
    -------
    edges : ndarray
        An array of shape ``(8, rows, cols)`` if entered as a single image, or ``(N, 8, rows, cols)`` of multiple. Each pixel in the original image becomes a binary vector of size 8, one bit for each cardinal and diagonal direction. 

    References
    ----------
    [1] Y. Amit : 2D Object Detection and Recognition: Models, Algorithms and Networks. Chapter 5.4.
    """
    single = len(images.shape) == 2
    if single:
        features = array_bedges(np.array([images]), k)
    else:
        features = array_bedges(images, k) 

    if inflate is True or inflate == 'box':
        features = ag.util.inflate2d(features, np.ones((1+radius*2, 1+radius*2)))
    elif inflate == 'along':
        # Propagate the feature along the edge 
        for j in xrange(8):
            kernel = _along_kernel(j, radius)
            features[:,j] = ag.util.inflate2d(features[:,j], kernel)

    if lastaxis:
        features = np.rollaxis(features, axis=1, start=features.ndim)
            
    if single:
        features = features[0]

    return features

def bedges_from_image(im, k=6, inflate='box', radius=1, lastaxis=False):
    if isinstance(im, str):
        import matplotlib.pylab as plt
        im = plt.imread(im).astype(np.float64)

    # Run bedges on each channel, and then OR it. 
    
    edges = [bedges(im[...,i], k, inflate, radius, lastaxis) for i in xrange(3)]
    print edges[0].shape
    return edges[0] | edges[1] | edges[2]
