from abc import ABCMeta, abstractmethod


class PathFinder(object):
    __metaclass__ = ABCMeta

    def __init__(self, G, P):
        self.G = G
        self.P = P

    @abstractmethod
    def heuristic(self, v, src, dest):
        pass

    @abstractmethod
    def calc(self, src, dest):
        pass
