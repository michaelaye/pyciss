import multiprocessing
import signal
import logging
import subprocess
import time
from ipyparallel import Client

from . import io, opusapi, pipeline

logger = logging.getLogger(__name__)


def download_file_id(file_id):
    logger.debug("Downloading file id %s", file_id)
    opus = opusapi.OPUS()
    opus.query_image_id(file_id)
    basepath = opus.download_results()
    print("Downloaded images into {}".format(basepath))


def signal_handler(signal, frame):
    print("shutting down cluster")
    subprocess.Popen(["ipcluster", "stop", "--quiet"])


def setup_cluster(n_cores=None):
    if n_cores is None:
        n_cores = multiprocessing.cpu_count() // 2

    signal.signal(signal.SIGINT, signal_handler)
    subprocess.Popen(["ipcluster",
                      "start",
                      "--n=" + str(n_cores),
                      "--daemonize",
                      "--quiet"])
    time.sleep(5)


def download_and_calibrate_parallel(list_of_ids, n=None):
    """Download and calibrate in parallel.

    Parameters
    ----------
    list_of_ids : list, optional
        container with img_ids to process
    n : int
        Number of cores for the parallel processing. Default: n_cores_system//2
    """
    setup_cluster(n_cores=n)
    c = Client()
    lbview = c.load_balanced_view()
    lbview.map_async(download_and_calibrate, list_of_ids)
    subprocess.Popen(["ipcluster", "stop", "--quiet"])


def download_and_calibrate(img_id=None, overwrite=False, **kwargs):
    """Download and calibrate one or more image ids, in parallel.

    Parameters
    ----------
    img_id : str or io.PathManager, optional
        If more than one item is in img_id, a parallel process is started
    overwrite: bool, optional
        If the pm.cubepath exists, this switch controls if it is being overwritten.
        Default: False
    """
    if isinstance(img_id, io.PathManager):
        pm = img_id
    else:
        # get a PathManager object that knows where your data is or should be
        logger.debug('Creating Pathmanager object')
        pm = io.PathManager(img_id)

    # if pm.raw_image is already there, skip downloading.
    if not pm.raw_image.exists() or overwrite is True:
        logger.debug("Downloading file", pm.img_id)
        download_file_id(pm.img_id)

    # start the calibration pipeline.
    # if cube file exists skip calibration if not overwrite
    if pm.cubepath.exists():
        if overwrite is True:
            ret = pipeline.calibrate_ciss(pm, **kwargs)
        else:
            logger.warning("Cube exists but overwrite is not allowed.")
            return
    else:
        logger.info("Cubefile ")
        ret = pipeline.calibrate_ciss(pm, **kwargs)
    return ret
