__version__ = "0.12.6"

import logging

# this prevents messages sent to sys.stderr if no logging was configured on application-side
logging.getLogger("pyciss").addHandler(logging.NullHandler())

from .ringcube import RingCube
