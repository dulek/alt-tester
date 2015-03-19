from math import sin, cos, pi

from shapely import geometry

from lm_picker import LMPicker

# TODO: This doesn't perserve equality of area (or node count)... How to fix?


class PlanarLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        # Get boundary and center of it
        mp = geometry.MultiPoint(self.P.values())
        center = mp.centroid
        bounds = mp.bounds

        slice_l = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) / 1.5

        slice_points = []
        slice_rad = 2 * pi / lm_num
        i_rad = 0.0
        p = None
        pols = []
        for i in xrange(0, lm_num + 1):
            old_p = p
            p = geometry.Point(center.x + slice_l * sin(i_rad),
                               center.y + slice_l * cos(i_rad))

            if i > 0:
                pols.append(geometry.Polygon([(x.x, x.y) for x
                                              in [old_p, p, center]]))

            i_rad += slice_rad

        counts = [0 for i in xrange(0, lm_num)]
        maxes = [(-1, None, None) for i in xrange(0, lm_num)]

        for i, p in self.P.iteritems():
            for j in xrange(0, len(pols)):
                if (pols[j].contains(p)):
                    counts[j] += 1
                    if (maxes[j][0] < p.distance(center)):
                        maxes[j] = (p.distance(center), i, p)

        print 'Choosen landmarks: %s' % [x[1] for x in maxes]
        return {lm: {} for lm in [x[1] for x in maxes]}


