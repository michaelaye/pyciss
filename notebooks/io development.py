
# coding: utf-8

# In[1]:

from pyciss.io import RingCube, PathManager, db_mapped_cubes


# In[2]:

all_mapped_cubes = list(db_mapped_cubes())


# # meta development

# In[3]:

from pyciss.meta import prime_resonances


# In[4]:

get_ipython().magic('matplotlib nbagg')


# In[21]:

cube = RingCube(all_mapped_cubes[5])
cube.imshow()


# In[7]:

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


# In[6]:

from ipyparallel import Client
c = Client()
lbview = c.load_balanced_view()


# In[9]:

from nbtools import display_multi_progress


# In[10]:

results = lbview.map_async(get_all_meta_data, all_mapped_cubes)


# In[11]:

display_multi_progress(results, all_mapped_cubes)


# In[12]:

df = pd.DataFrame(results.result())
df


# In[14]:

df.to_csv('all_meta.csv',index=False)


# In[8]:

df = pd.read_csv('all_meta.csv')


# In[10]:

df.columns


# In[11]:

df.head()


# In[12]:

from pathlib import Path


# In[13]:

df['id'] = df.path.map(lambda x: Path(x).name.split('_')[0])


# In[14]:

df.id.head()


# In[15]:

df.set_index('time',inplace=True)


# In[31]:

df.set_index('id', inplace=True)


# In[16]:

df = df.sort_index()


# In[18]:

df.describe()


# In[20]:

t0 = '2004-12'
t1 = '2005-07'
t2 = '2005-08'
df[:t0].plot(style='*', logy=False, markersize=16, rot=25)


# In[18]:

cube = RingCube(df[df.label_res>5000].path.values[0])


# In[19]:

cube.imshow()


# In[36]:

cube.imagetime


# In[22]:

cube.get_opus_meta_data()


# In[26]:

cube.opusmeta.ring_geom


# # Resonances plotting

# In[1]:

from pyciss.meta import prime_resonances as resonances
from pyciss import io


# In[2]:

resonances.head()


# In[53]:

all_mapped_cubes = io.db_mapped_cubes()


# In[59]:

get_ipython().magic('matplotlib inline')


# In[62]:

cube = io.RingCube(next(all_mapped_cubes))


# In[63]:

cube.imshow()


# In[52]:

cube = io.RingCube(next(all_mapped_cubes))

fig, ax = plt.subplots(figsize=(12,9))
cube.imshow(ax=ax)

ax2 = ax.twinx()
ax2.set_ybound(cube.minrad, cube.maxrad)
ax2.ticklabel_format(useOffset=False)
ax2.set_yticks(newticks.radius/1000)
ax2.set_yticklabels(newticks.name);


# In[33]:

ax.get_ybound()


# In[34]:

ax.get_ylim()


# In[35]:

get_ipython().magic('pinfo2 ax.get_ylim')


# In[36]:

get_ipython().magic('pinfo2 ax.get_ybound')


# In[ ]:

ax2 = ax.twinx


# In[ ]:

ax.set_yticks(resonanc)


# In[96]:

f = lambda x,y: (resonances['radius']>x) & (resonances['radius']<y)


# In[97]:

resonances[f(134220, 134326)]


# In[93]:

resonances.describe()


# In[ ]:



