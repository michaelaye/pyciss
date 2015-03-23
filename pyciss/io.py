import os
from pysis import CubeFile
import matplotlib.pyplot as plt
import numpy as np


HOME = os.environ['HOME']

dataroot = os.path.join(HOME, 'data/ciss')


def calc_4_3(width):
    return (width, 3*width/4)


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
        return self.mapping_label['PixelResolution']['value']

    @property
    def resolution_unit(self):
        return self.mapping_label['PixelResolution']['units']

    @property
    def plotfname(self):
        return self.filename.split('.')[0]

    def imshow(self, data=None, plow=2, phigh=98, save_ext=None):
        if data is None:
            data = self.img
        min_, max_ = np.percentile(data[~np.isnan(data)], (plow, phigh))
        fig, ax = plt.subplots(figsize=calc_4_3(10))
        ax.imshow(data, extent=self.extent, cmap='bone', vmin=min_, vmax=max_,
                  interpolation='sinc')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Radius [1e6 km]')
        ax.ticklabel_format(useOffset=False)
        ax.grid('on')
        title = "{}, Resolution: {} {}".format(self.filename,
                                               self.resolution_val,
                                               self.resolution_unit)

        ax.set_title(title, fontsize=14)
        if save_ext is not None:
            savename = 'plots/'+self.plotfname+'_'+save_ext+'.png'
            fig.savefig(savename, dpi=150)

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
