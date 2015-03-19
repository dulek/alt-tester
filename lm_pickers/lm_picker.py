from abc import ABCMeta, abstractmethod


class LMPicker:
    __metaclass__ = ABCMeta

    def __init__(self, G, db):
        self.G = G
        self.db = db

    @abstractmethod
    def get_landmarks(self, lm_num=10):
        pass
