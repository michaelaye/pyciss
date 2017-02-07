from pathlib import Path

import numpy as np
import pandas as pd

from .io import config


def read_cumulative_iss_index():
    "Read in the whole cumulative index and return dataframe."
    try:
        indexdir = Path(config['pyciss_index']['path'])
    except KeyError:
        print("Did not find the key `[pyciss_index][path]` in the config file.")
        return
    path = indexdir / 'cumindex.tab.hdf'
    df = pd.read_hdf(path, 'df')
    # replace DPS Nan values (-1e32) with real NaNs
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


#
# def
#     else:
#         df = index_to_df(indexdir / 'cumindex.tab')
#         df.to_hdf(savepath, 'df')
#         return df
#

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
