from pathlib import Path

import numpy as np
import pandas as pd

from .io import config


def read_cumulative_iss_index():
    "Read in the whole cumulative index and return dataframe."
    try:
        indexdir = Path(config['pyciss_index']['path'])
    except KeyError:
        print(
            "Did not find the key `[pyciss_index][path]` in the config file.")
        return
    path = indexdir / 'cumindex.tab.hdf'
    try:
        df = pd.read_hdf(path, 'df')
    except FileNotFoundError:
        path = indexdir / 'cumindex.hdf'
        df = pd.read_hdf(path, 'df')
    # replace PDS Nan values (-1e32) with real NaNs
    return df.replace(-1.000000e+32, np.nan)


def read_ring_images_index():
    """Filter cumulative index for ring images.

    This is done by matching the column TARGET_DESC to contain the string 'ring'

    Returns
    -------
    pandas.DataFrame
        data table containing only meta-data for ring images
    """
    meta = read_cumulative_iss_index()
    ringfilter = meta.TARGET_DESC.str.contains('ring', case=False)
    return meta[ringfilter]


def get_clearnacs_ring_images():
    df = read_ring_images_index()
    df[df == -1e32] = np.nan
    df = df.set_index('isotime')
    ringimages = df.query("RINGS_FLAG=='YES'")
    ringimages = ringimages[ringimages.MAXIMUM_RING_RADIUS.notnull()]
    ringimages = ringimages[ringimages.MINIMUM_RING_RADIUS.notnull()]
    ringimages = ringimages.query(
        'MAXIMUM_RING_RADIUS < 1e90 and MINIMUM_RING_RADIUS > 0')
    nac = ringimages[ringimages.INSTRUMENT_ID == 'ISSNA']
    clearnacs = nac.query('FILTER_NAME_1 == "CL1" and FILTER_NAME_2 == "CL2"')
    return clearnacs


def filter_for_ringspan(clearnacs, spanlimit):
    "filter for covered ringspan, giver in km."
    delta = clearnacs.MAXIMUM_RING_RADIUS - clearnacs.MINIMUM_RING_RADIUS
    f = delta < spanlimit
    ringspan = clearnacs[f].copy()
    return ringspan


class IndexDB(object):
    def __init__(self, indexdir=None):
        if indexdir is None:
            try:
                indexdir = config['pyciss_index']['path']
            except KeyError:
                print("Did not find the key `pyciss_indexdir` in the config file.")
                return
        self.indexdir = Path(indexdir)

    @property
    def indexfiles(self):
        return self.indexdir.glob('*_????.tab')

    @property
    def cumulative_label(self):
        return IndexLabel(self.indexdir / 'cumindex.lbl')

    def get_index_no(self, no):
        return iss_index_to_df(next(self.indexdir.glob('*_' + str(no) + '.tab')))
