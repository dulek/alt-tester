import random

from lib.priority_queue import PriorityQueue

from farthest import FarthestLMPicker


class OptimizedFarthestLMPicker(FarthestLMPicker):
    def get_landmarks(self, lm_num=10):
        # First one at random
        lms = [random.choice(self.G.keys())]

        # Then greedily get farthest nodes from set
        for _i in xrange(0, lm_num):
            lm = self._get_farthest(lms)
            lms.append(lm)

        lms.pop(0)  # Remove the first one

        # And now the optimizations...
        for _i in xrange(0, 100):
            # Remove landmark at random
            lms.pop(random.choice(range(0, lm_num)))

            # Find new farthest
            lm = self._get_farthest(lms)
            lms.append(lm)

        print 'Choosen landmarks: %s' % lms
        return {lm: {} for lm in lms}