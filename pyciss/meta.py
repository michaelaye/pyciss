import pandas as pd
import pkg_resources as pr

def read_metadata(f):
    df = pd.read_csv(f, header=None, delim_whitespace=True)
    df = df.rename(columns={0: 'id', 1: 'pixres', 14: 'lit_status'})
    df = df.set_index('id')
    df['is_lit'] = df.lit_status == True
    # df.drop('lit_status', axis=1)
    return df

with pr.resource_stream('pyciss', 'data/metadata.txt') as f:
    meta_df = read_metadata(f)


with pr.resource_stream('pyciss', 'data/ring_resonances.csv') as f:
    resonances = pd.read_csv(f)
