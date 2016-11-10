from pathlib import Path

import pandas as pd
import yaml

try:
    from pysis.isis import getkey
except ImportError:
    print("Cannot import ISIS system.")

configpath = Path.home() / '.pyciss.yaml'


def get_config():
    if not configpath.exists():
        raise IOError("Config file .pyciss.yaml not found.")
    else:
        with configpath.open() as f:
            return yaml.load(f)


if not configpath.exists():
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
    try:
        d = get_config()
    except IOError:
        d = {}
    d['pyciss_db_path'] = dbfolder
    with configpath.open('w') as f:
        yaml.dump(d, f, default_flow_style=False)
    print("Saved database path into {}.".format(configpath))


def db_mapped_cubes():
    return get_db_root().glob("**/*cal.dst.map.cub")


def db_label_paths():
    return get_db_root().glob("*.LBL")


def get_db_root():
    with configpath.open() as f:
        d = yaml.load(f)
    dbroot = Path(d['pyciss_db_path'])
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
        d[key] = [len(list(dbroot.glob("**/*"+val)))]
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

    extensions = {
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

    def __init__(self, img_id, savedir=None):

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

        self.set_attributes()

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
            try:
                path = list(self.basepath.glob(self.img_id + '_?' + v))[0]
            except IndexError:
                path = None
            setattr(self, k, path)


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
