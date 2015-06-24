import random

from lib.utils import all_dijkstra

from lm_picker import LMPicker


class FarthestLMPicker(LMPicker):
    def _get_farthest(self, lms):
        dists = all_dijkstra(lms, self.G)
        node = max(dists.iterkeys(), key=(lambda key: dists[key]))
        return node

    def get_landmarks(self, lm_num=10):
        # First one at random
        lms = [random.choice(self.G.keys())]

        # Then greedily get farthest nodes from set
        for _i in xrange(0, lm_num):
            lm = self._get_farthest(lms)
            lms.append(lm)

        lms.pop(0)  # Remove the first one

        print 'Choosen landmarks: %s' % lms
        return {lm: {} for lm in lms}