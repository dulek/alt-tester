from abc import ABCMeta, abstractmethod

from lib.utils import get_lm_distances


class LMPicker(object):
    __metaclass__ = ABCMeta

    def __init__(self, G, G_reversed, P, center):
        self.G = G
        self.G_reversed = G_reversed
        self.P = P
        self.center = center

    @abstractmethod
    def get_landmarks(self, lm_num=10):
        pass

    def _calc_dists(self, lms):
        lms_dists = get_lm_distances(self.G, lms)
        lms_dists_rev = get_lm_distances(self.G_reversed, lms)

        return lms, lms_dists, lms_dists_rev
