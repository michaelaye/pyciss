from astropy.time import Time


def which_epi_janus_resonance(name, time):
    """Find which swap situtation we are in by time.

    Starting from 2006-01-21 where a Janus-Epimetheus swap occured, and
    defining the next 4 years until the next swap as `scenario1, and the 4
    years after that `scenario2`.
    Calculate in units of 4 years, in which scenario the given time falls.

    Parameters
    ----------
    time : timestring, datetime
        Time of the image. The astropy Time object can deal with both formats.

    Returns
    -------
    str
        The given name string (either `janus` or `epimetheus`) and attach
        a 1 or 2, as appropriate.
    """
    t1 = Time('2002-01-21').to_datetime()
    delta = Time(time).to_datetime() - t1
    yearfraction = delta.days / 365
    if int(yearfraction / 4) % 2 == 0:
        return name + '2'
    else:
        return name + '1'
