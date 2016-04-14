
# coding: utf-8

# In[17]:

from pathlib import Path
import shutil
from pyciss import pipeline


# # Data on little USB plug

# In[2]:

root = Path("/Volumes/USB128GB/ciss/opus/")


# In[8]:

myiter = root.glob("**/*.png")


# In[9]:

for p in myiter:
    p.unlink()


# In[ ]:




# In[5]:

pipeline.calibrate_ciss(next(myiter))


# # OPUS API things

# In[38]:

from pyciss.opusapi import OPUS,MetaData


# In[19]:

op = OPUS()


# In[60]:

from urllib.request import unquote, urlretrieve
import requests


# In[61]:

http://pds-rings-tools.seti.org/opus/api/meta/range/endpoints/emission1.json?target=Saturn


# In[33]:

def get_meta_for_id(img_id):
    urlname = "S_IMG_CO_ISS_{}_{}.json".format(img_id[1:], img_id[0])
    urlbase = "http://pds-rings-tools.seti.org/opus/api/metadata/"
    r = requests.get(urlbase+urlname)
    return r.json()


# In[41]:

meta = MetaData('N1591682340')


# In[42]:

meta.image


# In[47]:

meta.ring_geom['emission1']


# In[44]:

from pyciss.meta import meta1500m


# In[46]:

meta1500m.head()


# In[ ]:

meta1500m


# In[52]:

some_lits = meta1500m[meta1500m.lit_status=='lit'].head(5)


# In[53]:

some_lits


# In[54]:

some_unlits = meta1500m[meta1500m.lit_status=='unlit'].head()


# In[55]:

f = lambda x: MetaData(x).ring_geom['emission1']


# In[56]:

some_lits['emission1'] = some_lits.id.map(f)


# In[57]:

some_unlits['emission1'] = some_unlits.id.map(f)


# In[58]:

some_lits.emission1


# In[59]:

some_unlits.emission1


# In[1]:

from pysis import CubeFile


# In[3]:

cube = CubeFile.open("/Users/klay6683/Dropbox/data/ciss/SOI/N1467345444_2.map.dst.cal.cub")


# In[ ]:



