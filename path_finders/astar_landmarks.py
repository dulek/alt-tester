from lib.utils import all_dijkstra

from astar import AStar
from lm_pickers.rand import RandomLMPicker


class AStarLandmarks(AStar):
    def __init__(self, G, P, db, G_reversed, lm_picker_cls=RandomLMPicker,
                 lm_num=8):
        super(AStarLandmarks, self).__init__(G, P, db)
        self.G_reversed = G_reversed
        self.lm_picker = lm_picker_cls(self.G, self.P, self.db)

        self.calculate_landmarks(lm_num)

    def calculate_landmarks(self, lm_num):
        self.lms = self.lm_picker.get_landmarks(lm_num)
        self.lms_rev = self.lms.copy()

        for lm in self.lms:
            self.lms[lm] = all_dijkstra([lm], self.G)

        for lm in self.lms_rev:
            self.lms_rev[lm] = all_dijkstra([lm], self.G_reversed)

    def heuristic(self, v, src, dest):
        def get_dist(mapping, node):
            return mapping[node] if node in mapping else float('inf')

        candid = []
        for lm in self.lms.keys():
            c = max(
                get_dist(self.lms[lm], dest) - get_dist(self.lms[lm], v),
                get_dist(self.lms_rev[lm], v) - get_dist(self.lms_rev[lm],
                                                         dest)
            )
            candid.append(c)

        return abs(max(candid))
