import sys
import random

from colorama import Fore, Style
from shapely import wkb
import sqlite3

from lib.utils import pairwise

from lib import logger
from lm_pickers.avoid import AvoidLMPicker
from lm_pickers.definied import DefiniedLMPicker
from lm_pickers.rand import RandomLMPicker
from lm_pickers.farthest import FarthestLMPicker, FarthestBLMPicker
from lm_pickers.optimized_farthest import OptimizedFarthestLMPicker
from lm_pickers.optimized_rand import OptimizedRandomLMPicker
from lm_pickers.optimized_planar import OptimizedPlanarLMPicker
from lm_pickers.planar import PlanarLMPicker, PlanarBLMPicker
from path_finders.dijkstra import Dijkstra
from path_finders.astar import AStar
from path_finders.astar_landmarks import AStarLandmarks

from visualize import visualize


LOG = logger.getLogger()

def connect_to_db(db_name):
    db = sqlite3.connect(db_name, isolation_level=None)
    db.enable_load_extension(True)
    db.load_extension('libspatialite')
    return db.cursor()


def load_graph(cur):
    # Graph definition
    G = {}  # Graph
    G_reversed = {}  # Graph with reversed edges - for A* landmarks heuristic
    P = {}  # Geographical points TODO: Node class and geom info in it?
    L = {}  # Roads geometries, TODO: Edge class and geom info in it?

    # Load graph vertices
    node_qr = "SELECT node_id, AsBinary(geometry) AS point FROM roads_nodes;"
    cur.execute(node_qr)
    nodes = cur.fetchall()
    for i, geometry in nodes:
        G_reversed[i] = {}
        G[i] = {}
        L[i] = {}
        P[i] = wkb.loads(str(geometry))

    # Load graph edges
    road_qr = ("SELECT node_from, node_to, oneway_fromto, oneway_tofrom, "
               "length, AsBinary(geometry) as line FROM roads;")
    cur.execute(road_qr)
    roads = cur.fetchall()
    for node_from, node_to, fromto, tofrom, length, geometry in roads:
        if fromto:
            G[node_from][node_to] = length
            G_reversed[node_to][node_from] = length
            L[node_from][node_to] = wkb.loads(str(geometry))
        if tofrom:
            G[node_to][node_from] = length
            G_reversed[node_from][node_to] = length
            L[node_to][node_from] = wkb.loads(str(geometry))

    return G, G_reversed, P, L


def query(G, L, P, src, dest, dijkstra, astar, astar_landmarks):
    dijkstra_path, dijkstra_visited = dijkstra.calc(src, dest)
    astar_path, astar_visited = astar.calc(src, dest)
    astar_landmarks_path, astar_landmarks_visited = astar_landmarks.calc(src,
                                                                         dest)

    def calc_cost(path):
        cost = 0.0
        for i in range(1, len(path)):
            cost += G[path[i - 1]][path[i]]
        return cost

    if not (dijkstra_path == astar_path == astar_landmarks_path):
        LOG.error(Fore.RED + "Paths doesn't match!" + Fore.RESET)
    else:
        LOG.info('    Length: %d', len(dijkstra_path))
        LOG.info('    Cost: %f', calc_cost(dijkstra_path))

    def print_info(alg, visited, ref_visited):
        p = (float(len(visited)) / float(len(ref_visited))) * 100
        LOG.info('    ' + Fore.MAGENTA + '%8s: ' + Fore.RED + '%8d' + Fore.GREEN
                 + ' (%.2f)' + Fore.RESET, alg, len(visited), p)

    print_info('Dijkstra', dijkstra_visited, dijkstra_visited)
    print_info('A*', astar_visited, dijkstra_visited)
    print_info('ALT', astar_landmarks_visited, astar_visited)

    bounds_poland = (13.42529296875, 48.574789910928864, 24.23583984375,
                     55.12864906848878)
    bounds_pomeranian = (16.8365478515625, 53.389880751560284, 19.506225585937,
                         55.05949523049586)
    bounds_gdansk = (18.174, 54.007, 19.113, 54.8351)

    dijkstra_path_geom = [L[a][b] for a, b in pairwise(dijkstra_path)]
    astar_path_geom = [L[a][b] for a, b in pairwise(astar_path)]
    astar_landmarks_path_geom = [L[a][b] for a, b
                                 in pairwise(astar_landmarks_path)]

    # visualize(dijkstra_visited, dijkstra_path_geom, bounds_pomeranian,
    #           'dijkstra')
    # visualize(astar_visited, astar_path_geom, bounds_pomeranian, 'astar')
    # visualize(astar_landmarks_visited, astar_landmarks_path_geom,
    #           bounds_pomeranian, 'astar-lms',
    #           [P[lm] for lm in astar_landmarks.lms])


def main():
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'gdansk_cleaned.sqlite'
    u_src = int(sys.argv[2]) if len(sys.argv) > 2 else None
    u_dest = int(sys.argv[3]) if len(sys.argv) > 3 else None

    # Connecting to the database
    cur = connect_to_db(db_name)

    # Load the graph
    G, G_reversed, P, L = load_graph(cur)

    # Let's prepare classes
    dijkstra = Dijkstra(G, P, cur)
    astar = AStar(G, P, cur)
    astar_landmarks = AStarLandmarks(G, P, cur, G_reversed,
                                     OptimizedPlanarLMPicker, 16)

    runs = 1 if u_dest else 30

    for _ in range(runs):
        if not u_src or not u_dest:
            src = random.choice(G.keys())
            dest = random.choice(G.keys())
        else:
            src = u_src
            dest = u_dest

        LOG.info(Fore.BLUE + Style.DIM + 'From: %d, To: %d' + Style.RESET_ALL,
                 src, dest)
        query(G, L, P, src, dest, dijkstra, astar, astar_landmarks)
if __name__ == '__main__':
    main()
