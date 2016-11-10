import yaml
from pathlib import Path

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


class PathManager(object):

    """Manage paths to data in database.

    The `.pyciss.yaml` config file determines the path to the database for ISS images.
    With this class you can access the different kind of files conveniently.

    NOTE: This class will read the .pyciss.yaml to define the pyciss_db path, but
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
    """

    def __init__(self, img_id, savedir=None):

        if Path(img_id).is_absolute():
            self._id = Path(img_id).name.split('_')[0]
        else:
            # I'm using only filename until _ for storage
            self._id = img_id[:11]
        if savedir is not None:
            self._dbroot = Path(savedir)
        else:
            self._dbroot = get_db_root()

        self._basepath = self._dbroot / self._id

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

    def glob_for_pattern(self, pattern):
        return self.check_and_return(self.basepath.glob(self._id + pattern))

    @property
    def calib_img(self):
        return self.glob_for_pattern("*_CALIB.IMG")

    @property
    def calib_label(self):
        return self.glob_for_pattern("*_CALIB.LBL")

    @property
    def raw_image(self):
        return self.glob_for_pattern("*_?.IMG")

    @property
    def raw_cub(self):
        return self.glob_for_pattern("*_?.cub")

    @property
    def cal_cub(self):
        return self.glob_for_pattern("*_?.cal.cub")

    @property
    def dst_cub(self):
        "pathlib.Path : Path to destriped calibrated unprojected product."
        return self.glob_for_pattern("*_?.cal.dst.cub")

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
