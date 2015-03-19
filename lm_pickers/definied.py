from lm_picker import LMPicker


class DefiniedLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        lms = [9987, 2062, 36861, 1483, 37357, 30542, 1271, 6699]
        return {lm: {} for lm in lms}