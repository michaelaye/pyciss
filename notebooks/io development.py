
# coding: utf-8

# In[ ]:

from pyciss.io import RingCube, PathManager, db_mapped_cubes


# In[ ]:

all_mapped_cubes = db_mapped_cubes()


# # meta development

# In[ ]:

from pyciss.meta import prime_resonances


# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

cube = RingCube(next(all_mapped_cubes))
cube.imshow()


# In[ ]:

cube.meta


# In[ ]:

dics = []
for p in db_mapped_cubes():
    d = {}
    d['path'] = p
    cube = RingCube(p)
    d['meta_res'] = cube.meta_pixres
    d['label_res'] = cube.resolution_val
    d['time'] = cube.imagetime
    dics.append(d)


# In[ ]:

df = pd.DataFrame(dics)


# In[ ]:

df.head()


# In[ ]:

df['id'] = df.path.map(lambda x: x.name.split('_')[0])


# In[ ]:

df.set_index('time',inplace=True)


# In[ ]:

df.set_index('id', inplace=True)


# In[ ]:

df = df.sort_index()


# In[ ]:

df.tail()


# In[ ]:

df['ratio'] = df.meta_res / df.label_res


# In[ ]:

df[df.label_res<5000].plot(style='*')


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



