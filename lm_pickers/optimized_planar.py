from lib import logger
from lib.utils import chunks, optimize_lm, all_bfs
from planar import PlanarLMPicker


LOG = logger.getLogger()


class OptimizedPlanarLMPicker(PlanarLMPicker):
    def get_landmarks(self, lm_num=10):
        # At first get landmarks from planar
        LOG.info('Choosing %d landmarks by planar...', lm_num)
        lms, lm_dists, lm_dists_rev = super(OptimizedPlanarLMPicker,
                                            self).get_landmarks(lm_num)
        LOG.info('Planar returned: %s.', str(lms))

        def cand_callback(chunk, lm_num, lms):
            cands = []
            chunked_nodes = chunks(chunk, lm_num)
            for chunk2 in chunked_nodes:
                cands.append(max(chunk2,
                                 key=lambda k: self.dists[k]
                                 if k in self.dists else 0))

            return cands

        return optimize_lm(self.G, self.G_reversed, lm_num, lms, lm_dists,
                           lm_dists_rev, cand_callback,
                           chunks(self.sorted_nodes, lm_num))


class OptimizedPlanarBLMPicker(OptimizedPlanarLMPicker):
    def _get_dists(self, lms):
        return all_bfs(lms, self.G)
