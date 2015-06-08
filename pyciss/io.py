import os
from pysis import CubeFile
from pysis.isis import getkey
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd

HOME = os.environ['HOME']

dataroot = '/Volumes/Data/ciss'


def is_lossy(label):
    """Check Label file for the compression type. """
    val = getkey(from_=label, keyword='INST_CMPRS_TYPE').decode().strip()
    if val == 'LOSSY':
        return True
    else:
        return False


def calc_4_3(width):
    return (width, 3*width/4)


def get_cube_filelist():
    res = glob.glob('/Volumes/Data/ciss/opus/*/*.map.cal.cub')
    return pd.Series(res)


class RingCube(CubeFile):

    @property
    def mapping_label(self):
        return self.label['IsisCube']['Mapping']

    @property
    def minrad(self):
        return self.mapping_label['MinimumRingRadius']/1e6

    @property
    def maxrad(self):
        return self.mapping_label['MaximumRingRadius']/1e6

    @property
    def minlon(self):
        return self.mapping_label['MinimumRingLongitude']

    @property
    def maxlon(self):
        return self.mapping_label['MaximumRingLongitude']

    @property
    def img(self):
        return self.apply_numpy_specials()[0]

    @property
    def extent(self):
        return [self.minlon, self.maxlon, self.minrad, self.maxrad]

    @property
    def resolution_val(self):
        return self.mapping_label['PixelResolution'].value

    @property
    def resolution_unit(self):
        return self.mapping_label['PixelResolution'].units

    @property
    def plottitle(self):
        return os.path.basename(self.filename).split('.')[0]

    @property
    def plotfname(self):
        return self.filename.split('.')[0] + '.png'

    def imshow(self, data=None, plow=2, phigh=98, save=False, ax=None,
               interpolation='sinc', **kwargs):
        if data is None:
            data = self.img
        min_, max_ = np.percentile(data[~np.isnan(data)], (plow, phigh))
        if ax is None:
            fig, ax = plt.subplots(figsize=calc_4_3(10))
        ax.imshow(data, extent=self.extent, cmap='gray', vmin=min_, vmax=max_,
                  interpolation=interpolation, origin='lower', **kwargs)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Radius [Mkm]')
        ax.ticklabel_format(useOffset=False)
        # ax.grid('on')
        title = "{}, Resolution: {} {}".format(self.plottitle,
                                               int(self.resolution_val),
                                               self.resolution_unit)

        ax.set_title(title, fontsize=14)
        if save:
            fig.savefig(self.plotfname, dpi=150)

    @property
    def density_wave_subtracted(self):
        mean_profile = np.nanmean(self.img, axis=1)
        subtracted = self.img - mean_profile[:, np.newaxis]
        return subtracted

    def imshow_subtracted(self):
        self.imshow(data=self.density_wave_subtracted)

    @property
    def inner_zoom(self, data=None):
        if data is None:
            data = self.img
        shape = self.img.shape
        x1 = shape[0]//4
        x2 = 3*shape[0]//4
        y1 = shape[1]//4
        y2 = 3*shape[1]//4
        return data[x1:x2, y1:y2]

    @property
    def imagetime(self):
        return self.label['IsisCube']['Instrument']['ImageTime']
