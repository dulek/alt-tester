import sys

from shapely import wkb
import sqlite3

from lib.timing import timing
from lib.pairwise import pairwise

from path_finders.dijkstra import Dijkstra
from path_finders.astar import AStar
from path_finders.astar_landmarks import AStarLandmarks
from lm_pickers.definied import DefiniedLMPicker
from lm_pickers.rand import RandomLMPicker
from lm_pickers.farthest import FarthestLMPicker
from lm_pickers.optimized_farthest import OptimizedFarthestLMPicker
from lm_pickers.planar import PlanarLMPicker

from visualize import visualize

# Connecting to the database
db = sqlite3.connect('gdansk.sqlite')
db.enable_load_extension(True)
db.load_extension('libspatialite')
cur = db.cursor()

# Graph definition
G = {}  # Graph
G_reversed = {}  # Graph with reversed edges - for A* landmarks heuristic
P = {}  # Geographical points TODO: Node class and geom info in it?
L = {}  # Roads geometries, TODO: Edge class and geom info in it?

# Load graph vertices
node_query = "SELECT node_id, AsBinary(geometry) AS point FROM roads_nodes;"
cur.execute(node_query)
nodes = cur.fetchall()
for i, geometry in nodes:
    G_reversed[i] = {}
    G[i] = {}
    L[i] = {}
    P[i] = wkb.loads(str(geometry))

# Load graph edges
road_query = ("SELECT node_from, node_to, oneway_fromto, oneway_tofrom, "
              "GLength(geometry) as length, AsBinary(geometry) as line "
              "FROM roads;")
cur.execute(road_query)
roads = cur.fetchall()
for node_from, node_to, fromto, tofrom, length, geometry in roads:
    if fromto:
        G[node_from][node_to] = length
        G_reversed[node_to][node_from] = length
        L[node_from][node_to] = wkb.loads(str(geometry))
    if tofrom:
        G[node_to][node_from] = length
        G_reversed[node_to][node_from] = length
        L[node_to][node_from] = wkb.loads(str(geometry))

# We need to decide target now...
src = 10  # 224979
dest = int(sys.argv[1]) if len(sys.argv) > 1 else 8000  # 1142754

# Let's prepare classes
dijkstra = Dijkstra(G, P, cur)
astar = AStar(G, P, cur)
astar_landmarks = AStarLandmarks(G, P, cur, G_reversed, OptimizedFarthestLMPicker)

# Precalculations
dijkstra.precalc(src, dest)
astar.precalc(src, dest)
lms = astar_landmarks.precalc(src, dest, 8)


@timing
def test_dijkstra():
    return dijkstra.calc()


@timing
def test_astar():
    return astar.calc()


@timing
def test_astar_landmarks():
    return astar_landmarks.calc()


dijkstra_path, dijkstra_visited = test_dijkstra()
astar_path, astar_visited = test_astar()
astar_landmarks_path, astar_landmarks_visited = test_astar_landmarks()


def calc_cost(path):
    cost = 0.0
    for i in range(1, len(path)):
        cost += G[path[i - 1]][path[i]]
    return cost


print dijkstra_path == astar_path == astar_landmarks_path

print '%d = %f, %d' % (len(dijkstra_path), calc_cost(dijkstra_path),
                       len(dijkstra_visited))
print '%d = %f, %d' % (len(astar_path), calc_cost(astar_path),
                       len(astar_visited))
print '%d = %f, %d' % (len(astar_landmarks_path),
                       calc_cost(astar_landmarks_path),
                       len(astar_landmarks_visited))

exit()

bounds_poland = (13.42529296875, 48.574789910928864, 24.23583984375,
                 55.12864906848878)
bounds_pomeranian = (16.8365478515625, 53.389880751560284, 19.5062255859375,
                     55.05949523049586)

dijkstra_path_geom = [L[a][b] for a, b in pairwise(dijkstra_path)]
astar_path_geom = [L[a][b] for a, b in pairwise(astar_path)]
astar_landmarks_path_geom = [L[a][b] for a, b in pairwise(astar_landmarks_path)]

visualize(dijkstra_visited, dijkstra_path_geom, bounds_pomeranian, 'dijkstra')
visualize(astar_visited, astar_path_geom, bounds_pomeranian, 'astar')
visualize(astar_landmarks_visited, astar_landmarks_path_geom, bounds_pomeranian,
          'astar-lms', [P[lm] for lm in lms])
