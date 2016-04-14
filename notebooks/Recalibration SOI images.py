
# coding: utf-8

# In[1]:

from pyciss import io, pipeline
from pysis import CubeFile
from pathlib import Path


# In[19]:

path = io.PathManager('N1591682340')


# In[20]:

path.basepath


# In[21]:

path.cal_cub


# In[22]:

cube = CubeFile(str(path.cal_cub))


# In[23]:

get_ipython().magic('matplotlib nbagg')


# In[24]:

low,high = np.percentile(cube.data, (0.5, 99.5))
data = cube.data[0].astype('float')
data[data<low]=np.nan
data[data>high] = np.nan


# In[25]:

plt.imshow(data, cmap='gray', aspect='')


# In[28]:

get_ipython().magic('pinfo plt.imshow')


# In[31]:

plt.figure()
plt.imshow(data[600:900, 0:400], cmap='gray', aspect='equal')


# In[7]:

pipeline.calibrate_ciss(path.raw_label)


# In[8]:

cube = io.RingCube(path.cubepath)


# In[10]:

get_ipython().magic('matplotlib nbagg')


# In[12]:

cube.imshow(set_extent=False)


# In[13]:

subimg = cube.img[340:400,400:1000]


# In[19]:

cube.imshow(data=subimg)


# In[18]:

plt.figure(figsize=(12,10))
plt.imshow(np.log(np.abs(np.fft.fftshift(np.fft.fft2(subimg)))), cmap='gray', aspect='auto')


# In[46]:

for p in io.dbpath.glob('*_?.IMG'):
    id = p.name.split('_')[0]
    pm = PathManager(id)
    if len(pm.raw_image) !=1:
        print(id)
        print(pm.raw_path)


# In[54]:

pm = PathManager('N1467345621')
pm.raw_label


# In[52]:

pm.raw_image.with_suffix('.LBL')


# In[55]:

map_cup = pipeline.calibrate_ciss(pm.raw_label)


# In[59]:

cube = io.RingCube(map_cup)


# In[57]:

get_ipython().magic('matplotlib nbagg')


# In[60]:

cube.imshow()


# In[61]:

meta = pd.read_csv('/Users/klay6683/Dropbox/DDocuments/UVIS/straws/coiss_ahires.015.list.txt',
                   header=None, delim_whitespace=True)

meta = meta.rename(columns={0:'id',1:'pixres', 14:'lit_status'})


# In[66]:

def recalibrate(id):
    pm = PathManager(id)
    map_cube = pipeline.calibrate_ciss(pm.raw_label)
    cube = io.RingCube(map_cube)
    cube.imshow()


# In[71]:

recalibrate('N1467347249')


# In[ ]:



