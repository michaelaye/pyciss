"""This module deals with the metadata I have received from collaborators.

It defines the location of ring resonances for the RingCube plotting.
"""
import pandas as pd
import pkg_resources as pr


def get_meta_df():
    def read_metadata(f):
        df = pd.read_csv(f, header=None, delim_whitespace=True)
        df = df.rename(columns={0: 'id', 1: 'pixres', 14: 'lit_status'})
        df = df.set_index('id')
        df['is_lit'] = df.lit_status is True
        # df.drop('lit_status', axis=1)
        return df

    with pr.resource_stream('pyciss', 'data/metadata.txt') as f:
        meta_df = read_metadata(f)
    return meta_df


# resonances
def get_order(name):
    ratio = name.split()[1]
    a, b = ratio.split(':')
    return int(a) - int(b)


def get_resonances():
    with pr.resource_stream('pyciss', 'data/ring_resonances.csv') as f:
        resonances = pd.read_csv(f)
    resonances.columns = ['name', 'radius', 'a_moon', 'n', 'kappa']
    resonances = resonances.sort_values(by='radius', ascending=True)
    resonances['order'] = resonances.name.map(get_order)
    return resonances


def get_prime_resonances():
    resonances = get_resonances()
    prime_resonances = resonances[resonances.order == 1].drop('order', axis=1)
    # filter out Janus and Epimetheus as we have a more precise file for that.
    prime_resonances = prime_resonances.loc[~prime_resonances.name.str.startswith('Janus')]
    prime_resonances = prime_resonances.loc[~prime_resonances.name.str.startswith('Epimetheus')]
    return prime_resonances


# Janus Epithemeus resonances
def get_janus_epimetheus_resonances():
    w = [len('              Janus1'),
         len(' reson'),
         len('  Resonance radius R')]

    def get_janos_epi_order(reso):
        a, b = reso.split(':')
        return int(a) - int(b)

    fname = pr.resource_filename('pyciss',
                                 'data/ring_janus_epimetheus_resonances.txt')
    with open(fname) as f:
        jan_epi_resonances = pd.read_fwf(f, skiprows=15, header=0, widths=w,
                                         skipfooter=1)

    # replace column names
    jan_epi_resonances.columns = ['moon', 'reson', 'radius']

    # calculate order from resonance name
    jan_epi_resonances['order'] = jan_epi_resonances.reson.map(get_janos_epi_order)

    def func(x):
        "Remove space from resonce string"
        return ':'.join(i.strip() for i in x.split(':'))
    jan_epi_resonances.reson = jan_epi_resonances.reson.map(func)

    # calculate name for axes display
    jan_epi_resonances['name'] = jan_epi_resonances.moon + ' ' +\
        jan_epi_resonances.reson
    return jan_epi_resonances


def get_prime_jan_epi():
    jan_epi_resonances = get_janus_epimetheus_resonances()
    # remove orders > 1 and drop unrequired columns
    prime_jan_epis = jan_epi_resonances[jan_epi_resonances.order == 1]
    to_drop = ['order', 'moon']
    prime_jan_epis = prime_jan_epis.drop(to_drop, axis=1)
    return prime_jan_epis


def get_all_resonances():
    prime_resonances = get_prime_resonances()
    prime_jan_epis = get_prime_jan_epi()
    all_resonances = pd.concat([prime_resonances, prime_jan_epis])
    all_resonances.sort_values(by='radius', inplace=True)
    all_resonances['moon'] = all_resonances.name.map(lambda x: x.split()[0].lower())
    return all_resonances
