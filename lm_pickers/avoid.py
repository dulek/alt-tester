from collections import defaultdict
import random

from lib.utils import all_dijkstra_tree, get_lower_bound, get_lm_distances
from lm_picker import LMPicker


class AvoidLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        # First one at random
        lms = [random.choice(self.G.keys())]
        lm_dists = {}
        lm_dists_rev = {}

        # Calculate distances for new landmark
        lm_dists.update(get_lm_distances(self.G, lms[-1:]))
        lm_dists_rev.update(get_lm_distances(self.G_reversed, lms[-1:]))

        # And now real picking begins...
        for i in range(0, lm_num - 1):
            print 'Calculating landmark %d...' % i

            r = random.choice(self.G.keys())
            r_dists, r_tree = all_dijkstra_tree(r, self.G)

            # First calculate "weights".
            weights = {}
            for v in self.G.keys():
                weights[v] = r_dists[v] - get_lower_bound(lm_dists,
                                                          lm_dists_rev, r, v)

            # Then "sizes" dependent on "weights"
            sizes = {}
            w = None # That's the node of max size
            for v in self.G.keys():
                sizes[v] = 0

                # Traverse subtree of r_tree rooted at v using DFS (why not?)
                Q = [v]
                while Q:
                    u = Q.pop()

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

            # We have all the sizes calculated, and max one (w). Now we travese
            # subtree of r_tree rooted in w. We always choose branch of highest
            # size.
            while r_tree[w]:
                w = max(r_tree[w], key=lambda x: sizes[x])

            # Adding leaf as a new landmark
            lms.append(w)

            # Calculate distances for new landmark
            lm_dists.update(get_lm_distances(self.G, lms[-1:]))
            lm_dists_rev.update(get_lm_distances(self.G_reversed, lms[-1:]))

        print 'Choosen landmarks: %s' % lms
        return lms, lm_dists, lm_dists_rev
