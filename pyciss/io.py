import os
from pysis import CubeFile

HOME = os.environ['HOME']

dataroot = os.path.join(HOME, 'data/ciss')


class RingCube(CubeFile):

    @property
    def mapping_label(self):
        return self.label['IsisCube']['Mapping']

    @property
    def minrad(self):
        return self.mapping_label['MinimumRingRadius']

    @property
    def maxrad(self):
        return self.mapping_label['MaximumRingRadius']

    @property
    def minlon(self):
        return self.mapping_label['MinimumRingLongitude']

    @property
    def maxlon(self):
        return self.mapping_label['MaximumRingLongitude']
