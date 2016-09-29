import matplotlib.pyplot as plt
# from skimage.exposure import equalize_hist
from ipywidgets import interact, fixed
import numpy as np


interpolators = ['none', 'nearest', 'bilinear', 'bicubic',
                 'spline16', 'spline36', 'hanning', 'hamming',
                 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian',
                 'bessel', 'mitchell', 'sinc', 'lanczos']


def lookup_rcparam(rcParams, pattern):
    return [i for i in rcParams.keys() if pattern in i]


def myimshow(img, vmin, vmax, i, cmap='gray'):
    _, ax = plt.subplots(nrows=2, figsize=(10, 10))
    ax, ax2 = ax
    ax.imshow(img, vmin=vmin, vmax=vmax, aspect='auto',
              interpolation=interpolators[i],
              cmap=cmap)
    ax.set_title('vmin: {:.2f}, vmax: {:.2f}, interpolator:{}'
                 .format(vmin, vmax, interpolators[i]))
    tohist = img[~np.isnan(img)]
    p1, p99 = np.percentile(tohist, (0.5, 99.5))
    ax2.hist(img[~np.isnan(img)], 100, range=(p1, p99))
    plt.show()


def myinteract(img):
    min_ = round(np.nanmin(img), 4)
    max_ = round(np.nanmax(img), 4)
    p30, p70 = np.percentile(img[~np.isnan(img)], (30, 70))
    delta = round((p30-min_)/50, 5)
    interact(myimshow, img=fixed(img), vmin=(min_, p30, delta),
             vmax=(p70, max_, delta), i=(0, len(interpolators)-1))


def imshowlowhigh(data, low=10, high=90):
    fig, ax = plt.subplots()
    plow, phigh = np.percentile(data[~np.isnan(data)], (low, high))
    ax.imshow(data, vmin=plow, vmax=phigh, cmap='gray', interpolation='sinc')
    return fig
