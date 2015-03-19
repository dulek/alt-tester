from math import sin, cos, pi

from shapely import geometry

from lm_picker import LMPicker


class PlanarLMPicker(LMPicker):
    def get_landmarks(self, lm_num=10):
        # Get boundary and center of it
        mp = geometry.MultiPoint(self.P.values())
        center = mp.centroid

        # First decide on pie slices
        slice_l = max(mp.bounds[2] - mp.bounds[0], mp.bounds[3] -
                      mp.bounds[1]) / 1.5
        slice_nodes = len(self.P) / lm_num
        slice_step = 2 * pi / lm_num / 10
        i_rad = 0.0
        first_p = old_p = geometry.Point(center.x + slice_l * sin(i_rad),
                                         center.y + slice_l * cos(i_rad))
        pols = []
        print 'Starting planar:'
        while len(pols) != (lm_num - 1):
            i_rad += slice_step
            p = geometry.Point(center.x + slice_l * sin(i_rad),
                               center.y + slice_l * cos(i_rad))

            pol = geometry.Polygon([(x.x, x.y) for x in [old_p, p, center]])

            num = 0
            for i, geom in self.P.iteritems():
                if pol.contains(geom):
                    num += 1

            # TODO: More experiments on len(self.P) * 0.005 - with st. deviation
            if num > slice_nodes or slice_nodes - num <= len(self.P) * 0.0054:
                pols.append(pol)
                old_p = p
                print 'HIT!'

            print 'Planar progress: %f' % (i_rad / (2 * pi))

        pols.append(geometry.Polygon([(x.x, x.y) for x
                                      in [old_p, first_p, center]]))

        # Now find landmark per slice
        counts = [0 for i in xrange(0, lm_num)]
        maxes = [(-1, None, None) for i in xrange(0, lm_num)]

        for i, p in self.P.iteritems():
            for j in xrange(0, len(pols)):
                if pols[j].contains(p):
                    counts[j] += 1
                    if maxes[j][0] < p.distance(center):
                        maxes[j] = (p.distance(center), i, p)

        print counts
        print 'Choosen landmarks: %s' % [x[1] for x in maxes]
        return {lm: {} for lm in [x[1] for x in maxes]}


