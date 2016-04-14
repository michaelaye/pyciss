
# coding: utf-8

# In[1]:

from pyciss.io import RingCube, PathManager


# In[2]:

pm = PathManager("N1591682340") 


# In[3]:

cube = RingCube(pm.cal_cub)


# In[5]:

cube.is_lit


# In[14]:

from pyciss.meta import meta2500m as meta


# In[15]:

cube.meta.ring_geom


# In[16]:

meta[meta.id==cube.pm._id]


# In[ ]:



