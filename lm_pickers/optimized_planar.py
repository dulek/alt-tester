from numpy import arctan2
from shapely import geometry

from lib import logger
from lib.utils import all_dijkstra, chunks, get_lm_distances, get_lower_bound,\
    get_single_lower_bound, get_pairs, all_bfs
from planar import PlanarLMPicker


LOG = logger.getLogger()

class OptimizedPlanarLMPicker(PlanarLMPicker):
    def get_landmarks(self, lm_num=10):
        # At first get landmarks from planar
        LOG.info('Choosing %d landmarks by planar...', lm_num)
        lms, lm_dists, lm_dists_rev = super(OptimizedPlanarLMPicker,
                                            self).get_landmarks(lm_num)
        LOG.info('Planar returned: %s.', str(lms))

        # Let's choose a sample of vertex pairs
        LOG.info('Choosing sample...')
        pairs = get_pairs(self.G)
        LOG.info('Sample choosen.')

        chunked_nodes = chunks(self.sorted_nodes, lm_num)

        # TODO: This code is duplicated with optimized_rand, refactoring?
        i = 0
        for chunk in chunked_nodes:
            LOG.info('Optimizing landmark %d=%d...', i, lms[i])
            LOG.info('    Geting %d candidates...', lm_num)
            # We're chunking a chunk again!
            cands = []
            chunked_nodes2 = chunks(chunk, lm_num)
            for chunk2 in chunked_nodes2:
                cands.append(max(chunk2,
                                 key=lambda k: self.dists[k]
                                 if k in self.dists else 0))

            cands_scores = [0] * lm_num
            cands_dists = get_lm_distances(self.G, cands)
            cands_dists_rev = get_lm_distances(self.G_reversed, cands)

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
            best_i = max(xrange(lm_num), key=lambda k: cands_scores[k])
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
            i += 1

            # TODO: Possible optimization if two lms are close.

        return lms, lm_dists, lm_dists_rev


class OptimizedPlanarBLMPicker(OptimizedPlanarLMPicker):
    def _get_dists(self, lms):
        return all_bfs(lms, self.G)
