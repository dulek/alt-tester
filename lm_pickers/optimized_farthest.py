import random

from farthest import FarthestLMPicker
from lib import logger
from lib.utils import all_bfs


LOG = logger.getLogger()

class OptimizedFarthestLMPicker(FarthestLMPicker):
    def get_landmarks(self, lm_num=10):
        # Get lm_num landmarks at random
        lms = self._get_landmarks(lm_num)

        # And now the optimizations...
        for _i in xrange(0, 100):
            # Remove landmark at random
            lms.pop(random.choice(range(0, lm_num)))

            # Find new farthest
            lm = self._get_farthest(lms)
            lms.append(lm)

        LOG.info('Choosen landmarks: %s', str(lms))
        return self._calc_dists(lms)


class OptimizedFarthestBLMPicker(OptimizedFarthestLMPicker):
    def _get_dists(self, lms):
        return all_bfs(lms, self.G)
