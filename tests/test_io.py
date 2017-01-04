import configparser
from pathlib import Path

import pytest

from pyciss import io


@pytest.fixture(scope='module')
def config():
    d = configparser.ConfigParser()
    d['test'] = {}
    d['test']['path'] = '/test/path'
    return d


@pytest.fixture()
def configpath(tmpdir):
    p = tmpdir / 'test.ini'
    return p


def mockreturn():
    return Path('/abc')


def test_get_oldconfigpath(monkeypatch):
    monkeypatch.setattr(Path, 'home', mockreturn)
    x = io.get_oldconfigpath()
    assert x == Path('/abc/.pyciss.yaml')


def test_get_configpath(monkeypatch):
    monkeypatch.setattr(Path, 'home', mockreturn)
    x = io.get_configpath()
    assert x == Path('/abc/.pyciss.ini')


def test_get_config_not_found(monkeypatch):
    "will raise because no config is found at patched path."
    monkeypatch.setattr(Path, 'home', mockreturn)
    with pytest.raises(IOError):
        io.get_config()


def test_get_config_found(monkeypatch, tmpdir, config, configpath):
    p = configpath

    def mockreturn():
        return Path(str(p))
    monkeypatch.setattr(io, 'get_configpath', mockreturn)
    with open(str(p), 'w') as f:
        config.write(f)
    new = io.get_config()
    assert new.sections() == config.sections()


def test_set_database_path_not_found(monkeypatch, configpath):
    def mockreturn():
        return Path(str(configpath))
    monkeypatch.setattr(io, 'get_configpath', mockreturn)
    io.set_database_path('/test/path')
    config = configparser.ConfigParser()
    config.read(str(configpath))
    assert config['pyciss_db']['path'] == '/test/path'


class TestPathManager:
    def mockdbpath(self):
        return Path('/abc/db')

    @pytest.fixture
    def dbroot(self, monkeypatch):
        monkeypatch.setattr(io, 'get_db_root', self.mockdbpath)

    @pytest.fixture
    def pm(self, dbroot):
        return io.PathManager('N1234')

    def test_init_with_full_path(self, dbroot):
        pm = io.PathManager('/def/N1234_1.IMG')
        assert pm._id == 'N1234'

    def test_dbroot(self, pm):
        assert pm.dbroot == Path('/abc/db')

    def test_with_relative_path(self, dbroot):
        pm = io.PathManager('0123456789ABCD')
        assert pm._id == '0123456789A'

    def test_basepath(self, pm):
        assert pm.basepath == Path('/abc/db/N1234')

    def test_version(self, dbroot):
        pm = io.PathManager('N1234567890_1')
        assert pm.version == '1'

    def test_cubepath(self, pm):
        assert isinstance(pm.cubepath, Path)
        # note version 0 string!
        assert str(pm.cubepath) == '/abc/db/N1234/N1234_0.cal.dst.map.cub'

    def test_cal_cub(self, pm):
        assert str(pm.cal_cub) == '/abc/db/N1234/N1234_0.cal.cub'

    def test_dst_cub(self, pm):
        assert str(pm.dst_cub) == '/abc/db/N1234/N1234_0.cal.dst.cub'

    def test_raw_cub(self, pm):
        assert str(pm.raw_cub) == '/abc/db/N1234/N1234_0.cub'

    ###
    # continue here with other keys of the `d` dictionary
    # in PathManager
    ###
