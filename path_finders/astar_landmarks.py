from lib.priority_queue import PriorityQueue

from astar import AStar
from lm_pickers.rand import RandomLMPicker


class AStarLandmarks(AStar):
    def __init__(self, G, P, db, G_reversed, lm_picker_cls=RandomLMPicker):
        super(AStarLandmarks, self).__init__(G, P, db)
        self.G_reversed = G_reversed
        self.lm_picker = lm_picker_cls(self.G, self.P, self.db)

    def _dijkstra(self, lm, G):
        # TODO: Replace with utils all_dijkstra
        frontier = PriorityQueue()
        frontier.put(lm, 0)
        cost_so_far = {}
        cost_so_far[lm] = 0

        while not frontier.empty():
            current = frontier.get()

            for next in G[current].keys():
                new_cost = cost_so_far[current] + G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    frontier.put(next, priority)

        return cost_so_far

    def precalc(self, src, dest, lm_num=5):
        self.src = src
        self.dest = dest

        lms = self.lm_picker.get_landmarks(lm_num)
        lms_rev = lms.copy()

        for lm in lms:
            lms[lm] = self._dijkstra(lm, self.G)

        for lm in lms_rev:
            lms_rev[lm] = self._dijkstra(lm, self.G_reversed)

        cinf = 0
        cnan = 0
        self.H = {}
        for node_id in self.G.keys():
            def get_dist(mapping, node):
                return abs(mapping[node] if node in mapping else float('inf'))

            candid = []
            for lm in lms.keys():
                # TODO: Seems like this is it. Need more tests to confirm.
                c = max(get_dist(lms[lm], node_id) -
                        get_dist(lms[lm], self.dest),
                        get_dist(lms_rev[lm], node_id) -
                        get_dist(lms_rev[lm], self.dest))
                candid.append(c)

            self.H[node_id] = max(candid)

            if self.H[node_id] == float('inf'):
                cinf += 1

            if self.H[node_id] == float('nan'):
                cnan += 1

        print 'Infs: %d' % cinf
        print 'NaNs: %d' % cnan
        print 'Nums: %d' % (len(self.H) - cinf - cnan)

        return lms
