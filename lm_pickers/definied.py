from lm_picker import LMPicker

class DefiniedLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        lms = [1175756, 1186070, 1189622, 1190330, 1190325, 1146788, 914167,
               730787, 562683, 263336, 88328, 13724, 1, 300, 104782, 339900]
        return {lm: {} for lm in lms}