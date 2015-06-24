from lib.priority_queue import PriorityQueue

from path_finder import PathFinder


class AStar(PathFinder):
    def precalc(self, src, dest):
        self.src = src
        self.dest = dest

        # Load target node geometry
        target_query = ("SELECT AsText(geometry) as geometry FROM roads_nodes "
                        "WHERE node_id = %s;" % self.dest)
        self.db.execute(target_query)
        target = self.db.fetchone()

        # Load distances to target for each node (basic A* heuristic)
        heuristic_query = ("SELECT node_id, Distance(geometry, "
                           "GeomFromText('%s')) AS distance FROM roads_nodes;"
                           % target[0])
        self.db.execute(heuristic_query)
        heuristic = self.db.fetchall()

        self.H = {}
        for node_id, distance in heuristic:
            self.H[node_id] = distance

    def calc(self):
        visited_nodes = []
        frontier = PriorityQueue()
        frontier.put(self.src, 0)
        came_from = {}
        cost_so_far = {}
        came_from[self.src] = None
        cost_so_far[self.src] = 0

        while not frontier.empty():
            current = frontier.get()
            visited_nodes.append(self.P[current]) # TODO: As we're using heapq
            # this isn't good way of calculating. visited_nodes should be a set
            # then.

            if current == self.dest:
                break

            for next in self.G[current].keys():
                new_cost = cost_so_far[current] + self.G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.H[next] # TODO: Test with self.H
                    # moved up to the condition (this is how some describe the
                    # algorithm).
                    frontier.put(next, priority)
                    came_from[next] = current

        return self._reconstruct_path(came_from), visited_nodes

