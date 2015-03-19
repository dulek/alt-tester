from astar import AStar

class Dijkstra(AStar):
    def precalc(self, src, dest):
        self.src = src
        self.dest = dest

        class ZeroDict():
            def __getitem__(self, val):
                return 0

        # Heuristic is always 0
        self.H = ZeroDict()
