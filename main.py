import sqlite3
import sys

from lib.priority_queue import PriorityQueue
from lib.timing import timing

def dijkstra_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph[current].keys():
            new_cost = cost_so_far[current] + graph[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

def astar_search(graph, start, goal, H):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph[current].keys():
            new_cost = cost_so_far[current] + graph[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + H[next]
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    return path[::-1]

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
    if fromto:
        G[node_from][node_to] = length
    if tofrom:
        G[node_to][node_from] = length

# We need to decide target now...
source = 1
dest = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000

# Load target node geometry
target_query = ("SELECT AsText(geometry) as geometry FROM roads_nodes "
                "WHERE node_id = %s;" % dest)
cur.execute(target_query)
target = cur.fetchone()

# Load distances to target for each node (basic A* heuristic)
'''heuristic_query = ("SELECT node_id, GeodesicLength(MakeLine(geometry, "
                   "GeomFromText('%s'))) AS distance FROM roads_nodes;" % target[0])'''
heuristic_query = ("SELECT node_id, Distance(geometry, "
                   "GeomFromText('%s')) AS distance FROM roads_nodes;" % target[0])
'''heuristic_query = ("SELECT node_id, Distance(Transform(geometry, 2180), "
                   "Transform(GeomFromText('%s', 4326), 2180)) AS distance FROM "
                   "roads_nodes;" % target[0])'''
cur.execute(heuristic_query)
heuristic = cur.fetchall()

H = {}
for node_id, distance in heuristic:
    H[node_id] = distance;

@timing
def test_dijkstra():
    came_from, cost_so_far = dijkstra_search(G, source, dest)
    dijkstra_path = reconstruct_path(came_from, source, dest)
    return dijkstra_path

@timing
def test_astar():
    came_from, cost_so_far = astar_search(G, source, dest, H)
    astar_path = reconstruct_path(came_from, source, dest)
    return astar_path

# Get shortest paths
'''dijkstra_time = timeit.Timer('test_dijkstra()',
                             'from __main__ import test_dijkstra').timeit(number=3)
astar_time = timeit.Timer('test_astar()',
                          'from __main__ import test_astar').timeit(number=3)

print 'Dijkstra: %f s' % dijkstra_time
print 'A*: %f s' % astar_time'''

dijkstra_path = test_dijkstra()
astar_path = test_astar()

def calc_cost(path):
    cost = 0.0
    for i in range(1, len(path)):
        cost += G[path[i - 1]][path[i]]
    return cost


print dijkstra_path == astar_path
print dijkstra_path
print astar_path

print '%d = %f' % (len(dijkstra_path), calc_cost(dijkstra_path))
print '%d = %f' % (len(astar_path), calc_cost(astar_path))

