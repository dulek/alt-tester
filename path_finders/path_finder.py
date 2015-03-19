from abc import ABCMeta, abstractmethod

class PathFinder(object):
    __metaclass__ = ABCMeta

    def __init__(self, G, db):
        self.db = db
        self.G = G
        self.src = None
        self.dest = None

    @abstractmethod
    def precalc(self, src, dest):
        pass

    @abstractmethod
    def calc(self):
        pass

    def _reconstruct_path(self, came_from):
        current = self.dest
        path = [current]
        while current != self.src:
            current = came_from[current]
            path.append(current)
        return path[::-1]