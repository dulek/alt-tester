import random

from lm_picker import LMPicker


class RandomLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        lms = {}
        for _i in xrange(0, lm_num):
            lms[random.choice(self.G.keys())] = {}

        return lms