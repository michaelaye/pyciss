import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from ipywidgets import fixed, interact

interpolators = ['none', 'nearest', 'bilinear', 'bicubic',
                 'spline16', 'spline36', 'hanning', 'hamming',
                 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian',
                 'bessel', 'mitchell', 'sinc', 'lanczos']


def lookup_rcparam(rcParams, pattern):
    """Look up a pattern in the matplotlib rcParams dict.

    Just a little helper to get to the right MPL settings faster.
    """
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


def add_ticks_to_x(ax, newticks, newnames):
    """Add new ticks to an axis.

    I use this for the right-hand plotting of resonance names in my plots.
    """
    ticks = list(ax.get_xticks())
    ticks.extend(newticks)
    ax.set_xticks(ticks)

    names = list(ax.get_xticklabels())
    names.extend(newnames)
    ax.set_xticklabels(names)


def soliton_plot(cube, solitons, ax=None, solitoncolor='red', resonances=None,
                 draw_prediction=True, set_boundaries=False):
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 9), nrows=2)
    else:
        fig = ax.get_figure()

    # set resonances to True to get all (warning: in A ring too many to be useful)
    if resonances is None:
        # setting some reasonable defaults here:
        resonances = ['janus', 'prometheus', 'epimetheus']

    cube.imshow(show_resonances=resonances, ax=ax[0], fig=fig,
                set_extent=True, plow=35)

    ticks = []
    names = []
    if draw_prediction:
        for k, v in solitons.items():
            ax[0].axhline(y=v/1000, alpha=1, color=solitoncolor, linestyle='dashdot',
                          lw=4, xmin=0.25, xmax=0.5)
            ticks.append(v)
            names.append(k)

    if set_boundaries:
        # i'm only considering the first set of vaules here:
        xlow = (solitons['janus65'] - 20) / 1000
        xhigh = xlow + 0.2

    ax[0].set_ybound(xlow, xhigh)

    ax2 = ax[0].twinx()
    ax2.set_ybound(cube.minrad, cube.maxrad)
    ax2.ticklabel_format(useOffset=False)
    ax2.set_yticks(np.array(ticks)/1000)
    ax2.set_yticklabels(names)

    ax[1].plot(np.linspace(*cube.extent[2:], cube.img.shape[0]),
               np.nanmedian(cube.img, axis=1),
    #            cube.img[:, 700],
               color='white', lw=1)
    # ax[1].grid()
    ax[1].set_axis_bgcolor('black')
    ticks = []
    names = []
    # if solitons is not None:
    #     for k, v in solitons.items():
    #         ax[1].axvline(x=v/1000, alpha=1, color=solitoncolor, linestyle='dashdot',
    #                 lw=4)
    #         ticks.append(v)
    #         names.append(k)
    ax[1].set_title('Longitude-median profile over radius')
    ax[1].set_xlabel('Radius [Mm]')
    ax[1].set_ylabel('I/F')
    ax[1].set_xlim(xlow, xhigh)
    ax3 = ax[1].twiny()
    ax3.ticklabel_format(useOffset=False)
    ax3.set_xticks(np.array(ticks)/1000)
    ax3.set_xticklabels(names)
    # add_ticks_to_x(ax[1], ticks, names)
    fig.tight_layout()
    fig.savefig("{}_janus65.png".format(cube.pm.img_id), dpi=100)
