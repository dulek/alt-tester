from lib.utils import all_dijkstra, get_lower_bound, get_lm_distances

from astar import AStar
from lm_pickers.rand import RandomLMPicker


class AStarLandmarks(AStar):
    def __init__(self, G, P, center, G_reversed, lm_picker_cls=RandomLMPicker,
                 lm_num=8):
        super(AStarLandmarks, self).__init__(G, P)
        self.G_reversed = G_reversed
        self.lm_picker = lm_picker_cls(self.G, self.G_reversed, self.P,
                                       center)

        self.calculate_landmarks(lm_num)

    def calculate_landmarks(self, lm_num=None):
        if not lm_num:
            lm_num = len(self.lms)

        self.lms, self.lms_dists, self.lms_dists_rev = \
            self.lm_picker.get_landmarks(lm_num)

    def heuristic(self, v, src, dest):
        return get_lower_bound(self.lms_dists, self.lms_dists_rev, v, dest)
