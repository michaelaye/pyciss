__version__ = '0.8.2'

import logging

# this prevents messages sent to sys.stderr if no logging was configured on application-side
logging.getLogger('pyciss').addHandler(logging.NullHandler())
