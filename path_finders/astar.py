from heap.heap import heap

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
        frontier = heap([])
        frontier[self.src] = 0
        came_from = {}
        cost_so_far = {}
        came_from[self.src] = None
        cost_so_far[self.src] = 0

        while len(frontier):
            current = frontier.pop()
            visited_nodes.append(self.P[current])

            if current == self.dest:
                break

            for next in self.G[current].keys():
                new_cost = cost_so_far[current] + self.G[current][next]
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.H[next]
                    frontier[next] = priority
                    came_from[next] = current

        return self._reconstruct_path(came_from), visited_nodes

