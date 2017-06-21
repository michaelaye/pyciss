from os import path

from setuptools import find_packages, setup

DISTNAME = 'pyciss'
DESCRIPTION = "Software for handling Cassini ISS data"
AUTHOR = "K.-Michael Aye"
AUTHOR_EMAIL = "michael.aye@lasp.colorado.edu"
MAINTAINER_EMAIL = AUTHOR_EMAIL
URL = "https://github.com/michaelaye/pyciss"
LICENSE = "ISC"
KEYWORDS = ['CASSINI', 'science', 'saturn', 'imaging']
DOWNLOAD_URL = "https://github.com/michaelaye/pyciss"

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=DISTNAME,
    version="0.9.1",
    packages=find_packages(),

    install_requires=['pandas', 'numpy', 'matplotlib', 'pysis', 'astropy'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    package_data={
        'pyciss': ['data/*']
    },

    # metadata
    author=AUTHOR,
    maintainer=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    keywords=KEYWORDS,
    url=URL,
    download_url=DOWNLOAD_URL,

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
