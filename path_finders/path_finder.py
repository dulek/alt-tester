from abc import ABCMeta, abstractmethod


class PathFinder(object):
    __metaclass__ = ABCMeta

    def __init__(self, G, P, db):
        self.db = db
        self.G = G
        self.P = P

    @abstractmethod
    def heuristic(self, v, src, dest):
        pass

    @abstractmethod
    def calc(self):
        pass

    def _reconstruct_path(self, came_from, src, dest):
        current = dest
        path = [current]
        while current != src:
            current = came_from[current]
            path.append(current)
        return path[::-1]
