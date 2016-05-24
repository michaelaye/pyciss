from socket import gethostname

import configparser as cp
from pathlib import Path
import pkg_resources as pr

try:
    from pysis.isis import getkey
except ImportError:
    print("Cannot import ISIS system.")


configpath = pr.resource_filename('pyciss', 'config.ini')
config = cp.ConfigParser()
config.read(configpath)
# just take first node as host name:
hostname = gethostname().split('.')[0]
section = hostname if hostname in config else 'DEFAULT'
dataroot = Path(config[section]['database_path'])

dbroot = dataroot / 'db'
dbroot.mkdir(exist_ok=True)


def set_database_path(dbfolder, _append=False, _testhostname=None):
    """Use to write the database path into the config.

    Using the socket module to determine the host/node name and
    creating a new section in the config file.
    """
    config = cp.ConfigParser()
    config['DEFAULT'] = {}
    if _testhostname is not None:
        hostname = _testhostname
    else:
        hostname = gethostname().split('.')[0]
    config[hostname] = {}
    config[hostname]['database_path'] = dbfolder
    mode = 'a' if _append else 'w'
    with open(configpath, mode) as fp:
        config.write(fp)
    print("Saved database path into {}.".format(configpath))
    print("Please restart your Python to activate the new path settings.")


def db_mapped_cubes():
    return dbroot.glob("**/*cal.dst.map.cub")


def db_label_paths():
    return dbroot.glob("*.LBL")


class PathManager(object):

    """Manage paths to data in database.

    The `config.ini` file determines the path to the database for ISS images.
    With this class you can access the different kind of files conveniently.

    Parameters
    ----------
    img_id : {str, pathlib.Path)
        The N... or W... image identifier string of CISS images or the absolute
        path to an existing image
    """

    def __init__(self, img_id, savedir=None):

        if Path(img_id).is_absolute():
            self._id = Path(img_id).name.split('_')[0]
        else:
            self._id = img_id
        if savedir is not None:
            self._basepath = Path(savedir) / self._id
        else:
            self._basepath = dbroot / self._id

    @property
    def basepath(self):
        return self._basepath

    @property
    def img_id(self):
        return self._id

    def check_and_return(self, myiter):
        l = list(myiter)
        if l:
            return l[0]
        else:
            print("No file found.")
            return None

    @property
    def calib_img(self):
        return self.check_and_return((self._basepath).glob(self._id + "*_CALIB.IMG"))

    @property
    def calib_label(self):
        return self.check_and_return((self._basepath).glob(self._id + "*_CALIB.LBL"))

    @property
    def raw_image(self):
        return self.check_and_return((self._basepath).glob(self._id + "*_?.IMG"))

    @property
    def raw_cub(self):
        return self.check_and_return((self._basepath).glob(self._id + "*_?.cub"))

    @property
    def cal_cub(self):
        return self.check_and_return((self._basepath).glob(self._id + "*_?.cal.cub"))

    @property
    def raw_label(self):
        try:
            return self.raw_image.with_suffix('.LBL')
        except AttributeError:
            return None

    @property
    def cubepath(self):
        try:
            return self.raw_label.with_suffix('.cal.dst.map.cub')
        except AttributeError:
            return None


def is_lossy(label):
    """Check Label file for the compression type. """
    val = getkey(from_=label, keyword='INST_CMPRS_TYPE').decode().strip()
    if val == 'LOSSY':
        return True
    else:
        return False


def calc_4_3(width):
    return (width, 3*width/4)
