"""Support tools to work with PDS ISS indexfiles."""
from pathlib import Path

import pandas as pd
import progressbar
import pvl

from planetpy import utils

from .io import config

# The '2' stands for all data at Saturn, '1' would be all transit data.
base_url = "http://pds-rings.seti.org/volumes/COISS_2xxx/COISS_"


class PVLColumn(object):
    def __init__(self, pvlobj):
        self.pvlobj = pvlobj

    @property
    def name(self):
        return self.pvlobj['NAME']

    @property
    def name_as_list(self):
        "needs to return a list for consistency for cases when it's an array."
        if self.items is None:
            return [self.name]
        else:
            return [self.name + '_' + str(i + 1) for i in range(self.items)]

    @property
    def start(self):
        "Decrease by one as Python is 0-indexed."
        return self.pvlobj['START_BYTE'] - 1

    @property
    def stop(self):
        return self.start + self.pvlobj['BYTES']

    @property
    def items(self):
        return self.pvlobj.get('ITEMS')

    @property
    def item_bytes(self):
        return self.pvlobj.get('ITEM_BYTES')

    @property
    def item_offset(self):
        return self.pvlobj.get('ITEM_OFFSET')

    @property
    def colspecs(self):
        if self.items is None:
            return (self.start, self.stop)
        else:
            i = 0
            bucket = []
            for _ in range(self.items):
                off = self.start + self.item_offset * i
                bucket.append((off, off + self.item_bytes))
                i += 1
            return bucket

    def decode(self, linedata):
        if self.items is None:
            start, stop = self.colspecs
            return linedata[start:stop]
        else:
            bucket = []
            for (start, stop) in self.colspecs:
                bucket.append(linedata[start:stop])
            return bucket

    def __repr__(self):
        return self.pvlobj.__repr__()


class TableLabel(object):
    tablename = 'TABLE'
    """Support working with the labelfile of ISS indices."""
    def __init__(self, labelpath):
        self._path = Path(labelpath)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def lbl(self):
        return pvl.load(str(self.path))

    @property
    def table(self):
        return self.lbl[self.tablename]

    @property
    def pvl_columns(self):
        return self.table.getlist('COLUMN')

    @property
    def columns_dic(self):
        return {col['NAME']: col for col in self.pvl_columns}

    @property
    def colnames(self):
        """Read the columns in a ISS index label file.

        The label file for the ISS indices describes the content
        of the index files.
        """
        colnames = []
        for col in self.pvl_columns:
            colnames.extend(PVLColumn(col).name_as_list)
        return colnames

    @property
    def colspecs(self):
        colspecs = []
        columns = self.table.getlist('COLUMN')
        for column in columns:
            pvlcol = PVLColumn(column)
            if pvlcol.items is None:
                colspecs.append(pvlcol.colspecs)
            else:
                colspecs.extend(pvlcol.colspecs)
        return colspecs


class ImageTableLabel(TableLabel):
    tablename = 'IMAGE_INDEX_TABLE'


class RDRIndexLabel(TableLabel):
    tablename = 'RDR_INDEX_TABLE'


class RingGeoTableLabel(TableLabel):
    tablename = 'RING_GEOMETRY_TABLE'


def decode_line(linedata, labelpath):
    """Decode one line of tabbed data with the appropriate label file.

    Parameters
    ----------
    linedata : str
        One line of a .tab data file
    labelpath : str or pathlib.Path
        Path to the appropriate label that describes the data.
    """
    label = ImageTableLabel(labelpath)
    for column in label.pvl_columns:
        pvlcol = PVLColumn(column)
        print(pvlcol.name, pvlcol.decode(linedata))


def index_to_df(indexpath, label, convert_times):
    indexpath = Path(indexpath)
    df = pd.read_fwf(indexpath, header=None,
                     names=label.colnames,
                     colspecs=label.colspecs)
    if convert_times:
        print("Converting times...")
        for column in [i for i in df.columns if 'TIME' in i]:
            df[column] = pd.to_datetime(df[column])

    return df


def iss_index_to_df(indexpath, labelpath=None, convert_times=True):
    """Read index.tab file with appropriate label file into dataframe.

    By default the detached label should be in the same folder as the
    indexfile and will automatically be used.
    The user can force a special labelpath to be used as second
    parameter.

    Parameters
    ----------
    indexpath : str or pathlib.Path
        Path to actual indexfile to be read into dataframe.
    labelpath : str or pathlib.Path
        Path to labelfile that desribes content to indexfiles.
    """
    indexpath = Path(indexpath)
    if labelpath is not None:
        # if extra labelpath given.
        labelpath = Path(labelpath)
    else:
        # create path from index table path
        labelpath = indexpath.with_suffix('.lbl')
    if not labelpath.exists():
        df = pd.read_csv(indexpath, header=None)
    else:
        label = ImageTableLabel(labelpath)
        df = pd.read_fwf(indexpath, header=None,
                         names=label.colnames,
                         colspecs=label.colspecs)
    if convert_times:
        print("Converting times...")
        for column in [i for i in df.columns if 'TIME' in i]:
            df[column] = pd.to_datetime(df[column].map(utils. nasa_datetime_to_iso))

    return df


def convert_indexfiles_to_hdf(folder):
    """Convert all indexfiles to an HDF database.

    Search for .tab files in `folder`, read them into a dataframe,
    concat to large dataframe at the end and store as HDF file.

    Parameters
    ----------
    folder : str or pathlib.Path
        Folder in where to search for .tab files
    labelpath : str or pathlb.Path
    """
    indexdir = Path(folder)
    indexfiles = list(indexdir.glob('*.tab'))
    bucket = []
    bar = progressbar.ProgressBar(max_value=len(indexfiles))
    for i, indexfile in enumerate(indexfiles):
        # convert times later, more performant
        df = iss_index_to_df(indexfile, convert_times=False)
        df['index_fname'] = str(indexfile)
        bucket.append(df)
        bar.update(i)
    totalindex = pd.concat(bucket, ignore_index=True)
    # Converting timestrings to datetimes
    print("Converting times...")
    for column in [i for i in totalindex.columns if 'TIME' in i]:
        totalindex[column] = pd.to_datetime(totalindex[column].
                                            map(utils.
                                                nasa_datetime_to_iso))
    savepath = indexdir / 'iss_totalindex.hdf'
    totalindex.to_hdf(savepath, 'df')
    print("Created pandas HDF index database file here:\n{}"
          .format(savepath))


def read_cumulative_index(indexdir=None):
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
        df = iss_index_to_df(indexdir / 'cumindex.tab')
        df.to_hdf(savepath, 'df')
        return df


class IndexDB(object):
    def __init__(self, indexdir=None):
        if indexdir is None:
            try:
                indexdir = config['pyciss_indexdir']
            except KeyError:
                print("Did not find the key `pyciss_indexdir` in the config file.")
                return
        self.indexdir = Path(indexdir)

    @property
    def indexfiles(self):
        return self.indexdir.glob('*_????.tab')

    @property
    def cumulative_label(self):
        return ImageTableLabel(self.indexdir / 'cumindex.lbl')

    def get_index_no(self, no):
        return iss_index_to_df(next(self.indexdir.glob('*_' + str(no) + '.tab')))
