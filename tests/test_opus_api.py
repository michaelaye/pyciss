# coding: utf-8
import pytest
from pyciss import opusapi


@pytest.fixture
def opus_naked():
    return opusapi.OPUS()


@pytest.fixture
def opus(opus_naked):
    opus_naked.query_image_id('N1695760475')
    return opus_naked


def test_query(opus_naked):
    import pyciss
    opus_naked.query_image_id('N1695760475')
    assert len(opus_naked.obsids) == 1
    assert type(opus_naked.obsids[0] is pyciss.opusapi.OPUSObsID)


def test_query_results(opus):
    baseurl = 'http://pds-rings.seti.org/volumes/COISS_2xxx/COISS_2069/data/'
    res = baseurl + '1695427520_1695761375/N1695760475_1.LBL'
    assert opus.obsids[0].raw.label_url == res


def test_download_results(opus, tmpdir):
    opus.download_results(savedir=str(tmpdir))
    assert (tmpdir / 'N1695760475' / 'N1695760475_1.IMG').exists()
    assert (tmpdir / 'N1695760475' / 'N1695760475_1.LBL').exists()


def test_download_previews(opus, tmpdir):
    opus.download_previews(savedir=str(tmpdir))
    assert (tmpdir / 'N1695760475' / 'N1695760475_1_med.jpg').exists()


def test_get_metadata(opus):
    meta = opus.get_metadata(opus.obsids[0])
    assert meta.image['duration'] == 38.0
    assert 'emission1' in meta.surface_geom
    assert meta.general['declination1'] == 3.556135
    assert meta.iss['GAIN_MODE_ID'] == '29 ELECTRONS PER DN'


def test_get_between_times_strings(opus):
    opus.get_between_times('2005-10-10:00:00:00', '2005-10-11:00:00:00')
    # this should find 7 items
    assert len(opus.obsids) == 7


def test_get_between_times_datetimes(opus):
    import datetime as dt
    t1 = dt.datetime(2005, 10, 9)
    t2 = dt.datetime(2005, 10, 10)
    opus.get_between_times(t1, t2)
    assert len(opus.obsids) == 12


def test_get_radial_res_query(opus):
    d = opus.get_radial_res_query(0.1, 0.2)
    assert isinstance(d, dict)
    assert d['instrumentid'] == 'Cassini+ISS'
    assert d['projectedradialresolution1'] == 0.1
    assert d['projectedradialresolution2'] == 0.2
    assert d['target'] == 'S+RINGS'


def test_get_between_resolutions(opus):
    opus.get_between_resolutions(0.1, 0.5)
    # should find 89 items
    assert len(opus.obsids) == 90
