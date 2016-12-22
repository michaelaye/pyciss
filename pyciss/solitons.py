from datetime import datetime as dt

import pandas as pd
import pkg_resources as pr
from astropy import units as u
from numpy import poly1d


def get_year_since_resonance(ringcube):
    "Calculate the fraction of the year since moon swap."
    t0 = dt(2006, 1, 21)
    td = ringcube.imagetime - t0
    return td.days / 365.25


def create_polynoms():
    """Create and return poly1d objects.

    Uses the parameters from Morgan to create poly1d objects for
    calculations.
    """
    fname = pr.resource_filename('pyciss', 'data/soliton_prediction_parameters.csv')
    res_df = pd.read_csv(fname)
    polys = {}
    for resorder, row in zip('65 54 43 21'.split(),
                             range(4)):
        p = poly1d([res_df.loc[row, 'Slope (km/yr)'], res_df.loc[row, 'Intercept (km)']])
        polys['janus' + resorder] = p
    return polys


def check_for_soliton(ringcube):
    """Workhorse function.

    Creates the polynom.
    Calculates radius constraints from attributes in `ringcube` object.

    Parameters
    ----------
    ringcube : pyciss.ringcube.RingCube
        A containter class for a ring-projected ISS image file.

    Returns
    -------
    dict
        Dictionary with all solitons found. Reason why it is a dict is
        that it could be more than one in one image.
    """
    polys = create_polynoms()
    minrad = ringcube.minrad.to(u.km)
    maxrad = ringcube.maxrad.to(u.km)
    delta_years = get_year_since_resonance(ringcube)
    soliton_radii = {}
    for k, p in polys.items():
        current_r = p(delta_years) * u.km
        if minrad < current_r < maxrad:
            soliton_radii[k] = current_r
    return soliton_radii if soliton_radii else None
