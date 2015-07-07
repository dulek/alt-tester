from numpy import arctan2
from shapely import geometry

from lib import utils
from lm_picker import LMPicker


class PlanarLMPicker(LMPicker):
    def _get_dists(self, lms):
        return utils.all_dijkstra(lms, self.G)

    def get_landmarks(self, lm_num=10):
        lms = []
        bounds = []

        # Get boundary and center of it
        mp = geometry.MultiPoint(self.P.values())

        # Get node closest to the center
        center_query = ("SELECT node_id, "
                        "Distance(MakePoint(%f, %f), geometry) as dist "
                        "FROM roads_nodes ORDER BY dist LIMIT 1;" %
                        (mp.centroid.x, mp.centroid.y))
        self.db.execute(center_query)
        center_id, _ = self.db.fetchone()

        # Get point
        center = self.P[center_id]

        def polarc(c, p):
            """
            :param c: Center of reference system.
            :param p: Point to convert.
            :return: Returns angle in polar coordinates.
            """
            t = geometry.Point(p.x - c.x, p.y - c.y)
            return arctan2(t.y, t.x)

        # Get a sorted copy
        sorted_nodes = self.P.items()
        sorted_nodes.sort(key=lambda x: polarc(center, x[1]))

        # Get only the node_id
        sorted_nodes = [x[0] for x in sorted_nodes]

        # Chunk node_ids
        chunked_nodes = utils.chunks(sorted_nodes, lm_num)

        # Calc distances from center
        dists = self._get_dists([center_id])

        bounds.append(sorted_nodes[0])
        for chunk in chunked_nodes:
            # Get farthest node
            lms.append(max(chunk,
                           key=lambda k: dists[k] if k in dists else 0))

            bounds.append(chunk[-1])

            # TODO: Possible optimization if two lms are close.

        return {lm: {} for lm in lms}


class PlanarBLMPicker(PlanarLMPicker):
    def _get_dists(self, lms):
        return utils.all_bfs(lms, self.G)
