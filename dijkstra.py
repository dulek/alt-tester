from path_finder import PathFinder
from lib.priority_queue import PriorityQueue

class Dijkstra(PathFinder):
    def precalc(self, src, dest):
        self.src = src
        self.dest = dest

    def calc(self):
        frontier = PriorityQueue()
        frontier.put(self.src, 0)
        came_from = {}
        cost_so_far = {}
        came_from[self.src] = None
        cost_so_far[self.src] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == self.dest:
                break

            for next in self.G[current].keys():
                new_cost = cost_so_far[current] + self.G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    frontier.put(next, priority)
                    came_from[next] = current

        return self._reconstruct_path(came_from)
