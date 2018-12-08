"""RingCube class definition"""
import logging
import os
import warnings
from pathlib import Path

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from astropy import units as u
from skimage import exposure

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

logger = logging.getLogger(__name__)

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

    def __init__(self, fname, plot_limits=(0.1, 99), destriped=True, **kwargs):
        p = Path(fname)
        self.pm = PathManager(fname)
        if not p.is_absolute():
            # assuming it's an image_id and user wants default action:
            if self.pm.cubepath.exists() and destriped is True:
                fname = str(self.pm.cubepath)
            else:
                fname = str(self.pm.undestriped)
        # if fname is absolute path, open exactly that one:
        super().__init__(str(fname), **kwargs)
        try:
            q = f"file_id == '{self.pm.img_id}'"
            self.meta = meta_df.query(q)
        except KeyError:
            self.meta = None
        self.resonance_axis = None
        self.pmin, self.pmax = plot_limits
        self._plotted_data = None

    def get_opus_meta_data(self):
        print("Getting metadata from the online OPUS database.")
        self.opusmeta = MetaData(self.pm._id)
        print("Done.")
        return self.opusmeta

    @property
    def plotted_data(self):
        return self.img if self._plotted_data is None else self._plotted_data

    @plotted_data.setter
    def plotted_data(self, value):
        self._plotted_data = value

    @property
    def meta_pixres(self):
        if self.meta is not None:
            return int(self.meta.mean_radial_res * 1000) * u.m / u.pix
        else:
            return np.nan

    @property
    def meta_litstatus(self):
        if self.meta is not None:
            emang = self.meta.filter(regex='RING_EMISSION_ANGLE').mean(axis=1)
            return "LIT" if emang.iat[0] < 90.0 else "UNLIT"
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
    def midrad(self):
        return (self.minrad + self.maxrad) / 2

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
    def image_id(self):
        return Path(self.filename).stem.split('.')[0]

    @property
    def plotfname(self):
        return self.filename.split('.')[0] + '.png'

    def calc_clim(self, data):
        from numpy import inf
        if np.nanmin(data) == -inf:
            data[data == -inf] = np.nan
            data[data == inf] = np.nan
        return np.percentile(data[~np.isnan(data)], (self.pmin, self.pmax))

    @property
    def plot_limits(self):
        return self.calc_clim(self.plotted_data)

    def to_xarray(self):
        radii = np.linspace(self.minrad, self.maxrad, self.img.shape[0])
        azimuths = np.linspace(self.minlon, self.maxlon, self.img.shape[1])
        data = xr.DataArray(
            self.img,
            coords={'radius': radii, 'azimuth': azimuths},
            dims=('radius', 'azimuth'))
        vmin, vmax = self.plot_limits
        return data.where( (data > vmin) & (data < vmax) )

    def imshow(self, data=None, save=False, ax=None,
               interpolation='none', extra_title=None, show_resonances='some',
               set_extent=True, equalized=False, rmin=None, rmax=None,
               savepath='.', **kwargs):
        """Powerful default display.

        show_resonances can be True, a list, 'all', or 'some'
        """
        if data is None:
            data = self.img
        self.plotted_data = data
        if self.resonance_axis is not None:
            logger.debug('removing resonance_axis')
            self.resonance_axis.remove()
        if equalized:
            data = exposure.equalize_hist(np.nan_to_num(data))
        extent_val = self.extent if set_extent else None
        min_, max_ = self.plot_limits
        self.min_ = min_
        self.max_ = max_
        if ax is None:
            if not _SEABORN_INSTALLED:
                fig, ax = plt.subplots(figsize=calc_4_3(8))
            else:
                fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()
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
        title = self.plot_title
        if extra_title:
            title += ', ' + extra_title
        ax.set_title(title, fontsize=12)
        if show_resonances:
            self.set_resonance_axis(ax, show_resonances, rmin, rmax)
        fig.tight_layout()
        if save:
            savename = self.plotfname
            if extra_title:
                savename = savename[:-4] + '_' + extra_title + '.png'
            p = Path(savename)
            fullpath = Path(savepath) / p.name
            fig.savefig(fullpath, dpi=150)
            logging.info("Created %s", fullpath)
        self.im = im
        return im

    @property
    def plot_title(self):
        lit = {True: "LIT", False: "UNLIT"}
        title = (
            f"{self.image_id}, {self.meta_pixres}, "
            f"{self.imagetime.date().isoformat()}, "
            f"{self.meta_litstatus}"
        )
        return title

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
            show_resonances = ['janus', 'prometheus', 'epimetheus', 'atlas']
        elif show_resonances == 'all':
            show_resonances = self.inside_resonances.moon.unique()
            show_resonances = [
                i for i in show_resonances if i[:-1] not in ['janus', 'epimetheus']]
            show_resonances.extend(['janus', 'epimetheus'])
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
    def median_profile(self):
        return np.nanmedian(self.img, axis=1)

    @property
    def density_wave_subtracted(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'All-NaN slice encountered')
            subtracted = self.img - self.mean_profile[:, np.newaxis]
        return subtracted

    @property
    def density_wave_median_subtracted(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'All-NaN slice encountered')
            subtracted = self.img - self.median_profile[:, np.newaxis]
        return subtracted

    def imshow_subtracted(self, median=False, **kwargs):
        if median:
            self.imshow(data=self.density_wave_median_subtracted, **kwargs)
        else:
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
