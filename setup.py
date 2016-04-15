# import ez_setup
# ez_setup.use_setuptools()
from setuptools import setup, find_packages

pandas_version = '0.17.1'


setup(
    name="pyciss",
    version="0.3",
    packages=find_packages(),

    install_requires=['pandas>='+pandas_version, 'astropy'],

    package_data={
        'pyciss': ['data/*']
    },

    # metadata
    author="K.-Michael Aye",
    author_email="michael.aye@lasp.colorado.edu",
    description="Software for handling Cassini ISS data",
    license="BSD 2-clause",
    keywords="CASSINI ISS",
    url="http://lasp.colorado.edu",
)
