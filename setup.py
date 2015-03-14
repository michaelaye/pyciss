# import ez_setup
# ez_setup.use_setuptools()
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

pandas_version = '0.15.1'

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v', '-m']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name = "PYCISS",
    version = "0.1beta",
    packages = find_packages(),

    # install_requires = ['pandas>='+pandas_version, 'astropy'],
    # tests_require = ['pytest'],

    cmdclass = {'test': PyTest},

    # entry_points={
    #     "console_scripts": [
    #         'scp_l1a = diviner.file_utils:scp_l1a_file'
    #         ]
    # },

    #metadata
    author = "K.-Michael Aye",
    author_email = "michael.aye@lasp.colorado.edu",
    description = "Software for handling Cassini ISS data",
    license = "BSD 2-clause",
    keywords = "CASSINI ISS",
    url = "http://lasp.colorado.edu",
)
