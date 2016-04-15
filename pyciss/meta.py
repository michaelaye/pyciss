import pandas as pd
import pkg_resources as pr

from . import io


def read_metadata(f):
    df = pd.read_csv(f, header=None, delim_whitespace=True)
    return df.rename(columns={0: 'id', 1: 'pixres', 14: 'lit_status'})

with pr.resource_stream('pyciss', 'data/metadata.txt') as f:
    meta_df = read_metadata(f)


with pr.resource_stream('pyciss', 'data/ring_resonances.csv') as f:
    resonances = pd.read_csv(f)
