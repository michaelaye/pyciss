
# coding: utf-8

# In[ ]:

from pathlib import Path
import warnings
from pyciss import io, pipeline
import seaborn as sns
from sklearn.preprocessing import scale
sns.set_style('white')
sns.set_context('notebook')
get_ipython().magic('matplotlib nbagg')


# In[ ]:

savedir = io.dbpath.parent / 'std_overlays'
savedir.mkdir(exist_ok=True)


# In[ ]:

savedir


# In[ ]:

get_ipython().magic('matplotlib nbagg')
sns.set_style('white')


# In[ ]:

def mad(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    med = np.nanmedian(arr, axis=1)
    return np.nanmedian(np.abs(arr - med[:, np.newaxis]), axis=1)


# In[ ]:

cubes = io.db_mapped_cubes()


# In[ ]:

cube = io.RingCube(next(cubes))


# In[ ]:

def process_cube(fpath):
    cube = io.RingCube(fpath)
    img = cube.data[0]
    low, high = np.percentile(img[img>0], (2,98))
    img[img<0] = np.nan
    sub = pipeline.remove_mean_value(img)
    sublow, subhigh = np.percentile(sub[~np.isnan(sub)], (2,98))
    fig, ax = plt.subplots(ncols=2, figsize=(10, 6), sharey=False)
#     ax = ax.ravel()
#     ax=[ax]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        stats = mad(img)
    notnan_ind = ~np.isnan(stats)
    # scale the stats so that I can shift it easily to middle of image
    X = scale(stats[notnan_ind], with_mean=True, with_std=False)
    # shift image to middle of azimuth extent (the first 2 items of cube.extent)
    X = X*5 + np.mean(cube.extent[:2])
    # create Y array out of the radial extent
    Y = np.linspace(cube.extent[2],
                    cube.extent[3],
                    cube.img.shape[0])
    # filter for not-NANs
    Y = Y[notnan_ind]
    scattersize = 5
    for i, axis in enumerate(ax):
        cube.imshow(ax=axis, set_extent=True)
        if i == 1:
            scattersize = 25
        axis.scatter(X, Y, s=scattersize, color='red')
        axis.set_xlim(cube.extent[0], cube.extent[1])
        axis.set_ylim(cube.extent[2], cube.extent[3])
        axis.set_title('')
        if i==1:
            axis.set_ylabel('')
#     ax[2].plot(np.nanstd(img, axis=1))
    fig.subplots_adjust(bottom=0.15)
    fig.suptitle(fpath.name.split('.')[0],fontsize=14)
    fig.savefig(str(savedir / (fpath.name[:-4]+'.png')), dpi=150)
#     plt.close(fig)


# In[ ]:

process_cube(Path(cube.filename))


# In[ ]:

from pyciss.meta import meta1500m


# In[ ]:

meta1500m.columns


# In[ ]:

meta1500m[meta1500m.id=='N1591682340'].lit_status


# In[ ]:

io.PathManager(cube.filename).cubepath.exists()


# In[ ]:

from pathlib import Path


# In[ ]:

p = next(io.db_label_paths())


# In[ ]:

cubepath = io.PathManager('N1503229567').cubepath

process_cube(cubepath)


# In[ ]:

cubepath = io.PathManager('N1467346565').cubepath
process_cube(cubepath)


# In[ ]:

cube = io.RingCube(cubepath)


# In[ ]:

plt.figure(figsize=(12,10))
plt.imshow(np.log(np.abs(np.fft.fftshift(np.fft.fft2(img)))))


# In[ ]:

img = cube.data[0]


# In[ ]:

img[img<0]=0


# In[ ]:

plt.figure(figsize=(12,10))
plt.imshow(img, vmax=0.1, cmap='gray')
plt.colorbar()


# In[ ]:

subimg = img[750:1200, 200:1350]


# In[ ]:

plt.imshow(subimg, vmax=0.1, cmap='gray')


# In[ ]:

plt.figure(figsize=(12,10))
plt.imshow(np.log(np.abs(np.fft.fftshift(np.fft.fft2(subimg)))))


# In[ ]:

from skimage.feature import hog
from skimage import exposure


# In[ ]:

fd, hog_image = hog(subimg, orientations=8, pixels_per_cell=(16, 16),
                    cells_per_block=(1, 1), visualise=True)


# In[ ]:

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)

ax1.axis('off')
ax1.imshow(subimg, cmap=plt.cm.gray)
ax1.set_title('Input image')
ax1.set_adjustable('box-forced')

# Rescale histogram for better display
hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 0.02))

ax2.axis('off')
ax2.imshow(hog_image_rescaled, cmap=plt.cm.gray)
ax2.set_title('Histogram of Oriented Gradients')
ax1.set_adjustable('box-forced')
plt.show()


# In[ ]:

cubepath = io.PathManager('N1467346447').cubepath

process_cube(cubepath)


# In[ ]:

cube = io.RingCube(cubepath)


# In[ ]:

cube.imshow(set_extent=False)


# In[ ]:

cubepath = io.PathManager('/Volumes/Data/ciss/std_overlays/N1467345562_3.cal.dst.map.png').cubepath

process_cube(cubepath)


# In[ ]:

cubepath = io.PathManager('/Volumes/Data/ciss/std_overlays/N1467345680_2.cal.dst.map.png').cubepath

process_cube(cubepath)


# In[ ]:

cube = io.RingCube(cubepath)


# In[ ]:

cube.imshow(set_extent=False)


# In[ ]:

subimg = cube.img[1380:1465, 500:1800]


# In[ ]:

cube.imshow(data=subimg)


# In[ ]:

plt.figure(figsize=(12,10))
plt.imshow(np.log(np.abs(np.fft.fftshift(np.fft.fft2(subimg)))))


# In[ ]:

plt.figure()
min_ind = 681
max_var_ind = 694
out_ind = 1747
plt.plot(img[min_ind], label='minimum')
plt.plot(img[max_var_ind], label='max_var')
plt.plot(img[out_ind], label='out')
plt.legend(loc=1)


# In[ ]:

import wavelets
from wavelets import WaveletAnalysis


# In[ ]:

x1 = img[max_var_ind]
x1 = x1[~np.isnan(x1)]
x2 = img[min_ind]
x2 = x2[~np.isnan(x2)]


# In[ ]:

cube.resolution_val


# In[ ]:

# dt = 0.35

def do_wavelet(x):
    dt = 1
    wa = WaveletAnalysis(x, dt=dt)
    power = wa.wavelet_power
    scales = wa.scales
    t = wa.time
    T, S = np.meshgrid(t, scales)
    return T, S, power, t

def plot_wavelet(x1, x2):
    T, S, power, t = do_wavelet(x1)
    print(power.max())
    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(4.5,6))
    im = ax[0].contourf(T, S, power*1000, 100, cmap='viridis', vmax=1.5)
    plt.colorbar(im, ax=ax[0])
    T, S, power, t = do_wavelet(x2)
    print(power.max())
    im2 = ax[1].contourf(T, S, power*1000, 100, cmap='viridis', vmax=1.5)
    plt.colorbar(im2, ax=ax[1])
    for axis in ax:
        axis.set_yscale('log')
        axis.set_ylabel("Arbitrary power in 1/distance")
    ax[0].set_title("Maximum dispersion row")
    ax[1].set_title("Minimum dispersion row")
    ax[1].set_xlabel("Along Azimuth [pixel]")
    


# In[ ]:

plot_wavelet(x1, x2)


# # Sinusoidal fits

# In[ ]:

img = cube.img


# In[ ]:

img.shape


# In[ ]:

import numpy as np
from scipy.optimize import curve_fit

# create the function we want to fit
def my_sin(x, freq, amplitude, phase, offset):
    return np.sin(x * freq + phase) * amplitude + offset

def fit_row(data, guess_freq):
    guess_amplitude = 2*np.std(data)
    guess_phase = 0
    guess_offset = np.mean(data)

    p0=[guess_freq, guess_amplitude,
        guess_phase, guess_offset]

    t = np.arange(len(data))
    # now do the fit
    fit = curve_fit(my_sin, t, data, p0=p0)

    # we'll use this to plot our first estimate. This might already be good enough for you
    data_first_guess = my_sin(t, *p0)

    # recreate the fitted curve using the optimized parameters
    data_fit = my_sin(t, *fit[0])

    plt.figure()
    plt.plot(data, '.')
    plt.plot(data_fit, label='after fitting')
    plt.plot(data_first_guess, label='first guess')
    plt.legend()
    plt.show()


# In[ ]:

row = img[1000:1001]
data = row[~np.isnan(row)][:-3]
plt.figure()
plt.plot(data)


# In[ ]:

fit_row(data, 0.05)


# In[ ]:



