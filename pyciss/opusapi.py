"""This module is making use of the
`OPUS API <https://pds-rings-tools.seti.org/opus/api/>`_ to create web requests
for OPUS data, metadata, and preview images.
"""
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import unquote, urlretrieve

import pandas as pd
import requests
from IPython.display import HTML, display

from . import io

base_url = "https://tools.pds-rings.seti.org/opus/api"
metadata_url = base_url + "/metadata"
image_url = base_url + "/image/"

dic = {"raw_data": "coiss-raw", "calibrated_data": "coiss-calib"}


class MetaData(object):
    """Receive OPUS Metadata for ISS img_id.

    Parameters
    ----------
    img_id : str
        In the form of {'N','W'}0123456789, the image id used in science publications

    """

    attr_dic = {
        "image": "Image Constraints",
        "wavelength": "Wavelength Constraints",
        "surface_geom": "Saturn Surface Geometry",
        "mission": "Cassini Mission Constraints",
        "ring_geom": "Ring Geometry Constraints",
        "general": "General Constraints",
        "iss": "Cassini ISS Constraints",
    }

    def __init__(self, img_id, query=None):
        self.img_id = img_id
        urlname = "S_IMG_CO_ISS_{}_{}.json".format(img_id[1:], img_id[0])
        fullurl = "{}/{}".format(metadata_url, urlname)
        print("Requesting", fullurl)
        if query is not None:
            query = unquote(urlencode(query))
            self.r = requests.get(fullurl, params=query).json()
        else:
            self.r = requests.get(fullurl).json()

        # setting attributes to access data quicker:
        for key, val in self.attr_dic:
            setattr(self, key, self.r[val])

    # this property access the
    @property
    def target_name(self):
        """str: Intended target name for the current ISS observation"""
        return self.mission["cassini_target_name"]


def _get_dataframe_from_meta_dic(meta, attr_name):
    d = getattr(meta, attr_name)
    df = pd.DataFrame({k: [v] for (k, v) in d.items()})
    df.index = [meta.img_id]
    return df


class OPUSImageURL(object):

    """Manage URLS from the OPUS response."""

    def __init__(self, jsonlist):
        self.jsonlist = jsonlist
        for item in jsonlist:
            parsed = urlparse(item)
            if "//" in parsed.path:
                continue
            if item.upper().endswith(".LBL"):
                self.label_url = item
            elif item.upper().endswith(".IMG"):
                self.image_url = item

    def __repr__(self):
        s = "Label:\n{}\nImage:\n{}".format(self.label_url, self.image_url)
        return s


class OPUSObsID(object):

    """Manage observation IDs from OPUS responses."""

    def __init__(self, obsid_data):
        self.idname = obsid_data[0]
        self.raw = OPUSImageURL(obsid_data[1][dic["raw_data"]])
        # the images have an iteration number. I'm fishing it out here:
        self.number = self.raw.image_url.split("_")[-1][0]
        try:
            self.calib = OPUSImageURL(obsid_data[1][dic["calibrated_data"]])
        except KeyError:
            self.calib = None

    def _get_img_url(self, size):
        base = self.raw.label_url[:-4].replace("volumes", "browse")
        return "{}_{}.jpg".format(base, size)

    @property
    def raw_urls(self):
        return [self.raw.image_url, self.raw.label_url]

    @property
    def calib_urls(self):
        return [self.calib.image_url, self.calib.label_url]

    @property
    def all_urls(self):
        return self.raw_urls + self.calib_urls

    @property
    def img_id(self):
        """Convert OPUS ObsID into the more known image_id."""
        tokens = self.idname.split("-")
        return tokens[-1]

    @property
    def small_img_url(self):
        return self._get_img_url("small")

    @property
    def medium_img_url(self):
        return self._get_img_url("med")

    @property
    def thumb_img_url(self):
        return self._get_img_url("thumb")

    @property
    def full_img_url(self):
        return self._get_img_url("full")

    def get_meta_data(self):
        return MetaData(self.img_id)

    def __repr__(self):
        s = "Raw:\n{}\nCalibrated:\n{}".format(self.raw, self.calib)
        return s


class OPUS(object):

    """Manage OPUS API requests.


    """

    def __init__(self, silent=False):
        self.silent = silent

    def query_image_id(self, image_id):
        """Query OPUS via the image_id.

        This is a query using the 'primaryfilespec' field of the OPUS database.
        It returns a list of URLS into the `obsids` attribute.

        This example queries for an image of Titan:

        >>> opus = opusapi.OPUS()
        >>> opus.query_image_id('N1695760475_1')

        After this, one can call `download_results()` to retrieve the found
        data into the standard locations into the database_path as defined in
        `.pyciss.yaml` (the config file),
        """
        myquery = {"primaryfilespec": image_id}
        self.create_files_request(myquery, fmt="json")
        self.unpack_json_response()
        return self.obsids

    def get_metadata(self, obsid, fmt="html", get_response=False):
        return MetaData(obsid.img_id)

    def create_request_with_query(self, kind, query, size="thumb", fmt="json"):
        """api/data.[fmt], api/images/[size].[fmt] api/files.[fmt]

        kind = ['data', 'images', 'files']


        """
        if kind == "data" or kind == "files":
            url = "{}/{}.{}".format(base_url, kind, fmt)
        elif kind == "images":
            url = "{}/images/{}.{}".format(base_url, size, fmt)
        self.url = url
        self.r = requests.get(url, params=unquote(urlencode(query)))

    def create_files_request(self, query, fmt="json"):
        self.create_request_with_query("files", query, fmt=fmt)

    def create_images_request(self, query, size="thumb", fmt="html"):
        self.create_request_with_query("images", query, size=size, fmt=fmt)

    def get_volume_id(self, ring_obsid):
        url = "{}/{}.json".format(metadata_url, ring_obsid)
        query = {"cols": "volumeidlist"}
        r = requests.get(url, params=unquote(urlencode(query)))
        return r.json()[0]["volume_id_list"]

    # def create_data_request(self, query, fmt='json'):
    #     myquery = query.copy()
    #     myquery.update(query)
    #     self.create_request_with_query('data', myquery, fmt=fmt)

    @property
    def response(self):
        return self.r.json()["data"]

    def unpack_json_response(self):
        if self.r.status_code == 500:
            if not self.silent:
                print("No data found.")
            self.obsids = []
            return
        obsids = []
        for obsid_data in self.response.items():
            obsids.append(OPUSObsID(obsid_data))
        self.obsids = obsids
        if not self.silent:
            print("Found {} obsids.".format(len(obsids)))
            if len(obsids) == 1000:
                print(
                    "List is 1000 entries long, which is the pre-set limit, hence"
                    " the real number of results might be longe."
                )

    def get_radial_res_query(self, res1, res2):
        myquery = dict(
            target="S+RINGS",
            instrumentid="Cassini+ISS",
            projectedradialresolution1=res1,
            projectedradialresolution2=res2,
            limit=1000,
        )
        return myquery

    def _get_time_query(self, t1, t2):
        myquery = dict(instrumentid="Cassini+ISS", timesec1=t1, timesec2=t2)
        return myquery

    def get_between_times(self, t1, t2, target=None):
        """
        Query for OPUS data between times t1 and t2.

        Parameters
        ----------
        t1, t2 : datetime.datetime, strings
            Start and end time for the query. If type is datetime, will be
            converted to isoformat string. If type is string already, it needs
            to be in an accepted international format for time strings.
        target : str
            Potential target for the observation query. Most likely will reduce
            the amount of data matching the query a lot.

        Returns
        -------
        None, but set's state of the object to have new query results stored
        in self.obsids.
        """
        try:
            # checking if times have isoformat() method (datetimes have)
            t1 = t1.isoformat()
            t2 = t2.isoformat()
        except AttributeError:
            # if not, should already be a string, so do nothing.
            pass
        myquery = self._get_time_query(t1, t2)
        if target is not None:
            myquery["target"] = target
        self.create_files_request(myquery, fmt="json")
        self.unpack_json_response()

    def get_between_resolutions(self, res1="", res2="0.5"):
        myquery = self.get_radial_res_query(res1, res2)
        self.create_files_request(myquery, fmt="json")
        self.unpack_json_response()

    def show_images(self, size="small"):
        """Shows preview images using the Jupyter notebook HTML display.

        Parameters
        ==========
        size : {'small', 'med', 'thumb', 'full'}
            Determines the size of the preview image to be shown.
        """
        d = dict(small=256, med=512, thumb=100, full=1024)
        try:
            width = d[size]
        except KeyError:
            print("Allowed keys:", d.keys())
            return
        img_urls = [i._get_img_url(size) for i in self.obsids]
        imagesList = "".join(
            [
                "<img style='width: {0}px; margin: 0px; float: "
                "left; border: 1px solid black;' "
                "src='{1}' />".format(width, s)
                for s in img_urls
            ]
        )
        display(HTML(imagesList))

    def download_results(self, savedir=None, raw=True, calib=False, index=None):
        """Download the previously found and stored Opus obsids.

        Parameters
        ==========
        savedir: str or pathlib.Path, optional
            If the database root folder as defined by the config.ini should not be used,
            provide a different savedir here. It will be handed to PathManager.
        """
        obsids = self.obsids if index is None else [self.obsids[index]]
        for obsid in obsids:
            pm = io.PathManager(obsid.img_id, savedir=savedir)
            pm.basepath.mkdir(exist_ok=True)
            to_download = []
            if raw is True:
                to_download.extend(obsid.raw_urls)
            if calib is True:
                to_download.extend(obsid.calib_urls)
            for url in to_download:
                basename = Path(url).name
                print("Downloading", basename)
                store_path = str(pm.basepath / basename)
                try:
                    urlretrieve(url, store_path)
                except Exception as e:
                    urlretrieve(url.replace("https", "http"), store_path)
            return str(pm.basepath)

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
