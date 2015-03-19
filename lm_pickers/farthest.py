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

    def get_landmarks(self, lm_num=10):
        # First one at random
        lms = [random.choice(self.G.keys())]

        # Then greedily get farthest nodes from set
        for _i in xrange(1, lm_num):
            dists = self._dijkstra(lms)
            lm = max(dists.iterkeys(), key=(lambda key: dists[key]))
            lms.append(lm)

        print 'Choosen landmarks: %s' % lms
        return {lm: {} for lm in lms}