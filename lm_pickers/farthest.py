import random

from lib import logger
from lib.utils import all_dijkstra, all_bfs

from lm_picker import LMPicker


LOG = logger.getLogger()

class FarthestLMPicker(LMPicker):
    def _get_dists(self, lms):
        return all_dijkstra(lms, self.G)

    def _get_farthest(self, lms):
        dists = self._get_dists(lms)
        node = max(dists.iterkeys(), key=(lambda key: dists[key]))
        return node

    def _get_landmarks(self, lm_num):
        # First one at random
        lms = [random.choice(self.G.keys())]

        # Then greedily get farthest nodes from set
        for _i in xrange(0, lm_num):
            lm = self._get_farthest(lms)
            lms.append(lm)

        lms.pop(0)  # Remove the first one

        return lms

    def get_landmarks(self, lm_num=10):
        lms = self._get_landmarks(lm_num)
        LOG.info('Choosen landmarks: %s', str(lms))
        return self._calc_dists(lms)


class FarthestBLMPicker(FarthestLMPicker):
    def _get_dists(self, lms):
        return all_bfs(lms, self.G)
