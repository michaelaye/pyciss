"""RingCube class definition"""
import os

import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from skimage import exposure
from pathlib import Path

from pysis import CubeFile

from ._utils import which_epi_janus_resonance
from .io import PathManager
from .meta import get_all_resonances, get_meta_df
from .opusapi import MetaData

try:
    # prettier plots with seaborn
    import seaborn as sns
    _SEABORN_INSTALLED = True
except ImportError:
    _SEABORN_INSTALLED = False
else:
    sns.set_context('notebook')
    sns.set_style('white')

resonances = get_all_resonances()
meta_df = get_meta_df()


def calc_4_3(width):
    """Calculate 4:3 ratio for figures.

    so that they import nicely in prezzies.

    Parameters
    ----------
    width : int, float
        Width of plotting window
    """
    return (width, 3 * width / 4)


class RingCube(CubeFile):

    def __init__(self, fname, **kwargs):
        p = Path(fname)
        self.pm = PathManager(fname)
        if not p.is_absolute():
            # assuming it's an image_id and user wants default action:
            fname = str(self.pm.cubepath)
        # if fname is absolute path, open exactly that one:
        super().__init__(str(fname), **kwargs)
        try:
            self.meta = meta_df.loc[self.pm.img_id]
        except KeyError:
            self.meta = None

    def get_opus_meta_data(self):
        print("Getting metadata from the online OPUS database.")
        self.opusmeta = MetaData(self.pm._id)
        print("Done.")
        return self.opusmeta

    @property
    def meta_pixres(self):
        if self.meta is not None:
            return int(self.meta.pixres * 1000)
        else:
            return np.nan

    @property
    def meta_litstatus(self):
        if self.meta is not None:
            return self.meta.lit_status.upper()
        else:
            return np.nan

    @property
    def mapping_label(self):
        return self.label['IsisCube']['Mapping']

    @property
    def minrad(self):
        "float: MinimumRingRadius in Mm."
        return self.mapping_label['MinimumRingRadius'] / 1e6 * u.Mm

    @property
    def minrad_km(self):
        return self.minrad.to(u.km)

    @property
    def maxrad(self):
        "float: MaxiumRingRadius in Mm."
        return self.mapping_label['MaximumRingRadius'] / 1e6 * u.Mm

    @property
    def maxrad_km(self):
        return self.maxrad.to(u.km)

    @property
    def minlon(self):
        return self.mapping_label['MinimumRingLongitude'] * u.degree

    @property
    def maxlon(self):
        return self.mapping_label['MaximumRingLongitude'] * u.degree

    @property
    def img(self):
        "apply_numpy_special is inherited from CubeFile."
        return self.apply_numpy_specials()[0]

    @property
    def extent(self):
        return [i.value for i in [self.minlon, self.maxlon, self.minrad, self.maxrad]]

    @property
    def resolution_val(self):
        return self.mapping_label['PixelResolution'].value * u.m / u.pixel

    @property
    def plottitle(self):
        return os.path.basename(self.filename).split('.')[0]

    @property
    def plotfname(self):
        return self.filename.split('.')[0] + '.png'

    def imshow(self, data=None, plow=1, phigh=99, save=False, ax=None, fig=None,
               interpolation='sinc', extra_title=None, show_resonances='some',
               set_extent=True, equalized=False, rmin=None, rmax=None, **kwargs):
        """Powerful default display.

        show_resonances can be True, a list, 'all', or 'some'
        """
        if data is None:
            data = self.img
        if equalized:
            data = exposure.equalize_hist(np.nan_to_num(data))
        extent_val = self.extent if set_extent else None
        min_, max_ = np.percentile(data[~np.isnan(data)], (plow, phigh))
        self.min_ = min_
        self.max_ = max_
        if ax is None:
            if not _SEABORN_INSTALLED:
                fig, ax = plt.subplots(figsize=calc_4_3(8))
            else:
                fig, ax = plt.subplots()
        im = ax.imshow(data, extent=extent_val, cmap='gray', vmin=min_,
                       vmax=max_, interpolation=interpolation, origin='lower',
                       aspect='auto', **kwargs)
        if any([rmin is not None, rmax is not None]):
            ax.set_ylim(rmin, rmax)
        self.mpl_im = im
        ax.set_xlabel('Longitude [deg]')
        ax.set_ylabel('Radius [Mm]')
        ax.ticklabel_format(useOffset=False)
        # ax.grid('on')
        title = ("{}, Metadata_Res: {} m/pix, {}, {}".format(
                 self.plottitle,
                 self.meta_pixres,
                 self.imagetime.date().isoformat(),
                 self.meta_litstatus))
        if extra_title:
            title += ', ' + extra_title
        ax.set_title(title, fontsize=14)
        if show_resonances:
            self.set_resonance_axis(ax, show_resonances, rmin, rmax)
        fig.tight_layout()
        if save:
            savename = self.plotfname
            if extra_title:
                savename = savename[:-4] + '_' + extra_title + '.png'
            fig.savefig(savename, dpi=150)

    @property
    def inside_resonances(self):
        lower_filter = (resonances['radius'] > (self.minrad_km))
        higher_filter = (resonances['radius'] < (self.maxrad_km))
        return resonances[lower_filter & higher_filter]

    @property
    def janus_swap_phase(self):
        return which_epi_janus_resonance('janus', self.imagetime)

    def set_resonance_axis(self, ax, show_resonances, rmin=None, rmax=None):
        if show_resonances == 'some':
            show_resonances = ['janus', 'prometheus', 'epimetheus']
        # check for janus/epimetheus year and copy over items
        # into final moons list
        moons = []
        for moon in show_resonances:
            if moon in ['janus', 'epimetheus']:
                moons.append(which_epi_janus_resonance(moon,
                                                       self.imagetime))
            else:
                moons.append(moon)
        try:
            moonfilter = (self.inside_resonances.moon.isin(moons))
        except TypeError:
            # if show_resonances not a list, do nothing, == 'all'
            moonfilter = True
        newticks = self.inside_resonances[moonfilter]
        ax2 = ax.twinx()
        ax2.set_ybound(self.minrad.value, self.maxrad.value)
        ax2.ticklabel_format(useOffset=False)
        # i plot in Mm, hence the division by 1000 here.
        ax2.set_yticks(newticks.radius / 1000)
        ax2.set_yticklabels(newticks.name)
        if any([rmin is not None, rmax is not None]):
            ax2.set_ylim(rmin, rmax)
        self.resonance_axis = ax2

    @property
    def mean_profile(self):
        return np.nanmean(self.img, axis=1)

    @property
    def density_wave_subtracted(self):
        subtracted = self.img - self.mean_profile[:, np.newaxis]
        return subtracted

    def imshow_subtracted(self, **kwargs):
        self.imshow(data=self.density_wave_subtracted, **kwargs)

    @property
    def imgmin(self):
        return np.nanmin(self.img)

    @property
    def imgmax(self):
        return np.nanmax(self.img)

    @property
    def imgminmax(self):
        return self.imgmin, self.imgmax

    @property
    def inner_zoom(self, data=None):
        if data is None:
            data = self.img
        shape = self.img.shape
        x1 = shape[0] // 4
        x2 = 3 * shape[0] // 4
        y1 = shape[1] // 4
        y2 = 3 * shape[1] // 4
        return data[x1:x2, y1:y2]

    @property
    def imagetime(self):
        return self.label['IsisCube']['Instrument']['ImageTime']
