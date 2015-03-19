from abc import ABCMeta, abstractmethod

class LMPicker:
    __metaclass__ = ABCMeta

    def __init__(self, G, P, db):
        self.G = G
        self.P = P
        self.db = db

    @abstractmethod
    def get_landmarks(self, lm_num=10):
        pass
