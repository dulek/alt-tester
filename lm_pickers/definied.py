from lm_picker import LMPicker

class DefiniedLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        lms = [74066, 1189637, 502011, 925562, 1190330, 655656, 101989,
               1033011, 503684, 1033830]
        return {lm: {} for lm in lms}