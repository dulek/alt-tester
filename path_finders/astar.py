from heap.heap import heap
from LatLon import LatLon

from path_finder import PathFinder


class AStar(PathFinder):
    def heuristic(self, v, src, dest):
        src = LatLon(self.P[v].y, self.P[v].x)
        dest = LatLon(self.P[dest].y, self.P[dest].x)
        return src.distance(dest) * 1000

    def calc(self, src, dest):
        visited_nodes = []
        frontier = heap([])
        frontier[src] = 0
        came_from = {}
        cost_so_far = {}
        came_from[src] = None
        cost_so_far[src] = 0

        while len(frontier):
            current = frontier.pop()
            visited_nodes.append(self.P[current])

            if current == dest:
                break

            for next in self.G[current].keys():
                new_cost = cost_so_far[current] + self.G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, src, dest)
                    frontier[next] = priority
                    came_from[next] = current

        return self._reconstruct_path(came_from, src, dest), visited_nodes
