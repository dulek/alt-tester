from collections import defaultdict
import random

from lib import logger
from lib.utils import all_dijkstra_tree, get_lower_bound, get_lm_distances
from lm_picker import LMPicker

LOG = logger.getLogger()


class AvoidLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        # First one at random
        first = random.choice(self.G.keys())
        lms = [first]
        lm_dists = {}
        lm_dists_rev = {}

        # Calculate distances for new landmark
        lm_dists[first] = get_lm_distances(self.G, lms)[first]
        lm_dists_rev[first] = get_lm_distances(self.G_reversed, lms)[first]

        # And now real picking begins...
        for i in range(0, lm_num - 1):
            LOG.info('Calculating landmark %d...', i)

            r = random.choice(self.G.keys())
            LOG.debug('Choosen r=%d.', r)
            r_dists, r_tree, r_order = all_dijkstra_tree(r, self.G)

            # First calculate "weights".
            LOG.info('Calculating weights...')
            weights = {}
            for v in self.G.keys():
                weights[v] = r_dists[v] - get_lower_bound(lm_dists,
                                                          lm_dists_rev, r, v)

            LOG.info('Calculating sizes...')
            # Then "sizes" dependent on "weights"
            sizes = defaultdict(lambda: 0)
            w = None  # That's the node of max size

            # We're processing the vertices in reversed order of Dijkstra
            # algorithm. Basically we're starting on the leaves and going up.
            # TODO: Is it any different from post-order tree traversal?
            for v in reversed(r_order):
                # Traverse subtree of r_tree rooted at v using DFS
                Q = [v]
                while Q:
                    u = Q.pop()

                    # It's possible we already have size of the subtree
                    if u in sizes:
                        if sizes[u] == 0:
                            sizes[v] = 0
                            break
                        else:
                            sizes[v] += sizes[u]
                            continue

                    # If subtree has landmark then size is 0
                    if u in lms:
                        sizes[v] = 0
                        break
                    else:
                        sizes[v] += weights[u]

                    for x in r_tree[u]:
                        Q.append(x)

                if w is None or sizes[w] < sizes[v]:
                    w = v

            LOG.info('Calculating landmark...')
            # We have all the sizes calculated, and max one (w). Now we travese
            # subtree of r_tree rooted in w. We always choose branch of highest
            # size.
            while r_tree[w]:
                w = max(r_tree[w], key=lambda x: sizes[x])

            # Adding leaf as a new landmark
            LOG.info('Calculated node %d as landmark.', w)
            lms.append(w)

            # Calculate distances for new landmark
            LOG.info('Calculating distances for this landmark...')
            lm_dists[w] = get_lm_distances(self.G, [w])[w]
            lm_dists_rev[w] = get_lm_distances(self.G_reversed, [w])[w]

        LOG.info('Choosen landmarks: %s', str(lms))
        return lms, lm_dists, lm_dists_rev
