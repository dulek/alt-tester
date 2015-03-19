from lib.priority_queue import PriorityQueue

from astar import AStar
from lm_picker import RandomLMPicker

class AStarLandmarks(AStar):
    def __init__(self, G, db, lm_picker_cls=RandomLMPicker):
        super(AStarLandmarks, self).__init__(G, db)
        self.lm_picker = lm_picker_cls(self.G, self.db)

    def _dijkstra(self, lm):
        frontier = PriorityQueue()
        frontier.put(lm, 0)
        cost_so_far = {}
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

    def precalc(self, src, dest, lm_num=5):
        self.src = src
        self.dest = dest

        lms = self.lm_picker.get_landmarks(lm_num)

        for lm in lms:
            lms[lm] = self._dijkstra(lm)

        cpinf = 0
        cminf = 0
        cnan = 0
        self.H = {}
        for node_id in self.G.keys():
            # TODO: This is estimated, need also second distance
            # TODO: What if some nodes are unrechable?

            self.H[node_id] = abs(max([
                (lm[node_id] if node_id in lm else float('inf')) -
                (lm[self.dest] if self.dest in lm else float('inf'))
                for lm in lms.values()]));

            if self.H[node_id] == float('inf'):
                cpinf += 1

            if self.H[node_id] == float('-inf'):
                cminf += 1

            if self.H[node_id] == float('nan'):
                cnan += 1

        print 'Infs: %d' % cpinf
        print '-Infs: %d' % cminf
        print 'NaNs: %d' % cnan
        print 'Nums: %d' % (len(self.H) - cpinf - cminf - cnan)
