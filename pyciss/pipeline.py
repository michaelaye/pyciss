""" Note that the calibration starts from the LBL files, not the IMG !!! """
from __future__ import division, print_function

import logging
import os
from pathlib import Path

from . import io

try:
    from pysis import IsisPool
    from pysis.exceptions import ProcessError
    from pysis.isis import (
        ciss2isis,
        cisscal,
        dstripe,
        editlab,
        getkey,
        isis2std,
        ringscam2map,
        spiceinit,
        fillgap,
    )
    from pysis.util import file_variations
except ImportError:
    print("Cannot load the ISIS system. pipeline module not functional.")
else:
    ISISDATA = Path(os.environ["ISIS3DATA"])


logger = logging.getLogger(__name__)


class Calibrator(object):
    """Calibrate raw Cassini ISS images using ISIS.

    ISIS is using an official released version the calibration routine `cisscal`
    that is being developed under IDL, but has been converted to C++ for ISIS.
    I am using the pipeline as described here:
    https://isis.astrogeology.usgs.gov/IsisWorkshop/index.php/Working_with_Cassini_ISS_Data
    It is customary to indicate the pipeline of ISIS apps that a file went through
    with a chain of extensions, e.g. '.cal.dst.map.cub', indicating calibration,
    destriping, and map projection.

    Parameters
    ----------
    img_name : io.PathManager, pathlib.Path, str
        Absolute path to image or io.PathManager object with raw_label attribute.
        If img_name has no attribute `raw_label`, I try to initialize a PathManager
        with `img_name` to see if I have received an image_id string here.
        Last thing I try is just a path.
    is_ring_data : bool
        Switch to tell the Calibrator if its dealing with ringdata.
        If True, it will check the label for the correct target (required for correct
        spiceinit and map projection) and will control spice
    do_map_project : bool
        Switch to control if map projection into ringplane shall occur
    final_resolution : int
        The map projection radial resolution value to achieve, in units meter per pixel.
        If not given, an automatic value is being calculated by the ISIS software.
        This often leads to higher res images than originally performed, using cubic spline
        interpolation.
        They look good, but one must be aware of this for interpretation.
        I usually take a median on all original resolutions
        of my dataset and set it to that value.

    """

    map_path = ISISDATA / "base/templates/maps/ringcylindrical.map"

    def __init__(
        self, img_name, is_ring_data=True, do_map_project=True, final_resolution=500
    ):
        self.img_name = self.parse_img_name(img_name)
        self.is_ring_data = is_ring_data
        self.do_map_project = do_map_project
        self.final_resolution = final_resolution

    def standard_calib(self):
        pm = self.pm  # save typing
        # import PDS into ISIS
        try:
            # use temp file here for fillgap to go to
            ciss2isis(from_=pm.raw_label, to="temp.cub")
        except ProcessError as e:
            print("At Calibrator.standard_calib()'s ciss2isis:")
            print("ERR:", e.stderr)
            print(f"Parameters:\n{pm.raw_label}\n{pm.raw_cub}")
            raise e
        else:
            logger.info("Import to ISIS done.")

        # fill Hrs pixels from bad importer
        fillgap(from_="temp.cub", to=pm.raw_cub, interp="akima")
        # check if label fits with data
        self.check_label()

        # initialize spice kernels into label
        self.spiceinit()

        # calibration, use I/F as units
        cisscal(from_=pm.raw_cub, to=pm.cal_cub, units="I/F")
        logger.info("cisscal done.")
        end = pm.cal_cub  # keep track of last produced path

        # destriping
        dstripe(from_=pm.cal_cub, to=pm.dst_cub, mode="horizontal")
        logger.info("Destriping done.")

        if self.do_map_project:
            # destriped
            self.map_project(pm.dst_cub, pm.cubepath)
            self.create_preview(pm.cubepath)
            # undestriped
            self.map_project(pm.cal_cub, pm.undestriped)
            self.create_preview(pm.undestriped)
        else:
            logger.warning(
                "Map projection was skipped.\n" "Set map_project to True if wanted."
            )

    def map_project(self, start, end):
        try:
            ringscam2map(
                from_=start,
                to=end,
                defaultrange="Camera",
                map=self.map_path,
                pixres="mpp",
                resolution=self.final_resolution,
            )
        except ProcessError as e:
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)

    def create_preview(self, end):
        # create tif quickview
        tifname = end.with_suffix(".tif")
        isis2std(from_=end, to=tifname, format="tiff")
        logger.info("Created tif product: %s", tifname)

    def spiceinit(self):
        """Perform either normal spiceinit or one for ringdata.

        Note how Python name-spacing can distinguish between the method
        and the function with the same name. `spiceinit` from the outer
        namespace is the one imported from pysis.
        """
        shape = "ringplane" if self.is_ring_data else None
        spiceinit(from_=self.pm.raw_cub, cksmithed="yes", spksmithed="yes", shape=shape)
        logger.info("spiceinit done.")

    def check_label(self):
        """ Check label for target and fix if necessary.

        Forcing the target name to Saturn here, because some observations of
        the rings have moons as a target, but then the standard map projection
        onto the Saturn ring plane fails.

        See also
        --------
        https://isis.astrogeology.usgs.gov/IsisSupport/index.php/topic,3922.0.html
        """
        if not self.is_ring_data:
            return
        targetname = getkey(
            from_=self.pm.raw_cub, grp="instrument", keyword="targetname"
        )

        if targetname.lower() != "saturn":
            editlab(
                from_=self.pm.raw_cub,
                options="modkey",
                keyword="TargetName",
                value="Saturn",
                grpname="Instrument",
            )

    def parse_img_name(self, img_name):
        # Check if img_name is maybe a PathManager object with a `raw_label` attribute:
        try:
            # if img_name is a PathManager:
            self.img_name = str(img_name.raw_label)
            self.pm = img_name
        except AttributeError:
            try:
                # if img_name is just the ID itself:
                self.pm = io.PathManager(img_name)
                self.img_name = str(self.pm.raw_label)
            except:
                # if it's actually the path:
                self.img_name = str(img_name)
                # PathManager can deal with absolute paths
                self.pm = io.PathManager(img_name)

    def remapping(self, output=None, resolution=500):
        input_ = self.pm.dst_cub if self.pm.dst_cub.exists() else self.pm.cal_cub
        if output is None:
            output = self.pm.cubepath
        elif not Path(output).is_absolute():
            output = input_.with_name(output)
        logger.info("Mapping %s to %s to resolution %i", input_, output, resolution)
        ringscam2map(
            from_=input_,
            to=output,
            map=self.map_path,
            pixres="mpp",
            defaultrange="Camera",
            resolution=resolution,
        )
        tifname = output.with_suffix(".tif")
        isis2std(from_=output, to=tifname, format="tiff")


def calibrate_many(images):
    images = [
        [img_name] + file_variations(img_name, [".cub", ".cal.cub", ".map.cal.cub"])
        for img_name in images
    ]

    with IsisPool() as isis_pool:
        for img_name, cub_name, cal_name, map_name in images:
            isis_pool.ciss2isis(from_=img_name, to=cub_name)

    return images
