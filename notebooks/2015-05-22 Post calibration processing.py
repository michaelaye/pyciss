
# coding: utf-8

# # Plot creation

# In[1]:

from pathlib import Path


# In[3]:

root = Path('/Users/klay6683/Dropbox/data/ciss/SOI')


# In[5]:

list(root.glob('*.cub'))


# In[4]:

res = glob.glob('/cassini_ringsdata/opus/N*/*.map.dst.cal.cub')


# In[5]:

fnames = pd.Series(res)
fnames.head()


# In[6]:

fnames.size


# In[7]:

fnames = pd.DataFrame(fnames)


# In[8]:

fnames.columns = ['filtered']


# In[9]:

fnames.head()


# In[10]:

import os
fnames['obs_id'] = fnames.filtered.map(lambda x: os.path.dirname(x).split('/')[-1])


# In[11]:

fnames.head()


# In[12]:

fnames.set_index('obs_id', inplace=True)


# In[13]:

fnames.head()


# In[14]:

def get_unfiltered_from_filtered(filtered):
    dirname = os.path.dirname(filtered)
    unfiltered = glob.glob(os.path.join(dirname, '*.map.cal.cub'))
    if unfiltered:
        return unfiltered[0]
    else:
        return None
fnames['unfiltered']=fnames.filtered.map(get_unfiltered_from_filtered)


# In[15]:

fnames.describe()


# In[16]:

SOI = fnames[fnames.filtered.str.contains('N146734')]


# In[17]:

SOI


# In[18]:

def convert_to_png(fname):
    import gdal
    from pyciss import io
    ds = gdal.Open(fname)
    if ds.RasterXSize > 5200:
        return fname, False
    cube = io.RingCube.open(fname)
    cube.imshow(save=True, extra_title='Filtered')
    return fname, True


# In[118]:

from IPython.parallel import Client
c = Client()


# In[119]:

lbview = c.load_balanced_view()


# In[124]:

results = lbview.map_async(convert_to_png, SOI.filtered)


# In[125]:

from iuvs.multitools import *


# In[126]:

from time import sleep
prog = IntProgress(min=0, max=len(SOI))
display(prog)
while not results.ready():
    sleep(1)
    prog.value = results.progress
print("Done.")


# In[106]:

results.result


# In[157]:

for fname in SOI.filtered:
    dirname = os.path.dirname(fname)
    sourcename = dirname+'/*.png'
    source2name = dirname+'/*.map.dst.cal.cub'
    targetname = '/cassini_ringsdata/SOI/'
    print(sourcename, source2name, targetname)
    get_ipython().system('cp {sourcename} {source2name} {targetname}')


# # Comparison

# In[9]:

plt.ioff()
import os
for fname in SOI:
    print(os.path.basename(fname))
    fig, axes = plt.subplots(ncols=2, figsize=io.calc_4_3(10))
    oldcube = io.RingCube.open(fname.split('.')[0]+'.map.cal.cub')
    oldcube.imshow(ax=axes[0])
    newcube = io.RingCube.open(fname)
    newcube.imshow(ax=axes[1])
    savename = os.path.basename(fname).split('.')[0]+'_compare.png'
    fig.savefig('/cassini_ringsdata/SOI/'+savename, dpi=150)


# # Create tifs

# In[154]:

from pysis.isis import isis2std
for fname in SOI.filtered:
    dirname = os.path.dirname(fname)
    cube = glob.glob(os.path.join(dirname, '*.map.dst.cal.cub'))[0]
    print(cube)
    isis2std(from_=cube, to=cube[:-3]+'png', format='png',
             minpercent=2, maxpercent=98,)
#     bittype='8bit')


# In[ ]:



