"""collection of ring research related tools"""

from collections import namedtuple

import numpy as np
from astropy import units as u

RingSection = namedtuple("RingSection", "name rmin rmax")

D_ring = RingSection("D ring", 66_900*u.km, 74_510*u.km)
C_ring = RingSection("C ring", 74_658*u.km, 92_000*u.km)
B_ring = RingSection("B ring", 92_000*u.km, 117_580*u.km)
A_ring = RingSection("A ring", 122_170*u.km, 136_775*u.km)
CasDiv = RingSection("Cassini Division", 117_580*u.km, 122_170*u.km)
RocheDiv = RingSection("Roche Division", 136_775*u.km, 139_380*u.km)
JanEpi_ring = RingSection("Janus/Epimetheus ring", 149_000*u.km, 154_000*u.km)
E_ring = RingSection("E Ring", 180_000*u.km, 480_000*u.km)
