from collections import defaultdict

from astar import AStar


class Dijkstra(AStar):
    def precalc(self, src, dest):
        self.src = src
        self.dest = dest

        # Heuristic is always 0
        self.H = defaultdict(lambda: 0)
