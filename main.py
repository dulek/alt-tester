import sys
import json
import random

from colorama import Fore, Style
from shapely import wkb
import sqlite3

from lib import logger
from lib.utils import pairwise
from pfds import pfds
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
    P = {}  # Geographical points
    L = {}  # Roads geometries,

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


def get_pairs(G, filename, rand_num):
    pairs = []

    if filename:
        with open(filename) as f:
            json_pairs = json.load(f)

        for pair in json_pairs:
            pairs.append((pair['src'], pair['dest']))

    while len(pairs) < rand_num:
        src = random.choice(G.keys())
        dest = random.choice(G.keys())
        if src != dest:
            pairs.append((src, dest))

    return pairs


def baseline_query(G, L, P, pairs, pfd):
    baseline = {}

    for src, dest in pairs:
        path, visited = pfd.calc(src, dest)

        cost = 0.0
        for i in range(1, len(path)):
            cost += G[path[i - 1]][path[i]]

        baseline['%d-%d' % (src, dest)] = len(visited), cost

    return baseline


def query(G, L, P, pairs, pfd, runs, baseline):
    results = {}

    for i in xrange(runs):
        results[i] = {}
        for src, dest in pairs:
            path, visited = pfd.calc(src, dest)

            cost = 0.0
            for j in range(1, len(path)):
                cost += G[path[j - 1]][path[j]]

            if cost != baseline['%d-%d' % (src, dest)][1]:
                LOG.error(Fore.RED + "Paths doesn't match!" + Fore.RESET)

            p = (float(len(visited)) /
                 float(baseline['%d-%d' % (src, dest)][0])) * 100

            results[i]['%d-%d' % (src, dest)] = p

        if runs > 1 and i != runs - 1:
            pfd.calculate_landmarks()

    # We need to flatten the results using average
    # TODO: Calculating also standard deviation here would be beneficial.
    flat_results = {}

    for src, dest in pairs:
        k = '%d-%d' % (src, dest)
        avg = 0.
        for i in xrange(runs):
            avg += results[i][k]

        flat_results[k] = avg / runs

    return results


def main():
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'gdansk_cleaned.sqlite'
    lm_num = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    tests = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    filename = int(sys.argv[3]) if len(sys.argv) > 3 else None

    # Connecting to the database
    cur = connect_to_db(db_name)

    # Load the graph
    G, G_reversed, P, L = load_graph(cur)

    # Decide on vertex pairs for the tests
    pairs = get_pairs(G, filename, tests)
    results = {}

    # A* as baseline first
    LOG.info('Baselining with A*.')
    astar_info = pfds.pop('A*')
    astar = astar_info['class'](G, P, cur)
    baseline = baseline_query(G, L, P, pairs, astar)

    # And now test on per-algorithm basis
    for alg, pfd_info in pfds.iteritems():
        LOG.info(Fore.RED + 'Starting %s tests.' + Style.RESET_ALL, alg)

        if not pfd_info['lm_picker']:
            pfd = pfd_info['class'](G, P, cur)
        else:
            pfd = pfd_info['class'](G, P, cur, G_reversed,
                                    pfd_info['lm_picker'], lm_num)

        results[alg] = query(G, L, P, pairs, pfd, pfd_info['runs'], baseline)

    # Let's calculate averages
    avgs = {k: 0. for k in pfds.keys()}
    for alg in pfds.keys():
        for p in results[alg].values():
            avgs[alg] += p

        avgs[alg] /= tests

    LOG.info('Average results:')
    for alg, avg in avgs.iteritems():
        LOG.info('%25s: %.2f', alg, avg)

    # TODO: Saving results to JSON file?


if __name__ == '__main__':
    main()
