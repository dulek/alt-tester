import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, LineString
from descartes import PolygonPatch


def visualize(points, lines, bounds, name, lms=[], additional=0.2):
    # lower left minx miny , upper right maxx maxy
    minx, miny, maxx, maxy = bounds
    w, h = maxx - minx, maxy - miny

    # create a new matplotlib figure and axes instance
    fig = plt.figure(figsize=(15, 15))  # TODO: Here we adjust size.
    ax = fig.add_subplot(111)
    # add a basemap and a small additional extent
    m = Basemap(
        projection='merc',
        ellps='WGS84',
        llcrnrlon=minx - additional * w,
        llcrnrlat=miny - additional * h,
        urcrnrlon=maxx + additional * w,
        urcrnrlat=maxy + additional * h,
        lat_ts=0,
        resolution='h')
    m.drawcoastlines(linewidth=0.3)
    m.drawmapboundary()
    m.drawcountries()
    # a shapefile can be added like so if needed
    # m.readshapefile('london_shp', 'london', color='#555555')

    # set axes limits to basemap's coordinate reference system
    min_x, min_y = m(minx, miny)
    max_x, max_y = m(maxx, maxy)
    corr_w, corr_h = max_x - min_x, max_y - min_y
    ax.set_xlim(min_x - additional * corr_w, max_x + additional * corr_w)
    ax.set_ylim(min_y - additional * corr_h, max_y + additional * corr_h)
    # square up axes and basemap
    ax.set_aspect(1)

    patches = []

    patches += [PolygonPatch(Point(m(point.x, point.y)).buffer(100.0),
                             fc='#0000ff', ec='#0000ff', zorder=3)
                for point in points]

    patches += [PolygonPatch(Point(m(point.x, point.y)).buffer(1000.0),
                             fc='#ff0000', ec='#ff0000', zorder=1)
                for point in lms]

    for line in lines:
        x, y = line.xy
        xys = []
        for x, y in zip(x, y):
            xys.append(m(x, y))

        x, y = map(list, zip(*xys))

        ax.plot(x, y, color='#00ff00', linewidth=1, solid_capstyle='round',
                zorder=2)

    ax.add_collection(PatchCollection(patches, match_original=True))
    plt.savefig('plots/%s.png' % name, dpi=300)
    plt.show()
