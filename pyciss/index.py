from .io import config
import pandas as pd
from pathlib import Path


def read_cumulative_iss_index():
    "Read in the whole cumulative index and return dataframe."
    if indexdir is None:
        try:
            indexdir = Path(config['pyciss_indexdir'])
        except KeyError:
            print("Did not find the key `pyciss_indexdir` in the config file.")
            return

    savepath = indexdir / 'cumindex.tab.hdf'
    if savepath.exists():
        return pd.read_hdf(savepath, 'df')
    else:
        df = index_to_df(indexdir / 'cumindex.tab')
        df.to_hdf(savepath, 'df')
        return df


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
