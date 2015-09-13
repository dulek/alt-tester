from collections import defaultdict
import math
import random
from numpy import random as random_np

from colorama import Fore

from lib import logger
from lib.utils import all_dijkstra_tree, get_lower_bound, get_lm_distances
from lm_picker import LMPicker


LOG = logger.getLogger()


class MaxcoverPicker(LMPicker):
    def get_avoid_landmarks(self, lms=None, lm_dists=None, lm_dists_rev=None,
                            lm_num=10):
        lms = lms or []
        lm_dists = lm_dists or {}
        lm_dists_rev = lm_dists_rev or {}

        # And now real picking begins...
        for i in range(len(lms), lm_num):
            LOG.info('Calculating landmark ' + Fore.RED + '%d' + Fore.RESET +
                     '...', i)

            r = random.choice(self.G.keys())
            LOG.debug('    Choosen r=%d.', r)
            r_dists, r_tree, r_order = all_dijkstra_tree(r, self.G)

            # First calculate "weights".
            LOG.info('    Calculating weights...')
            weights = {}
            for v in self.G.keys():
                weights[v] = r_dists[v] - get_lower_bound(lm_dists,
                                                          lm_dists_rev, r, v)

            LOG.info('    Calculating sizes...')
            # Then "sizes" dependent on "weights"
            sizes = defaultdict(lambda: 0)
            w = None  # That's the node of max size

            # We're processing the vertices in reversed order of Dijkstra
            # algorithm. Basically we're starting on the leaves and going up.
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

            LOG.info('    Calculating landmark...')
            # We have all the sizes calculated, and max one (w). Now we travese
            # subtree of r_tree rooted in w. We always choose branch of highest
            # size.
            while r_tree[w]:
                w = max(r_tree[w], key=lambda x: sizes[x])

            # Adding leaf as a new landmark
            LOG.info('    Calculated node ' + Fore.RED + '%d' + Fore.RESET +
                     ' as landmark.', w)
            lms.append(w)

            # Calculate distances for new landmark
            LOG.info('    Calculating distances for this landmark...')
            lm_dists[w] = get_lm_distances(self.G, [w])[w]
            lm_dists_rev[w] = get_lm_distances(self.G_reversed, [w])[w]

        LOG.info(Fore.RED + 'Choosen landmarks: %s' + Fore.RESET, str(lms))
        return lms, lm_dists, lm_dists_rev

    def calculate_cost(self, lms, lm_dists):
        cost = 0

        # Iterate over all edges.
        for v in self.G.keys():
            for w in self.G[v].keys():
                # Iterate over all landmarks
                for lm in lms:
                    if self.G[v][w] - lm_dists[lm][w] + lm_dists[lm][v]:
                        cost += 1
                        break

        LOG.info('Cost of current solution: %d', cost)
        return cost

    def get_landmarks(self, lm_num=10):
        k = lm_num  # For compatibility with description in Goldberg's article.
        C = set()
        C_dists = {}
        C_dists_rev = {}
        # Start with getting k landmarks by avoid, add all as candidates
        lms, lm_dists, lm_dists_rev = self.get_avoid_landmarks(lm_num=k)
        C.update(lms)
        C_dists.update(lm_dists)
        C_dists_rev.update(lm_dists_rev)

        # Repeat until avoid is called 5k times or we have 4k landmarks
        i = 0  # Number of calls to Avoid.
        # TODO: Too much candidates are generated (4 landmarks - 21 candidates)
        # I should probably split that to use avoid one-by-one.
        while len(C) < (4 * k) and i < (5 * k):
            # With probability 1/2 remove each landmark from the solution
            for lm in lms:
                if random.randint(0, 1):
                    lms.remove(lm)
                    del lm_dists[lm]
                    del lm_dists_rev[lm]

            i += k - len(lms)  # Avoid will be called that many times.

            # Generate new landmarks
            lms, lm_dists, lm_dists_rev = self.get_avoid_landmarks(lms,
                                                                   lm_dists,
                                                                   lm_dists_rev,
                                                                   k)

            # Add new ones to C and repeat everything
            C.update(lms)
            C_dists.update(lm_dists)
            C_dists_rev.update(lm_dists_rev)

        LOG.info('Got %d candidates in C.', len(C))

        # Multistart heuristic with local search - swapping
        solutions = []
        costs = []
        for i in xrange(int(math.log(k + 1, 2))):
            LOG.info('Calculating %d for %d sets', i + 1,
                     int(math.log(k + 1, 2)))
            S = set(random.sample(C, k))  # Get k lms from C at random
            T = C - S  # Rest of candidates

            current_cost = self.calculate_cost(S, C_dists)

            while True:
                profits = {}
                for s in S:
                    for t in T:
                        LOG.info('Trying out swap %d-%d.', s, t)
                        new_S = S.copy()
                        new_S.remove(s)
                        new_S.add(t)
                        new_cost = self.calculate_cost(new_S, C_dists)
                        profit = new_cost - current_cost
                        if profit > 0:
                            LOG.info('Swap %d-%d profitable with %d profit.',
                                     s, t, profit)
                            profits['%d-%d' % (s, t)] = profit

                # If no improvement can be made stop.
                if not profits:
                    break

                # Otherwise choose swap at random with profit weights
                p = profits.values()
                p_sum = float(sum(p))
                p = [x / p_sum for x in p]  # Normalize weigths to sum to 1.0
                swap = random_np.choice(profits.keys(), p=p)
                LOG.info('Swap %s chosen.', swap)
                s, t = swap.split('-')
                s, t = int(s), int(t)
                S.remove(s)
                S.add(t)
                current_cost += profits[swap]

            LOG.info('No improvements could be made - solution found: %s (%d).',
                     str(S), current_cost)
            solutions.append(S)
            costs.append(current_cost)

        solution = solutions[max(xrange(len(costs)), key=costs.__getitem__)]
        LOG.info('Best solution chosen: %s.', str(solution))
        return (list(solution),
                {k: v for k, v in C_dists.items() if k in solution},
                {k: v for k, v in C_dists_rev.items() if k in solution})
