
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


# In[14]:

dics = []
for p in db_mapped_cubes():
    d = {}
    d['path'] = p
    cube = RingCube(p)
    d['meta_res'] = cube.meta_pixres
    d['label_res'] = cube.resolution_val
    dics.append(d)


# In[15]:

df = pd.DataFrame(dics)


# In[16]:

df.head()


# In[17]:

df.plot(style='*-')


# In[18]:

cube = RingCube(df[df.label_res>5000].path.values[0])


# In[19]:

cube.imshow()


# In[21]:

cube.pm.id


# In[22]:

cube.get_opus_meta_data()


# In[26]:

cube.opusmeta.ring_geom


# In[ ]:



