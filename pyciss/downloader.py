from . import opusapi
from . import io
from . import pipeline


def download_file_id(file_id):
    opus = opusapi.OPUS()
    opus.query_image_id(file_id)
    basepath = opus.download_results()
    print("Downloaded images into {}".format(basepath))


def download_and_calibrate(img_id, overwrite=False, **kwargs):
    # get a PathManager object that knows where your data is or should be
    pm = io.PathManager(img_id)

    # if raw_image exists skip downloading
    # if query returned satisfying results.
    # Mostly will be 4 results, label + image for raw data, and label+image for calibrated image

    if not pm.raw_image.exists():
        download_file_id(img_id)

    # start the calibration pipeline.
    # if cube file exists skip calibration if not overwrite
    if not pm.cubepath.exists() or overwrite is True:
        pipeline.calibrate_ciss(pm, **kwargs)
