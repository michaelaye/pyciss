descr = """pyciss

Toolkit for handling image data of Cassini's Imaging Science Subsystem camera.

Please refer to the online documentation at
http://pyciss.readthedocs.org
"""

DISTNAME = 'pyciss'
DESCRIPTION = "Software for handling Cassini ISS data"
LONG_DESCRIPTION = descr
AUTHOR = "K.-Michael Aye"
AUTHOR_EMAIL = "michael.aye@lasp.colorado.edu"
MAINTAINER_EMAIL = AUTHOR_EMAIL
URL = "https://github.com/michaelaye/pyciss"
LICENSE = "ISC"
KEYWORDS = ['CASSINI', 'science', 'saturn', 'imaging']
DOWNLOAD_URL = "https://github.com/michaelaye/pyciss"

from setuptools import setup, find_packages

pandas_version = '0.17.1'


setup(
    name=DISTNAME,
    version="0.3",
    packages=find_packages(),

    install_requires=['pandas>='+pandas_version, 'astropy'],

    package_data={
        'pyciss': ['data/*', 'config.ini']
    },

    # metadata
    author=AUTHOR,
    maintainer=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    keywords="CASSINI ISS",
    url="http://lasp.colorado.edu",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
