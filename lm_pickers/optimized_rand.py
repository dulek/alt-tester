import random

from lm_picker import LMPicker


class OptimizedRandomLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        lms = random.sample(self.G.keys(), lm_num)

        return self._calc_dists(lms)
