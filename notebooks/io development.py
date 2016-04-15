
# coding: utf-8

# In[1]:

from pyciss.io import RingCube, PathManager, db_mapped_cubes


# In[2]:

pm = PathManager("N1467345444") 


# # meta development

# In[3]:

import pkg_resources as pr


# In[4]:

with pr.resource_stream('pyciss', 'data/ring_resonances.csv') as f:
    resonances = pd.read_csv(f)
resonances.head()


# In[5]:

resonances.sort_values(by='Resonance (km)',ascending=False).head()


# In[6]:

from pyciss.meta import meta_df


# In[7]:

meta_df.head()


# In[8]:

meta_df.loc[pm._id]


# In[9]:

cube = RingCube(pm.cubepath)


# In[10]:

cube.meta.pixres


# In[11]:

get_ipython().magic('matplotlib nbagg')


# In[12]:

cube.imshow()


# In[13]:

cube.meta


# In[123]:

dics = []
for p in db_mapped_cubes():
    d = {}
    d['path'] = p
    cube = RingCube(p)
    d['meta_res'] = cube.meta_pixres
    d['label_res'] = cube.resolution_val
    d['time'] = cube.imagetime
    dics.append(d)


# In[124]:

df = pd.DataFrame(dics)


# In[125]:

df.head()


# In[126]:

df['id'] = df.path.map(lambda x: x.name.split('_')[0])


# In[127]:

df.set_index('time',inplace=True)


# In[31]:

df.set_index('id', inplace=True)


# In[128]:

df = df.sort_index()


# In[43]:

df.tail()


# In[45]:

df['ratio'] = df.meta_res / df.label_res


# In[130]:

df[df.label_res<5000].plot(style='*')


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


# In[54]:

get_ipython().magic('matplotlib nbagg')


# In[57]:

cube = io.RingCube(next(all_mapped_cubes))


# In[58]:

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



