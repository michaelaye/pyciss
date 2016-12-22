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
