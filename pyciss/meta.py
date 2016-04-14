import pandas as pd

from . import io

paths = [io.dataroot / 'coiss_ahires.0{}.list.txt'.format(i) for i in [15, 19, 25]]


def read_metadata(i):
    df = pd.read_csv(str(paths[i]), header=None, delim_whitespace=True)
    return df.rename(columns={0: 'id', 1: 'pixres', 14: 'lit_status'})

meta_df = read_metadata(2)
