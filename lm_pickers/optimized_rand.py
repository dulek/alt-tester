import random

from lib import logger
from lib.utils import get_lower_bound, get_single_lower_bound,\
    get_lm_distances, get_pairs
from rand import RandomLMPicker


LOG = logger.getLogger()

class OptimizedRandomLMPicker(RandomLMPicker):
    def get_landmarks(self, lm_num=10):
        # At first get landmarks at random
        LOG.info('Choosing %d landmarks at random...', lm_num)
        lms, lm_dists, lm_dists_rev = super(OptimizedRandomLMPicker,
                                            self).get_landmarks(lm_num)
        LOG.info('Random returned: %s.', str(lms))

        # Let's choose a sample of vertex pairs
        LOG.info('Choosing sample...')
        pairs = get_pairs(self.G)
        LOG.info('Sample choosen.')

        # And now we're working to improve them
        LOG.info('Optimizing landmarks...')
        K = self.G.keys()
        for i in xrange(lm_num):
            LOG.info('Optimizing landmark %d=%d...', i, lms[i])
            LOG.info('    Geting %d candidates...', lm_num)
            # Get lm_num - 1 at random and calculate
            cands = random.sample(K, lm_num - 1)
            while [x for x in cands if x in lms]:
                # TODO: This probably isn't the best way, but should work.
                cands = random.sample(K, lm_num - 1)
            cands_scores = [0] * lm_num
            cands_dists = get_lm_distances(self.G, cands)
            cands_dists_rev = get_lm_distances(self.G_reversed, cands)

            # Add current lm
            cands.append(lms[i])
            cands_dists[lms[i]] = lm_dists[lms[i]]
            cands_dists_rev[lms[i]] = lm_dists_rev[lms[i]]

            LOG.info('    Choosen candidates: %s.', str(cands))

            # Calculate scores for each candidate
            LOG.info('    Calculating scores for candidates...')
            for S, D in pairs:
                b = get_lower_bound(lm_dists, lm_dists_rev, S, D)

                for j in xrange(lm_num):
                    new_b = get_single_lower_bound(cands_dists[cands[j]],
                                                   cands_dists_rev[cands[j]],
                                                   S, D)
                    sc = new_b - b
                    if sc > 0:
                        cands_scores[j] += sc
            LOG.info('    Scores calculated.')

            # Replace lm with candidate of max score
            best_i = max(xrange(lm_num), key=lambda i: cands_scores[i])
            best = cands[best_i]
            LOG.info('    Landmark %d considered best.', best)
            if best == lms[i]:
                # If we choosen the same - leave it
                LOG.info('    It is the same, continue.')
                continue
            LOG.info('    Replacing landmark %d with %d', lms[i], best)
            del lm_dists[lms[i]]
            lms[i] = best
            lm_dists[best] = cands_dists[best]
            lm_dists_rev[best] = cands_dists_rev[best]

        return lms, lm_dists, lm_dists_rev
