from pathlib import Path

import numpy as np
import pandas as pd

from planetpy.pdstools import indices

from ._utils import which_epi_janus_resonance
from .io import config
from .meta import get_all_resonances

resonances = get_all_resonances()


def get_index_dir():
    try:
        indexdir = Path(config["pyciss_index"]["path"])
    except KeyError:
        print("Did not find the key `[pyciss_index][path]` in the config file.")
        return None
    else:
        return indexdir


def download_general_index():
    indices.download("cassini:iss:index", get_index_dir())


def download_ring_summary_index():
    indices.download("cassini:iss:ring_summary", get_index_dir())


def read_cumulative_iss_index():
    "Read in the whole cumulative index and return dataframe."
    indexdir = get_index_dir()

    path = indexdir / "COISS_2999_index.hdf"
    try:
        df = pd.read_hdf(path, "df")
    except FileNotFoundError:
        path = indexdir / "cumindex.hdf"
        df = pd.read_hdf(path, "df")
    # replace PDS Nan values (-1e32) with real NaNs
    df = df.replace(-1.000000e32, np.nan)
    return df.replace(-999.0, np.nan)


def ring_summary_index():
    indexdir = get_index_dir()

    path = indexdir / "COISS_2999_ring_summary.hdf"
    try:
        df = pd.read_hdf(path, "df")
    except FileNotFoundError:
        print("File not found.")
        return
    else:
        df = df.replace(-1.00000e32, np.nan)
        return df.replace(-999.0, np.nan)


def read_ring_images_index():
    """Filter cumulative index for ring images.

    This is done by matching the column TARGET_DESC to contain the string 'ring'

    Returns
    -------
    pandas.DataFrame
        data table containing only meta-data for ring images
    """
    meta = read_cumulative_iss_index()
    ringfilter = meta.TARGET_DESC.str.contains("ring", case=False)
    return meta[ringfilter]


def get_clearnacs_ring_images():
    df = read_ring_images_index()
    df[df == -1e32] = np.nan
    try:
        df = df.set_index("isotime")
    except KeyError:
        print("'isotime' column does not exist. Leaving index as it is.")
    ringimages = df.query("RINGS_FLAG=='YES'")
    ringimages = ringimages[ringimages.MAXIMUM_RING_RADIUS.notnull()]
    ringimages = ringimages[ringimages.MINIMUM_RING_RADIUS.notnull()]
    ringimages = ringimages.query(
        "MAXIMUM_RING_RADIUS < 1e90 and MINIMUM_RING_RADIUS > 0"
    )
    nac = ringimages[ringimages.INSTRUMENT_ID == "ISSNA"]
    clearnacs = nac.query('FILTER_NAME_1 == "CL1" and FILTER_NAME_2 == "CL2"')
    return clearnacs


def filter_for_ringspan(clearnacs, spanlimit):
    "filter for covered ringspan, giver in km."
    delta = clearnacs.MAXIMUM_RING_RADIUS - clearnacs.MINIMUM_RING_RADIUS
    f = delta < spanlimit
    ringspan = clearnacs[f].copy()
    return ringspan


def get_resonances_inside_radius(row):
    minrad = row["MINIMUM_RING_RADIUS"]
    maxrad = row["MAXIMUM_RING_RADIUS"]
    lower_filter = resonances["radius"] > (minrad)
    higher_filter = resonances["radius"] < (maxrad)
    insides = resonances[lower_filter & higher_filter]
    return insides


def check_for_resonance(row, as_bool=True):
    insides = get_resonances_inside_radius(row)
    return bool(len(insides)) if as_bool else len(insides)


def check_for_janus_resonance(row, as_bool=True):
    insides = get_resonances_inside_radius(row)
    # row.name is the index of the row, which is a time!
    janus = which_epi_janus_resonance("janus", row.name)
    moonfilter = insides.moon == janus
    return bool(len(insides[moonfilter]))


def get_janus_phase(time):
    return which_epi_janus_resonance("janus", time)
