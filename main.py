import sys

import sqlite3

from lib.timing import timing

from dijkstra import Dijkstra
from astar import AStar
from astar_landmarks import AStarLandmarks
from lm_picker import RandomLMPicker, DefiniedLMPicker, GreedyFarthestLMPicker

# Connecting to the database
db = sqlite3.connect('poland.sqlite')
db.enable_load_extension(True)
db.load_extension('libspatialite')
cur = db.cursor()

# Graph definition
G = {}

# Load graph vertices
node_query = "SELECT node_id, AsBinary(geometry) AS point FROM roads_nodes;"
cur.execute(node_query)
nodes = cur.fetchall()
for i, geometry in nodes:
    G[i] = {}

# Load graph edges
road_query = ("SELECT node_from, node_to, oneway_fromto, oneway_tofrom, "
              "GLength(geometry) as length FROM roads;")
cur.execute(road_query)
roads = cur.fetchall()
for node_from, node_to, fromto, tofrom, length in roads:
    # TODO: That's broken, all paths assumed both ways
    # if fromto:
        G[node_from][node_to] = length
    # if tofrom:
        G[node_to][node_from] = length

# We need to decide target now...
src = 1142754
dest = int(sys.argv[1]) if len(sys.argv) > 1 else 224979

# Let's prepare classes
dijkstra = Dijkstra(G, cur)
astar = AStar(G, cur)
astar_landmarks = AStarLandmarks(G, cur, RandomLMPicker)

# Precalculations
dijkstra.precalc(src, dest)
astar.precalc(src, dest)
astar_landmarks.precalc(src, dest, 16)

@timing
def test_dijkstra():
    return dijkstra.calc()

@timing
def test_astar():
    return astar.calc()

@timing
def test_astar_landmarks():
    return astar_landmarks.calc()

dijkstra_path, dijkstra_count = test_dijkstra()
astar_path, astar_count = test_astar()
astar_landmarks_path, astar_landmarks_count = test_astar_landmarks()

def calc_cost(path):
    cost = 0.0
    for i in range(1, len(path)):
        cost += G[path[i - 1]][path[i]]
    return cost


print dijkstra_path == astar_path == astar_landmarks_path

print '%d = %f, %d' % (len(dijkstra_path), calc_cost(dijkstra_path),
                       dijkstra_count)
print '%d = %f, %d' % (len(astar_path), calc_cost(astar_path), astar_count)
print '%d = %f, %d' % (len(astar_landmarks_path),
                       calc_cost(astar_landmarks_path), astar_landmarks_count)
