pyciss
======

Python utilities to work with Cassini's ISS camera system

Fair use
--------
If you use this software, please consider citing it:

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.51899.svg
   :target: http://dx.doi.org/10.5281/zenodo.51899

Bibtex record::

    @misc{k_michael_aye_2016_51899,
      author       = {K.-Michael Aye},
      title        = {pyciss},
      version      = {v0.4.1},
      publisher    = {Zenodo},
      month        = may,
      year         = 2016,
      doi          = {10.5281/zenodo.51899},
      url          = {http://dx.doi.org/10.5281/zenodo.51899}
    }

Documentation
-------------

.. image:: https://readthedocs.org/projects/pyciss/badge/?version=latest
    :target: http://pyciss.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Homepage
--------

https://github.com/michaelaye/pyciss

Installation
------------

Several possibilities:

pypi
~~~~

:code:`pip install pyciss`

github
~~~~~~

* :code:`git clone https://github.com/michaelaye/pyciss.git` (without SSH keys)
* :code:`git clone git@github.com:michaelaye/pyciss.git` (with SSH keys)

followed by:
:code:`cd pyciss && pip install .`

Continuous Integration
----------------------

.. image:: https://travis-ci.org/michaelaye/pyciss.svg?branch=master
    :target: https://travis-ci.org/michaelaye/pyciss

Acknowledgements
----------------

* Miodrac Sremcevic for introducing me into some of the tricks of Saturn ring image analysis with Cassini ISS data and for producing a very nice resonance data file for the Saturn rings, here is one of his publications about it:

 * Sremčević, M., Stewart, G.R., Albers, N., Colwell, J.E., Esposito, L.W., 2008. Density Waves in Saturn's Rings: Non-linear Dispersion and Moon Libration Effects. American Astronomical Society 40, 24.03–.

* Morgan Rehnberg for providing me with Miodrag's data file and answering some of my newbie questions.
