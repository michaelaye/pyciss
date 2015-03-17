import os
import gdal
from pysis.isis import getkey
import numpy as np

HOME = os.environ['HOME']

dataroot = os.path.join(HOME, 'data/ciss')


class RingCube:
    def __init__(self, cubename):
        self.cubename = cubename
        self.ds = gdal.Open(cubename)
        self.xsize = self.ds.RasterXSize
        self.ysize = self.ds.RasterYSize

    def get_mapping_value(self, keyword):
        val = getkey.check_output(from_=self.cubename,
                                  keyword=keyword,
                                  grpname='mapping')
        return val.strip()

    @property
    def shape(self):
        return (self.ysize, self.xsize)

    @property
    def minrad(self):
        return float(self.get_mapping_value('minimumringradius'))

    @property
    def maxrad(self):
        return float(self.get_mapping_value('maximumringradius'))

    @property
    def minlon(self):
        return float(self.get_mapping_value('minimumringlongitude'))

    @property
    def maxlon(self):
        return float(self.get_mapping_value('maximumringlongitude'))

    def get_data(self):
        data = self.ds.ReadAsArray()
        data[data<0] = np.nan
        return data
