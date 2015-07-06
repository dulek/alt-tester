from collections import defaultdict

from astar import AStar


class Dijkstra(AStar):
    def heuristic(self, v, src, dest):
        return 0
