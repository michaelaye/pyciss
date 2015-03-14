from pysis.isis import ciss2isis, cisscal, spiceinit, ringscam2map
from pysis.util import file_variations
import gdal
import numpy as np
from os.path import join as pjoin
import os
from pyciss import plotting
from pyciss.io import dataroot


ISISDATA = os.environ['ISIS3DATA']


def calibrate_ciss(img_name, name_only=False):
    (cub_name, cal_name, map_name) = file_variations(img_name,
                                                     ['.cub', '.cal.cub',
                                                      '.map.cal.cub'])
    if name_only:
        return map_name
    ciss2isis(from_=img_name, to=cub_name)
    spiceinit(from_=cub_name, cksmithed='yes', spksmithed='yes',
              shape='ringplane')
    cisscal(from_=cub_name, to=cal_name)
    ringscam2map(from_=cal_name, to=map_name,
                 map=pjoin(ISISDATA,
                           'base/templates/maps/ringcylindrical.map'))
    return map_name


def process_image(fname):
    ds = gdal.Open(fname)
    data = ds.ReadAsArray()
    data[data < -2e+38] = np.nan
    mean_value = np.nanmean(data, axis=1)
    subtracted = data - mean_value[:, np.newaxis]
    fig = plotting.imshowlowhigh(subtracted)
    savename = pjoin(dataroot, 'pipeline_out')
    fig.savefig(pjoin(savename, fname+'.png'), dpi=150)


def pipeline(fname):
    try:
        map_name = calibrate_ciss(fname)
        process_image(map_name)
    except AttributeError:
        return "Problem with {}".format(fname)

