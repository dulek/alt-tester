from lib.utils import all_dijkstra, get_lower_bound, get_lm_distances

from astar import AStar
from lm_pickers.rand import RandomLMPicker


class AStarLandmarks(AStar):
    def __init__(self, G, P, db, G_reversed, lm_picker_cls=RandomLMPicker,
                 lm_num=8):
        super(AStarLandmarks, self).__init__(G, P, db)
        self.G_reversed = G_reversed
        self.lm_picker = lm_picker_cls(self.G, self.G_reversed, self.P,
                                       self.db)

        self.calculate_landmarks(lm_num)

    def calculate_landmarks(self, lm_num):
        self.lms = self.lm_picker.get_landmarks(lm_num)
        self.lms_dists = get_lm_distances(self.G, self.lms)
        self.lms_dists_rev = get_lm_distances(self.G_reversed, self.lms)

    def heuristic(self, v, src, dest):
        return get_lower_bound(self.lms_dists, self.lms_dists_rev, v, dest)
