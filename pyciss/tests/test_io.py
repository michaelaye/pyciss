
# coding: utf-8

# In[1]:

# setup
from pyciss import io, ringcube
from pyciss.opusapi import OPUS
import tempfile
from pathlib import Path
tmpdir = tempfile.TemporaryDirectory()
opus = OPUS()
img_id = 'N1695760475'
opus.query_image_id(img_id)
opus.download_results(savedir = tmpdir.name)


# In[2]:

# test_PathManager
pathmanager = io.PathManager(img_id, savedir=tmpdir.name)
assert pathmanager.raw_image == Path(tmpdir.name) / img_id / (img_id+'_1.IMG')
assert pathmanager.cubepath == Path(tmpdir.name) / img_id / (img_id+'_1.cal.dst.map.cub')

