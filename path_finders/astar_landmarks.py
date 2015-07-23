import json

from lib.utils import get_lower_bound

from astar import AStar
from lm_pickers.rand import RandomLMPicker


class AStarLandmarks(AStar):
    def __init__(self, G, P, center, G_reversed, lm_picker_cls=RandomLMPicker,
                 lm_num=8):
        super(AStarLandmarks, self).__init__(G, P)
        self.G_reversed = G_reversed
        self.lm_picker = lm_picker_cls(self.G, self.G_reversed, self.P,
                                       center)

        self.recalculate_num = 0
        self.calculate_landmarks(lm_num)

    def calculate_landmarks(self, lm_num=None):
        if not lm_num:
            lm_num = len(self.lms)

        self.lms, self.lms_dists, self.lms_dists_rev = \
            self.lm_picker.get_landmarks(lm_num)

        with open('lms/lms-%s-%d' % (type(self.lm_picker).__name__,
                                 self.recalculate_num)) as f:
            json.dump(self.lms, f)

        self.recalculate_num += 1

    def heuristic(self, v, src, dest):
        return get_lower_bound(self.lms_dists, self.lms_dists_rev, v, dest)
