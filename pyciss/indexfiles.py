"""Support tools to work with PDS ISS indexfiles."""
import pvl
import pandas as pd
from pathlib import Path
import progressbar


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
            return [self.name + '_' + str(i+1) for i in range(self.items)]

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
                bucket.append((off, off+self.item_bytes))
                i+=1
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


class Label(object):
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
        return self.lbl['IMAGE_INDEX_TABLE']

    @property
    def pvl_columns(self):
        return self.table.getlist('COLUMN')

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


def iss_index_to_df(indexpath, labelpath=None):
    """Read index.tab file with appropriate label file into dataframe.

    Parameters
    ----------
    indexpath : str or pathlib.Path
        Path to actual indexfile to be read into dataframe.
    labelpath : str or pathlib.Path
        Path to labelfile that desribes content to indexfiles.
    """
    if labelpath is None:
        df = pd.read_csv(indexpath, header=None)
    else:
        label = Label(labelpath)
        df = pd.read_fwf(indexpath, header=None,
                         names=label.colnames,
                         colspecs=label.colspecs)
    return df


def convert_indexfiles_to_hdf(folder, labelpath):
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
        bucket.append(iss_index_to_df(indexfile, labelpath))
        bar.update(i)
    totalindex = pd.concat(bucket, ignore_index=True)
    # Converting timestrings to datetimes
    for column in [i for i in totalindex.columns if 'TIME' in i]:
        totalindex[column] = pd.to_datetime(totalindex[column].map(utils.nasa_datetime_to_iso))
    savepath = indexdir / 'iss_totalindex.hdf'
    totalindex.to_hdf(savepath, 'df')
    print("Created pandas HDF index database file here:\n{}".format(savepath))
