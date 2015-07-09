from abc import ABCMeta, abstractmethod


class LMPicker(object):
    __metaclass__ = ABCMeta

    def __init__(self, G, G_reversed, P, db):
        self.G = G
        self.G_reversed = G_reversed
        self.P = P
        self.db = db

    @abstractmethod
    def get_landmarks(self, lm_num=10):
        pass
