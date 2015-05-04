import random

from lib.priority_queue import PriorityQueue

from lm_picker import LMPicker


class FarthestLMPicker(LMPicker):
    def _dijkstra(self, lms):
        frontier = PriorityQueue()
        cost_so_far = {}
        for lm in lms:
            frontier.put(lm, 0)
            cost_so_far[lm] = 0

        while not frontier.empty():
            current = frontier.get()

            for next in self.G[current].keys():
                new_cost = cost_so_far[current] + self.G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    frontier.put(next, priority)

        return cost_so_far

    def _get_farthest(self, lms):
        dists = self._dijkstra(lms)
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