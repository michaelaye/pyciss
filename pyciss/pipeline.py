from __future__ import division, print_function
from pysis.isis import ciss2isis, cisscal, spiceinit, ringscam2map, getkey,\
    editlab, dstripe, isis2std
from pysis.util import file_variations
from pysis import IsisPool
import gdal
import numpy as np
from os.path import join as pjoin
import os
from pyciss import plotting
from pyciss.io import dataroot
from . import io


ISISDATA = os.environ['ISIS3DATA']


def calibrate_ciss(img_name, name_only=False):
    (cub_name,
     cal_name,
     dst_name,
     map_name) = file_variations(img_name,
                                 ['.cub',
                                  '.cal.cub',
                                  '.dst.cal.cub',
                                  '.map.dst.cal.cub'])
    if name_only:
        return map_name
    ciss2isis(from_=img_name, to=cub_name)
    targetname = getkey(from_=cub_name,
                        grp='instrument',
                        keyword='targetname')
    # forcing the target name to Saturn here, because some observations of
    # the rings have moons as a target, but then the standard map projection
    # onto the Saturn ring plane fails.
    # see also
    # https://isis.astrogeology.usgs.gov/IsisSupport/index.php/topic,3922.0.html
    if targetname.lower() != 'saturn':
        editlab(from_=cub_name, options='modkey',
                keyword='TargetName', value='Saturn',
                grpname='Instrument')
    spiceinit(from_=cub_name, cksmithed='yes', spksmithed='yes',
              shape='ringplane')
    cisscal(from_=cub_name, to=cal_name)
    dstripe(from_=cal_name, to=dst_name, mode='horizontal')
    ringscam2map(from_=dst_name, to=map_name,
                 map=pjoin(ISISDATA,
                           'base/templates/maps/ringcylindrical.map'))
    isis2std(from_=map_name, to=map_name[:-3]+'tif', format='tiff')
    return map_name


def remapping(img_name):
    (cal_name, map_name) = file_variations(img_name,
                                           ['.cal.cub', '.map.cal.cub'])
    print("Mapping", cal_name, "to", map_name)
    mapfname = pjoin(io.HOME, 'data', 'ciss', 'opus', 'ringcylindrical.map')
    ringscam2map(from_=cal_name, to=map_name, map=mapfname, pixres='map')


def calibrate_many(images):
    images = [[img_name, ] + file_variations(img_name, ['.cub', '.cal.cub',
                                                        '.map.cal.cub'])
              for img_name in images]

    with IsisPool() as isis_pool:
        for img_name, cub_name, cal_name, map_name in images:
            isis_pool.ciss2isis(from_=img_name, to=cub_name)

    return images


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
