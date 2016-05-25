from __future__ import division, print_function

import requests
from IPython.display import HTML
from pathlib import Path

from . import io

try:
    from urllib.request import unquote, urlretrieve
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urllib2 import unquote
    from urlparse import urlparse
    from urllib import urlretrieve, urlencode

base_url = 'http://tools.pds-rings.seti.org/opus/api'
metadata_url = base_url + '/metadata/'
image_url = base_url + '/image/'


class MetaData(object):

    def __init__(self, img_id):
        urlname = "S_IMG_CO_ISS_{}_{}.json".format(img_id[1:], img_id[0])
        fullurl = metadata_url + urlname
        print("Requesting", fullurl)
        self.r = requests.get(fullurl).json()

    @property
    def image(self):
        return self.r['Image Constraints']

    @property
    def wavelength(self):
        return self.r['Wavelength Constraints']

    @property
    def surface_geom(self):
        return self.r['Cassini Surface Geometry']

    @property
    def mission(self):
        return self.r['Cassini Mission Constraints']

    @property
    def ring_geom(self):
        return self.r['Ring Geometry Constraints']

    @property
    def general(self):
        return self.r['General Constraints']

    @property
    def iss(self):
        return self.r['Cassini ISS Constraints']

    @property
    def surface(self):
        return self.r['Saturn Surface Geometry']


class OPUSImageURL(object):

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
        self.raw = OPUSImageURL(obsid_data[1]['RAW_IMAGE'])
        # the images have an iteration number. I'm fishing it out here:
        self.number = self.raw.image_url.split('_')[-1][0]
        try:
            self.calib = OPUSImageURL(obsid_data[1]['CALIBRATED'])
        except KeyError:
            self.calib = None

    def get_img_url(self, size):
        base = self.raw.label_url[:-4].replace('volumes', 'browse')
        return "{}_{}.jpg".format(base, size)

    @property
    def img_id(self):
        """Convert OPUS ObsID into the more known image_id."""
        tokens = self.idname.split('_')
        return ''.join(tokens[-2:][::-1])

    @property
    def small_img_url(self):
        return self.get_img_url('small')

    @property
    def medium_img_url(self):
        return self.get_img_url('med')

    @property
    def thumb_img_url(self):
        return self.get_img_url('thumb')

    @property
    def full_img_url(self):
        return self.get_img_url('full')

    def __repr__(self):
        s = "Raw:\n{}\nCalibrated:\n{}".format(self.raw, self.calib)
        return s


class OPUS(object):

    """Manage OPUS API requests.


    """

    def query_image_id(self, image_id):
        """Query OPUS via the image_id.

        This is a query using the 'primaryfilespec' field of the OPUS database.
        It returns a list of URLS into the `obsids` attribute.

        This example queries for an image of Titan:

        >>> opus = opusapi.OPUS()
        >>> opus.query_image_id('N1695760475_1')

        After this, one can call `download_results()` to retrieve the found
        data into the standard locations into the database_path as defined in
        config.ini.
        """
        myquery = {'primaryfilespec': image_id}
        self.create_files_request(myquery, fmt='json')
        self.unpack_json_response()
        return self.obsids

    def get_metadata(self, obsid, fmt='html', get_response=False):
        return MetaData(obsid.img_id)

    def create_request_with_query(self, kind, query, size='thumb', fmt='json'):
        """api/data.[fmt], api/images/[size].[fmt] api/files.[fmt]

        kind = ['data', 'images', 'files']


        """
        if kind == 'data' or kind == 'files':
            url = "{}/{}.{}".format(base_url, kind, fmt)
        elif kind == 'images':
            url = "{}/images/{}.{}".format(base_url, size, fmt)
        self.r = requests.get(url,
                              params=unquote(urlencode(query)))

    def create_files_request(self, query, fmt='json'):
        self.create_request_with_query('files', query, fmt=fmt)

    def create_images_request(self, query, size='thumb', fmt='html'):
        self.create_request_with_query('images', query, size=size, fmt=fmt)

    # def create_data_request(self, query, fmt='json'):
    #     myquery = query.copy()
    #     myquery.update(query)
    #     self.create_request_with_query('data', myquery, fmt=fmt)

    def unpack_json_response(self):
        response = self.r.json()['data']
        obsids = []
        for obsid_data in response.items():
            obsids.append(OPUSObsID(obsid_data))
        self.obsids = obsids
        print('Found {} obsids.'.format(len(obsids)))

    def get_radial_res_query(self, res1, res2):
        myquery = dict(target='S+RINGS', instrumentid='Cassini+ISS',
                       projectedradialresolution1=res1,
                       projectedradialresolution2=res2)
        return myquery

    def get_time_query(self, t1, t2):
        myquery = dict(instrumentid='Cassini+ISS',
                       timesec1=t1, timesec2=t2)
        return myquery

    def get_between_times(self, t1, t2):
        try:
            t1 = t1.isoformat()
            t2 = t2.isoformat()
        except AttributeError:
            pass
        myquery = self.get_time_query(t1, t2)
        self.create_files_request(myquery, fmt='json')
        self.unpack_json_response()

    def get_between_resolutions(self, res1='', res2='0.5'):
        myquery = self.get_radial_res_query(res1, res2)
        self.create_files_request(myquery, fmt='json')
        self.unpack_json_response()

    def show_images(self, size='small'):
        """Shows preview images using the Jupyter notebook HTML display.

        Parameters
        ==========
        size : {'small', 'med', 'thumb', 'full'}
            Determines the size of the preview image to be shown.
        """
        d = dict(small=256, med=512, thumb=100, full=1024)
        width = d[size]
        img_urls = [i.get_img_url(size) for i in self.obsids]
        imagesList = ''.join(["<img style='width: {0}px; margin: 0px; float: "
                              "left; border: 1px solid black;' "
                              "src='{1}' />"
                              .format(width, s) for s in img_urls])
        return HTML(imagesList)

    def download_results(self, savedir=None):
        """Download the previously found and stored Opus obsids.

        Parameters
        ==========
        savedir: str or pathlib.Path, optional
            If the database root folder as defined by the config.ini should not be used,
            provide a different savedir here. It will be handed to PathManager.
        """
        for obsid in self.obsids:
            pm = io.PathManager(obsid.img_id, savedir=savedir)
            pm.basepath.mkdir(exist_ok=True)
            for url in [obsid.raw.image_url, obsid.raw.label_url]:
                basename = Path(url).name
                print("Downloading", basename)
                urlretrieve(url, str(pm.basepath / basename))

    def download_previews(self, savedir=None):
        """Download preview files for the previously found and stored Opus obsids.

        Parameters
        ==========
        savedir: str or pathlib.Path, optional
            If the database root folder as defined by the config.ini should not be used,
            provide a different savedir here. It will be handed to PathManager.
        """
        for obsid in self.obsids:
            pm = io.PathManager(obsid.img_id, savedir=savedir)
            pm.basepath.mkdir(exist_ok=True)
            basename = Path(obsid.medium_img_url).name
            print("Downloading", basename)
            urlretrieve(obsid.medium_img_url, str(pm.basepath / basename))
