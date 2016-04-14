
# coding: utf-8

# In[ ]:

cd /Volumes/Data/ciss/pdsrings-data-b-2016-01-07T17-33-51/


# In[ ]:

from pyciss import pipeline, io
from pathlib import Path
p = Path()


# In[ ]:

p


# In[ ]:

files = list(p.glob('*_1.LBL'))


# In[ ]:

files


# In[ ]:

from pyciss import pipeline


# In[ ]:

for f in files[1:]:
    pipeline.calibrate_ciss(f)


# In[ ]:

maps = list(p.glob('*map.*.cub'))
maps


# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

cube = io.RingCube(maps[3])
cube.imshow()


# In[ ]:

from skimage.exposure import adjust_sigmoid, rescale_intensity, equalize_adapthist


# In[ ]:

data = cube.data[0]


# In[ ]:

data[data<0] = 0


# In[ ]:

data.max()


# In[ ]:

data.min()


# In[ ]:

data.shape


# In[ ]:

out = rescale_intensity(data)


# In[ ]:

out.max()


# In[ ]:

out.min()


# In[ ]:

from scipy import constants


# In[ ]:

constants.astronomical_unit


# 05h 36m 12.8s[1

# In[ ]:

from astropy import units as u
from astropy.coordinates import SkyCoord


c = SkyCoord('05h36m12.8s', '-01d12m06.9089s', frame='icrs')
# >>> c = SkyCoord('00h42.5m', '+41d12m')
# >>> c = SkyCoord('00 42 30 +41 12 00', unit=(u.hourangle, u.deg))
# >>> c = SkyCoord('00:42.5 +41:12', unit=(u.hourangle, u.deg))
# >>> c


# In[ ]:

c


# In[ ]:

c.__dict__


# In[ ]:

c.fk4


# In[ ]:

c.fk5


# In[ ]:

c.barycentrictrueecliptic


# In[ ]:

c.cartesian


# In[ ]:

c.default_representation


# In[ ]:

c.distance


# In[ ]:

c.frame


# In[ ]:

c.get_constellation()


# In[ ]:

c.itrs


# In[ ]:

c.pressure


# In[ ]:

c.z_sun


# In[ ]:




# In[ ]:

cube.imshow(data=out)


# In[ ]:

out2 = adjust_sigmoid(out)


# In[ ]:

equal = equalize_adapthist(out2)


# In[ ]:

cube.imshow(equal)


# In[ ]:

meta = pd.read_csv('/Users/klay6683/Dropbox/DDocuments/UVIS/straws/coiss_ahires.015.list.txt',
                   header=None, delim_whitespace=True)

meta = meta.rename(columns={0:'id',1:'pixres', 14:'lit_status'})


# In[ ]:

cube.filename


# In[ ]:

meta[meta.id=='N1467346211'].lit_status


# In[ ]:

meta[meta.id=='N1467346506'].lit_status


# In[ ]:

meta[meta.id=='N1467346447'].lit_status


# In[ ]:

meta.head()


# In[ ]:

meta.describe()


# In[ ]:

from pathlib import Path


# In[ ]:

soipath = Path("/Users/klay6683/Dropbox/data/ciss/SOI/")


# In[ ]:

for p in soipath.glob("*_2.png"):
    id = p.name.split('_')[0]
    print(meta[meta.id==id].lit_status.values)


# In[ ]:

meta[meta.id=='N1503242284'].lit_status


# In[ ]:



