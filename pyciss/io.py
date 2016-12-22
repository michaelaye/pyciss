"""This module manages where downloaded data is stored via a config
file. It also has a PathManager to support finding the paths to files
of interest."""
from pathlib import Path

import pandas as pd
import configparser

from collections import OrderedDict

try:
    from pysis.isis import getkey
except ImportError:
    print("Cannot import ISIS system.")


def get_oldconfigpath():
    return Path.home() / '.pyciss.yaml'


def get_configpath():
    return Path.home() / '.pyciss.ini'


def get_config():
    """Read the configfile and return config dict.

    Returns
    -------
    dict
        Dictionary with the content of the configpath file.
    """
    configpath = get_configpath()
    if not configpath.exists():
        raise IOError("Config file {} not found.".format(str(configpath)))
    else:
        config = configparser.ConfigParser()
        config.read(str(configpath))
        return config


def transfer_config():
    oldconfigpath = get_oldconfigpath()
    configpath = get_configpath()
    with oldconfigpath.open() as f:
        yaml_config = f.readlines()
    # clean up and break up into tokens
    name, value = [i.strip() for i in yaml_config[0].split(': ')]
    # create new configparser
    config = configparser.ConfigParser()
    config['pyciss_db'] = {}
    config['pyciss_db']['path'] = value
    with configpath.open('w') as configfile:
        config.write(configfile)
    oldconfigpath.unlink()


# some root level code for config
oldconfigpath = get_oldconfigpath()
configpath = get_configpath()
if oldconfigpath.exists() and not configpath.exists():
    transfer_config()
elif not configpath.exists():
    print("No configuration file {} found.\n".format(configpath))
    print("Please run `pyciss.io.set_database_path()` and provide the path where\n"
          "you want to keep your automatically downloaded images.")
    print("`pyciss` will store this path in {}, where you can easily change it later."
          .format(configpath))
else:
    config = get_config()


def set_database_path(dbfolder):
    """Use to write the database path into the config.

    Using the socket module to determine the host/node name and
    creating a new section in the config file.

    Parameters
    ----------
    dbfolder : str or pathlib.Path
        Path to where pyciss will store the ISS images it downloads and receives.
    """
    configpath = get_configpath()
    try:
        d = get_config()
    except IOError:
        d = configparser.ConfigParser()
        d['pyciss_db'] = {}
    d['pyciss_db']['path'] = dbfolder
    with configpath.open('w') as f:
        d.write(f)
    print("Saved database path into {}.".format(configpath))


def db_mapped_cubes():
    return get_db_root().glob("**/*cal.dst.map.cub")


def db_label_paths():
    return get_db_root().glob("*.LBL")


def get_db_root():
    "Read dbroot folder from config and mkdir if required."
    d = get_config()
    dbroot = Path(d['pyciss_db']['path'])
    dbroot.mkdir(exist_ok=True)
    return dbroot


def print_db_stats():
    """Print database stats.

    Returns
    -------
    pd.DataFrame
        Table with the found data items per type.
    """
    dbroot = get_db_root()
    n_ids = len(list(dbroot.glob("[N,W]*")))
    print("Number of WACs and NACs in database: {}".format(n_ids))
    print("These kind of data are in the database: (returning pd.DataFrame)")
    d = {}
    for key, val in PathManager.extensions.items():
        d[key] = [len(list(dbroot.glob("**/*" + val)))]
    return pd.DataFrame(d)


class PathManager(object):

    """Manage paths to data in database.

    The `.pyciss.yaml` config file determines the path to the database for ISS images.
    With this class you can access the different kind of files conveniently.

    Using the stored extensions dictionary, the attributes of the object listed here are created
    dynamically at object initialization and when the image_id is being set.

    NOTE
    ----
    This class will read the .pyciss.yaml to define the pyciss_db path, but
    one can also call it with the savedir argument to override that.

    Parameters
    ----------
    img_id : str or pathlib.Path
        The N... or W... image identifier string of CISS images or the absolute
        path to an existing image
    savedir : str or pathlib.Path
        Path to the pyciss image database. By default defined by what's found in
        the .pyciss.yaml config, but can be overridden using this parameter.

    Attributes
    ----------
    basepath
    img_id
    calib_img
    calib_label
    raw_image
    raw_cub
    raw_label
    cube_path
    tif
    """

    d = {
        'cubepath': '.cal.dst.map.cub',
        'cal_cub': '.cal.cub',
        'dst_cub': '.cal.dst.cub',
        'raw_cub': '.cub',
        'raw_label': '.LBL',
        'raw_image': '.IMG',
        'calib_img': '_CALIB.IMG',
        'calib_label': '_CALIB.LBL',
        'tif': '.cal.dst.map.tif',
    }
    # ordered, sorted by key:
    extensions = OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    def __init__(self, img_id, savedir=None):
        self.input_img_id = img_id
        if Path(img_id).is_absolute():
            # the split is to remove the _1.IMG or _2.IMG from the path
            # for the image id.
            self._id = Path(img_id).name.split('_')[0]
        else:
            # I'm using only filename until _ for storage
            # TODO: Could this create a problem?
            self._id = img_id[:11]
        if savedir is None:
            self.dbroot = get_db_root()
        else:
            self.dbroot = Path(savedir)

        self.set_version()
        self.set_attributes()

    def set_version(self):
        id_ = Path(self.input_img_id).name
        if len(id_) > 11:
            self.version = id_[12]
        else:
            # if the given id was without version, check if a raw file is in database:
            try:
                rawpath = next(self.basepath.glob(self.img_id + "_?.IMG")).name
            except StopIteration:
                self.version = '0'
            else:
                self.version = rawpath[12]

    @property
    def basepath(self):
        return self.dbroot / self._id

    @property
    def img_id(self):
        return self._id

    @img_id.setter
    def img_id(self, value):
        self._id = value
        self.set_attributes()

    def set_attributes(self):
        for k, v in self.extensions.items():
            path = self.basepath / ("{}_{}{}".format(self.img_id,
                                                     self.version,
                                                     v))
            setattr(self, k, path)

    def __str__(self):
        s = ''
        for k, v in self.extensions.items():
            s += "{}: ".format(k)
            path = getattr(self, k)
            if path.exists():
                s += "{}\n".format(path)
            else:
                s += "not found.\n"
        return s

    def __repr__(self):
        return self.__str__()


class DBManager():
    def __init__(self):
        self.dbroot = get_db_root()

    def print_stats(self):
        print_db_stats()


def is_lossy(label):
    """Check Label file for the compression type. """
    val = getkey(from_=label, keyword='INST_CMPRS_TYPE').decode().strip()
    if val == 'LOSSY':
        return True
    else:
        return False
