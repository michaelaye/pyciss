
# coding: utf-8

# In[1]:

# setup
from pyciss import opusapi
from pyciss.io import PathManager
from pathlib import Path
import tempfile
tmpdir = tempfile.TemporaryDirectory()

# setup OPUS object to be used for the tests.
# The query will retrieve URLS for each found object into
# the `obsids` attribute of the OPUS object.
opus = opusapi.OPUS()
opus.query_image_id('N1695760475')


# In[2]:

# test_query_results
baseurl = 'http://pds-rings.seti.org/volumes/COISS_2xxx/COISS_2069/data/'
res = baseurl + '1695427520_1695761375/N1695760475_1.LBL'
assert opus.obsids[0].raw.label_url == res


# In[3]:

# test_download_results
opus.download_results(savedir=tmpdir.name)
assert (Path(tmpdir.name) / 'N1695760475' / 'N1695760475_1.IMG').exists()
assert (Path(tmpdir.name) / 'N1695760475' / 'N1695760475_1.LBL').exists()


# In[4]:

# test_download_previews
opus.download_previews(savedir=tmpdir.name)
assert (Path(tmpdir.name) / 'N1695760475' / 'N1695760475_1_med.jpg').exists()


# In[5]:

# test_get_metadata
meta = opus.get_metadata(opus.obsids[0])
assert meta.image['duration'] == 38.0
assert meta.surface_geom['target_name'] == 'SATURN'
assert meta.general['declination1'] == 3.556135
assert meta.iss['GAIN_MODE_ID'] == '29 ELECTRONS PER DN'
assert meta.surface['center_phase_angle'] == 63.708


# In[6]:

# test_get_between_times_strings
opus.get_between_times('2005-10-10:00:00:00', '2005-10-11:00:00:00')
# this should find 7 items
assert len(opus.obsids) == 7


# In[7]:

# test_get_between_times_datetimes
import datetime as dt
t1 = dt.datetime(2005, 10, 9)
t2 = dt.datetime(2005, 10, 10)
opus.get_between_times(t1, t2)
assert len(opus.obsids) == 12


# In[8]:

# test_get_radial_res_query
d = opus.get_radial_res_query(0.1, 0.2)
assert isinstance(d, dict)
assert d['instrumentid'] == 'Cassini+ISS'
assert d['projectedradialresolution1'] == 0.1
assert d['projectedradialresolution2'] == 0.2
assert d['target'] == 'S+RINGS'


# In[9]:

# test_get_between_resolutions
opus.get_between_resolutions(0.1,0.5)
# should find 89 items
assert len(opus.obsids) == 89


# In[10]:

# cleanup
tmpdir.cleanup()

