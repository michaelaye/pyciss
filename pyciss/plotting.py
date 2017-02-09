from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from ipywidgets import fixed, interact

from ._utils import which_epi_janus_resonance
from .meta import get_all_resonances
from .ringcube import RingCube

resonance_table = get_all_resonances()

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
    delta = round((p30 - min_) / 50, 5)
    interact(myimshow, img=fixed(img), vmin=(min_, p30, delta),
             vmax=(p70, max_, delta), i=(0, len(interpolators) - 1))


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


def get_res_radius_from_res_name(res_name, cube):
    moon, resonance = res_name.split()
    moon = which_epi_janus_resonance(moon, cube.imagetime)
    row = resonance_table.query('moon==@moon and reson==@resonance')
    return row.squeeze()['radius'] * u.km


def soliton_plot(cube, solitons, ax=None, solitoncolor='red', resonances=None,
                 draw_prediction=True, soliton_controls_radius=False,
                 saveroot=None, ifmin=None, ifmax=None, rmin=None, rmax=None):
    if ax is None:
        # fig, ax = plt.subplots(figsize=(12, 9), nrows=2)
        fig, ax = plt.subplots(nrows=2)
    else:
        fig = ax.get_figure()

    # set resonances to True to get all (warning: in A ring too many to be useful)
    if resonances is None:
        # setting some reasonable defaults here:
        resonances = ['janus', 'prometheus', 'epimetheus']

    cube.imshow(show_resonances=resonances, ax=ax[0], fig=fig,
                set_extent=True)

    ticks = []
    names = []
    if draw_prediction:
        for k, v in solitons.items():
            ax[0].axhline(y=v.to('Mm').value, alpha=1, color=solitoncolor,
                          linestyle='dashdot', lw=3, xmin=0.0, xmax=0.25)
            # the following is only really required if i want to show more
            # than one prediction line
            # ticks.append(v.to('Mm').value)
            # names.append(k)

    # soliton name and value, only using first found soliton
    # TODO: create function that deals with more than one soliton
    res_name, soliton_radius = next(iter(solitons.items()))
    res_radius = get_res_radius_from_res_name(res_name, cube)
    ax[0].axhline(y=res_radius.to('Mm').value, alpha=0.5,
                  color='cyan', linestyle='dotted', lw=3,
                  xmin=0.75, xmax=1.0)

    soliton_ax = None
    # soliton_ax = ax[0].twinx()
    # soliton_ax.ticklabel_format(useOffset=False)
    # soliton_ax.set_yticks(np.array(ticks))
    # soliton_ax.set_yticklabels(names)
    # soliton_ax.axhline(y=res_radius.to('Mm').value, alpha=0.5,
    #                    color='cyan', linestyle='dotted', lw=3,
    #                    xmin=0.7, xmax=1.0)

    if soliton_controls_radius:
        radius_low = (res_radius - 20 * u.km).to(u.Mm)
        radius_high = radius_low + 200 * u.km
        for tempax in [ax[0], cube.resonance_axis]:
            tempax.set_ybound(radius_low.value, radius_high.value)
        if soliton_ax:
            soliton_ax.set_ybound(radius_low.value, radius_high.value)
    elif any([rmin is not None, rmax is not None]):
        for tempax in [ax[0], cube.resonance_axis]:
            tempax.set_ybound(rmin, rmax)
    else:
        # the min/max image radii otherwise control the plot in cube.imshow()
        # so set the soliton display axis to the same values
        soliton_ax.set_ybound(cube.minrad.value, cube.maxrad.value)

    ax[1].plot(np.linspace(*cube.extent[2:], cube.img.shape[0]),
               np.nanmedian(cube.img, axis=1),
               color='white', lw=1)
    if any([ifmin is not None, ifmax is not None]):
        ax[1].set_ylim(ifmin, ifmax)

    ticks = []
    names = []
    if draw_prediction:
        for k, v in solitons.items():
            ax[1].axvline(x=v.to('Mm').value, alpha=1, color=solitoncolor, linestyle='dashdot',
                          lw=4)
            ticks.append(v.to('Mm').value)
            names.append(k)

    ax[1].axvline(x=res_radius.to('Mm').value, alpha=0.5, color='cyan',
                  linestyle='dotted', lw=3)
    ax[1].set_axis_bgcolor('black')
    ax[1].set_title('Longitude-median profile over radius')
    ax[1].set_xlabel('Radius [Mm]')
    ax[1].set_ylabel('I/F')

    if soliton_controls_radius:
        ax[1].set_xlim(radius_low.value, radius_high.value)
    elif any([rmin is not None, rmax is not None]):
        ax[1].set_xlim(rmin, rmax)
    else:
        ax[1].set_xlim(cube.minrad.value, cube.maxrad.value)

    fig.tight_layout()
    savepath = "{}_{}.png".format(cube.pm.img_id, '_'.join(res_name.split()))
    if saveroot is not None:
        root = Path(saveroot)
        root.mkdir(exist_ok=True)
        savepath = root / savepath
    fig.savefig(str(savepath), dpi=100)


def resonance_plot(img_id, ax=None,
                   saveroot=None, ifmin=None, ifmax=None, rmin=None, rmax=None):
    cube = RingCube(img_id)
    if ax is None:
        # fig, ax = plt.subplots(figsize=(12, 9), nrows=2)
        fig, ax = plt.subplots(nrows=2)
    else:
        fig = ax.get_figure()

    cube.imshow(show_resonances=['janus'], ax=ax[0], fig=fig,
                set_extent=True)

    # soliton name and value, only using first found soliton
    # TODO: create function that deals with more than one soliton
    row_filter = cube.inside_resonances.moon == cube.janus_swap_phase
    cols = ['radius', 'reson']
    res_radius, res_name = cube.inside_resonances.loc[row_filter, cols].squeeze()
    res_radius *= u.km
    ax[0].axhline(y=res_radius.to('Mm').value, alpha=0.5,
                  color='cyan', linestyle='dotted', lw=3,
                  xmin=0.75, xmax=1.0)

    if any([rmin is not None, rmax is not None]):
        radius_low = rmin
        radius_high = rmax
    else:
        radius_low = (res_radius - 20 * u.km).to(u.Mm)
        radius_high = radius_low + 200 * u.km
    for tempax in [ax[0], cube.resonance_axis]:
        tempax.set_ybound(radius_low.value, radius_high.value)

    ifs = np.nanmedian(cube.img, axis=1)
    ifs = np.nan_to_num(ifs)
    ifs[ifs < 0] = 0
    ax[1].plot(np.linspace(*cube.extent[2:], cube.img.shape[0]),
               ifs, color='white', lw=1)
    if any([ifmin is not None, ifmax is not None]):
        iflow = ifmin
        ifhigh = ifmax
    else:
        iflow, ifhigh = np.percentile(ifs[~np.isnan(ifs)], (0.5, 99.5))
    ax[1].set_ylim(iflow / 1.1, ifhigh * 1.1)

    ax[1].axvline(x=res_radius.to('Mm').value, alpha=0.5, color='cyan',
                  linestyle='dotted', lw=3)
    ax[1].set_axis_bgcolor('black')
    ax[1].set_title('Longitude-median profile over radius')
    ax[1].set_xlabel('Radius [Mm]')
    ax[1].set_ylabel('I/F')

    ax[1].set_xlim(radius_low.value, radius_high.value)

    fig.tight_layout()
    if saveroot is not None:
        savepath = "{}_{}.png".format(cube.pm.img_id, '_'.join(res_name.split()))
        root = Path(saveroot)
        root.mkdir(exist_ok=True)
        savepath = root / savepath
        fig.savefig(str(savepath), dpi=100)
    return fig
