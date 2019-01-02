__version__ = "0.11.0"

import logging

# this prevents messages sent to sys.stderr if no logging was configured on application-side
logging.getLogger("pyciss").addHandler(logging.NullHandler())

from .ringcube import RingCube
