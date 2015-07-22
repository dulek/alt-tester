from numpy import arctan2
from shapely import geometry

from lib import utils
from lm_picker import LMPicker


class PlanarLMPicker(LMPicker):
    def _get_dists(self, lms):
        return utils.all_dijkstra(lms, self.G)

    def polarc(self, p):
        t = geometry.Point(p.x - self.c.x, p.y - self.c.y)
        return arctan2(t.y, t.x)

    def get_landmarks(self, lm_num=10):
        lms = []
        bounds = []

        # Get point
        self.c = self.P[self.center]

        # Get a sorted copy
        self.sorted_nodes = self.P.items()
        self.sorted_nodes.sort(key=lambda x: self.polarc(x[1]))

        # Get only the node_id
        self.sorted_nodes = [x[0] for x in self.sorted_nodes]

        # Chunk node_ids
        chunked_nodes = utils.chunks(self.sorted_nodes, lm_num)

        # Calc distances from center
        self.dists = self._get_dists([self.center])

        bounds.append(self.sorted_nodes[0])
        for chunk in chunked_nodes:
            # Get farthest node
            lms.append(max(chunk,
                           key=lambda k: self.dists[k]
                           if k in self.dists else 0))

            bounds.append(chunk[-1])

            # TODO: Possible optimization if two lms are close.

        return self._calc_dists(lms)


class PlanarBLMPicker(PlanarLMPicker):
    def _get_dists(self, lms):
        return utils.all_bfs(lms, self.G)
