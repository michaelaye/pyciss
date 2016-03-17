
# coding: utf-8

# In[11]:

from pyciss import io
import datetime as dt


# In[12]:

# test_image_time
cube = io.RingCube("/Volumes/Data/ciss/opus/N1467345444/N1467345444_2.cal.cub")
assert cube.imagetime == dt.datetime(2004, 7, 1, 3, 33, 9, 285000)


# In[ ]:

# test_survival
assert cube.imagetime == dt.datetime(2004, 7, 1, 3, 33, 9, 285000)

