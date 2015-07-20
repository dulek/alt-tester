import random

from lib import logger
from lib.utils import optimize_lm
from rand import RandomLMPicker


LOG = logger.getLogger()

class OptimizedRandomLMPicker(RandomLMPicker):
    def get_landmarks(self, lm_num=10):
        # At first get landmarks at random
        LOG.info('Choosing %d landmarks at random...', lm_num)
        lms, lm_dists, lm_dists_rev = super(OptimizedRandomLMPicker,
                                            self).get_landmarks(lm_num)
        LOG.info('Random returned: %s.', str(lms))

        def cand_callback(i, lm_num, lms):
            cands = random.sample(self.G.keys(), lm_num - 1)
            while [x for x in cands if x in lms]:
                # TODO: This probably isn't the best way, but should work.
                cands = random.sample(self.G.keys(), lm_num - 1)

            # Add current lm
            cands.append(lms[i])

            return cands

        return optimize_lm(self.G, self.G_reversed, lm_num, lms, lm_dists,
                           lm_dists_rev, cand_callback, xrange(lm_num))
