
# coding: utf-8

# In[ ]:

from pyciss.io import RingCube, PathManager, db_mapped_cubes
from pyciss import io


# # database

# In[ ]:

io.dbroot


# In[ ]:

calibs = list(io.dbroot.glob("**/*_CALIB*"))


# In[ ]:

pm = PathManager(calibs[0])


# In[ ]:

pm.img_id


# In[ ]:

pm.calib_img


# In[ ]:

import gdal


# In[ ]:

gdal.UseExceptions()


# In[ ]:

ds = gdal.Open(pm.calib_label.as_posix())


# In[ ]:

orig_calib = ds.ReadAsArray()


# In[ ]:

ds = gdal.Open(pm.cal_cub.as_posix())
new_calib = ds.ReadAsArray()
new_calib[new_calib<0] = orig_calib.min()


# In[ ]:

diff = orig_calib - new_calib


# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

from matplotlib.colors import LogNorm


# In[ ]:

plt.figure()
plt.imshow(diff, cmap='viridis', norm=LogNorm())
plt.colorbar()


# In[ ]:

orig_calib.max()


# In[ ]:

np.unique(np.isnan(orig_calib))


# In[ ]:

new_calib.max()


# In[ ]:




# In[ ]:

plt.imshow(new_calib)


# # meta development

# In[ ]:

from pyciss.meta import prime_resonances


# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

cube = RingCube(all_mapped_cubes[5])
cube.imshow()


# In[ ]:

def get_all_meta_data(p):
    from pyciss.io import RingCube
    d = {}
    d['path'] = p
    cube = RingCube(p)
    opusmeta = cube.get_opus_meta_data()
    d['meta_res'] = cube.meta_pixres
    d['label_res'] = cube.resolution_val
    d['time'] = cube.imagetime
    res1 = opusmeta.ring_geom['projected_radial_resolution1']
    res2 = opusmeta.ring_geom['projected_radial_resolution2']
    d['opusres'] = int((res1+res2)/2*1000)
    return d


# In[ ]:

from ipyparallel import Client
c = Client()
lbview = c.load_balanced_view()


# In[ ]:

from nbtools import display_multi_progress


# In[ ]:

results = lbview.map_async(get_all_meta_data, all_mapped_cubes)


# In[ ]:

display_multi_progress(results, all_mapped_cubes)


# In[ ]:

df = pd.DataFrame(results.result())
df


# In[ ]:

df.to_csv('all_meta.csv',index=False)


# In[ ]:

df = pd.read_csv('all_meta.csv')


# In[ ]:

df.columns


# In[ ]:

df.head()


# In[ ]:

from pathlib import Path


# In[ ]:

df['id'] = df.path.map(lambda x: Path(x).name.split('_')[0])


# In[ ]:

df.id.head()


# In[ ]:

df.set_index('time',inplace=True)


# In[ ]:

df.set_index('id', inplace=True)


# In[ ]:

df = df.sort_index()


# In[ ]:

df.describe()


# In[ ]:

t0 = '2004-12'
t1 = '2005-07'
t2 = '2005-08'
df[:t0].plot(style='*', logy=False, markersize=16, rot=25)


# In[ ]:

cube = RingCube(df[df.label_res>5000].path.values[0])


# In[ ]:

cube.imshow()


# In[ ]:

cube.imagetime


# In[ ]:

cube.get_opus_meta_data()


# In[ ]:

cube.opusmeta.ring_geom


# # Resonances plotting

# In[ ]:

from pyciss.meta import prime_resonances as resonances
from pyciss import io


# In[ ]:

resonances.head()


# In[ ]:

all_mapped_cubes = io.db_mapped_cubes()


# In[ ]:

get_ipython().magic('matplotlib inline')


# In[ ]:

cube = io.RingCube(next(all_mapped_cubes))


# In[ ]:

cube.imshow()


# In[ ]:

cube = io.RingCube(next(all_mapped_cubes))

fig, ax = plt.subplots(figsize=(12,9))
cube.imshow(ax=ax)

ax2 = ax.twinx()
ax2.set_ybound(cube.minrad, cube.maxrad)
ax2.ticklabel_format(useOffset=False)
ax2.set_yticks(newticks.radius/1000)
ax2.set_yticklabels(newticks.name);


# In[ ]:

ax.get_ybound()


# In[ ]:

ax.get_ylim()


# In[ ]:

get_ipython().magic('pinfo2 ax.get_ylim')


# In[ ]:

get_ipython().magic('pinfo2 ax.get_ybound')


# In[ ]:

ax2 = ax.twinx


# In[ ]:

ax.set_yticks(resonanc)


# In[ ]:

f = lambda x,y: (resonances['radius']>x) & (resonances['radius']<y)


# In[ ]:

resonances[f(134220, 134326)]


# In[ ]:

resonances.describe()


# In[ ]:



