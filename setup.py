# import ez_setup
# ez_setup.use_setuptools()
from setuptools import setup, find_packages

pandas_version = '0.15.1'


setup(
    name="pyciss",
    version="0.3",
    packages=find_packages(),

    install_requires=['pandas>='+pandas_version, 'astropy'],

    # entry_points={
    #     "console_scripts": [
    #         'scp_l1a = diviner.file_utils:scp_l1a_file'
    #         ]
    # },

    # metadata
    author="K.-Michael Aye",
    author_email="michael.aye@lasp.colorado.edu",
    description="Software for handling Cassini ISS data",
    license="BSD 2-clause",
    keywords="CASSINI ISS",
    url="http://lasp.colorado.edu",
)
