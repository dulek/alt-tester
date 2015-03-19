import random
from lib.priority_queue import PriorityQueue

from astar import AStar

class AStarLandmarks(AStar):
    def _dijkstra(self, lm):
        frontier = PriorityQueue()
        frontier.put(lm, 0)
        came_from = {}
        cost_so_far = {}
        came_from[lm] = None
        cost_so_far[lm] = 0

        while not frontier.empty():
            current = frontier.get()

            for next in self.G[current].keys():
                new_cost = cost_so_far[current] + self.G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    frontier.put(next, priority)
                    came_from[next] = current

        return cost_so_far

    def precalc(self, src, dest, lm_num=10):
        self.src = src
        self.dest = dest

        # Pick 10 landarks at random
        lms = {}
        for i in xrange(0, lm_num):
            lms[random.choice(self.G.keys())] = {}

        for lm in lms:
            lms[lm] = self._dijkstra(lm)

        self.H = {}
        print lms.keys()
        for node_id in self.G.keys():
            # TODO: This is estimated, need also second distance
            # TODO: What if some nodes are unrechable?

            self.H[node_id] = max([lm[node_id] if node_id in lm else
                                   float('inf') - lm[self.dest]
                                   for i, lm in lms.iteritems()]);
