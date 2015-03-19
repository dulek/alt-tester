import sqlite3
import timeit

from lib.priodict import priorityDictionary


def AStar(G, start, end, H):
    D = {}    # dictionary of final distances
    P = {}    # dictionary of predecessors
    Q = priorityDictionary()   # est.dist. of non-final vert.
    Q[start] = 0

    for v in Q:
        D[v] = Q[v]
        if v == end: break

        for w in G[v]:
            vwLength = D[v] + G[v][w] + H[w]
            if w in D:
                if vwLength < D[w]:
                    raise ValueError()
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v

    return D, P

def shortestPathAStar(G, start, end, H):
    D, P = AStar(G, start, end, H)
    Path = []
    while 1:
        Path.append(end)
        if end == start:
            break
        end = P[end]
    Path.reverse()
    return Path

def Dijkstra(G, start, end):
    D = {}    # dictionary of final distances
    P = {}    # dictionary of predecessors
    Q = priorityDictionary()   # est.dist. of non-final vert.
    Q[start] = 0

    for v in Q:
        D[v] = Q[v]
        if v == end: break

        for w in G[v]:
            vwLength = D[v] + G[v][w]
            if w in D:
                if vwLength < D[w]:
                    raise ValueError()
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v

    return D, P


def shortestPathDijkstra(G, start, end):
    D, P = Dijkstra(G, start, end)
    Path = []
    while 1:
        Path.append(end)
        if end == start:
            break
        end = P[end]
    Path.reverse()
    return Path

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
target = 100000

# Load target node geometry
target_query = ("SELECT AsText(geometry) as geometry FROM roads_nodes "
                "WHERE node_id = %s;" % target)
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

# Get shortest paths
'''dijkstra_time = timeit.Timer('dijkstra_path = shortestPathDijkstra(G, 1, 1000000)',
    'from __main__ import shortestPathDijkstra, G, dijkstra_path').timeit(number=1)
astar_time = timeit.Timer('astar_path = shortestPathAStar(G, 1, 1000000, H)',
    'from __main__ import shortestPathAStar, G, H, astar_path').timeit(number=1)'''

dijkstra_path = shortestPathDijkstra(G, 1, 100000)
astar_path = shortestPathAStar(G, 1, 100000, H)

# print 'Dijkstra: %f s' % dijkstra_time
# print 'A*: %f s' % astar_time

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

