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


# resonances
def get_order(name):
    ratio = name.split()[1]
    a, b = ratio.split(':')
    return int(a)-int(b)

with pr.resource_stream('pyciss', 'data/ring_resonances.csv') as f:
    resonances = pd.read_csv(f)
    resonances.columns = ['name','radius', 'a_moon', 'n','kappa']
    resonances = resonances.sort_values(by='radius', ascending=True)
    resonances['order'] = resonances.name.map(get_order)

prime_resonances = resonances[resonances.order == 1]
