import os
import gdal
from pysis.isis import getkey
import numpy as np
from urllib.request import unquote
from urllib.parse import urlparse, urlencode
import requests


HOME = os.environ['HOME']

dataroot = os.path.join(HOME, 'data/ciss')


class RingCube:
    def __init__(self, cubename):
        self.cubename = cubename
        self.ds = gdal.Open(cubename)
        self.xsize = self.ds.RasterXSize
        self.ysize = self.ds.RasterYSize

    def get_mapping_value(self, keyword):
        val = getkey.check_output(from_=self.cubename,
                                  keyword=keyword,
                                  grpname='mapping')
        return val.strip()

    @property
    def shape(self):
        return (self.ysize, self.xsize)

    @property
    def minrad(self):
        return float(self.get_mapping_value('minimumringradius'))

    @property
    def maxrad(self):
        return float(self.get_mapping_value('maximumringradius'))

    @property
    def minlon(self):
        return float(self.get_mapping_value('minimumringlongitude'))

    @property
    def maxlon(self):
        return float(self.get_mapping_value('maximumringlongitude'))

    def get_data(self):
        data = self.ds.ReadAsArray()
        data[data < 0] = np.nan
        return data


class OPUSImage(object):
    """Manage URLS from the OPUS response."""
    def __init__(self, jsonlist):
        self.jsonlist = jsonlist
        for item in jsonlist:
            parsed = urlparse(item)
            if '//' in parsed.path:
                continue
            if item.upper().endswith(".LBL"):
                self.label_url = item
            elif item.upper().endswith('.IMG'):
                self.image_url = item

    def __repr__(self):
        s = "Label:\n{}\nImage:\n{}".format(self.label_url,
                                            self.image_url)
        return s


class OPUSObsID(object):
    """Manage observation IDs from OPUS responses."""
    def __init__(self, obsid_data):
        self.idname = obsid_data[0]
        self.raw = OPUSImage(obsid_data[1]['RAW_IMAGE'])
        self.calib = OPUSImage(obsid_data[1]['CALIBRATED'])

    def __repr__(self):
        s = "Raw:\n{}\nCalibrated:\n{}".format(self.raw, self.calib)
        return s


class OPUS(object):
    """Manage OPUS API requests."""
    base_url = 'http://pds-rings-tools.seti.org/opus/api'
    files_url = base_url + '/files.json'
    payload = {'target': 'S+RINGS',
               'instrumentid': 'Cassini+ISS'}

    def create_request(self, payload):
        r = requests.get(self.files_url,
                         params=unquote(urlencode(payload)))
        return r

    def send_request(self, payload):
        r = self.create_request(payload)
        response = r.json()['data']
        obsids = []
        for obsid_data in response.items():
            obsids.append(OPUSObsID(obsid_data))
        self.obsids = obsids

    def get_between_resolutions(self, res1='', res2='0.5'):
        payload = self.payload.copy()
        payload['projectedradialresolution1'] = res1
        payload['projectedradialresolution2'] = res2
        self.send_request(payload)

    def get_filename(self, fname):
        payload = {'primaryfilespec': fname}
        self.send_request(payload)
        return self.obsids
