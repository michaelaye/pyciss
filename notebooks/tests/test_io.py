
# coding: utf-8

# In[ ]:

# setup
from pyciss import io, ringcube
from pyciss.opusapi import OPUS
import tempfile
from pathlib import Path
tmpdir = tempfile.TemporaryDirectory()
opus = OPUS()
opus.query_image_id('N1695760475_1')
opus.download_results(savedir = tmpdir.name)


# In[ ]:

# test_image_time
import datetime as dt
pathmanager = io.PathManager('N1467345444', savedir=tmpdir.name)
cube = ringcube.RingCube(pathmanager.cal_cub)
assert cube.imagetime == dt.datetime(2004, 7, 1, 3, 33, 9, 285000)

