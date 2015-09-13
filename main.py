import argparse
import json
from math import sqrt
from multiprocessing import Pool
import os
import random

from colorama import Fore, Style
from shapely import geometry, wkb
import sqlite3

from lib import logger
from lib.utils import pairwise
from pfds import pfds
from visualize import visualize


LOG = logger.getLogger()


def connect_to_db(db_name):
    db_name = os.path.join('data', db_name)
    db = sqlite3.connect(db_name, isolation_level=None)
    db.enable_load_extension(True)
    db.load_extension('libspatialite')
    return db.cursor()


def load_graph(cur):
    # Graph definition
    G = {}  # Graph
    G_reversed = {}  # Graph with reversed edges - for A* landmarks heuristic
    P = {}  # Geographical points
    #L = {}  # Roads geometries,

    # Load graph vertices
    node_qr = "SELECT node_id, AsBinary(geometry) AS point FROM roads_nodes;"
    cur.execute(node_qr)
    nodes = cur.fetchall()
    for i, g in nodes:
        G_reversed[i] = {}
        G[i] = {}
        #L[i] = {}
        P[i] = wkb.loads(str(g))

    # Load graph edges
    # road_qr = ("SELECT node_from, node_to, oneway_fromto, oneway_tofrom, "
    #           "length, AsBinary(geometry) as line FROM roads;")
    road_qr = ("SELECT node_from, node_to, oneway_fromto, oneway_tofrom, "
               "length FROM roads;")
    cur.execute(road_qr)
    roads = cur.fetchall()
    for node_from, node_to, fromto, tofrom, length in roads:
        if fromto:
            G[node_from][node_to] = length
            G_reversed[node_to][node_from] = length
            #L[node_from][node_to] = wkb.loads(str(g))
        if tofrom:
            G[node_to][node_from] = length
            G_reversed[node_from][node_to] = length
            #L[node_to][node_from] = wkb.loads(str(g))

    # Get node closest to the center
    # Get boundary and center of it
    mp = geometry.MultiPoint(P.values())
    center_query = ("SELECT node_id, "
                    "Distance(MakePoint(%f, %f), geometry) as dist "
                    "FROM roads_nodes ORDER BY dist LIMIT 1;" %
                    (mp.centroid.x, mp.centroid.y))
    cur.execute(center_query)
    center, _ = cur.fetchone()

    return G, G_reversed, P, center


def get_pairs(G, filename, rand_num, save):
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

    if save:
        json_pairs = []
        for src, dest in pairs:
            json_pairs.append({'src': src, 'dest': dest})

        with open(filename, 'w') as f:
            json.dump(json_pairs, f)

    return pairs


def baseline_query(G, P, pairs, pfd):
    baseline = {}

    for src, dest in pairs:
        path, visited = pfd.calc(src, dest)

        cost = 0.0
        for i in range(1, len(path)):
            cost += G[path[i - 1]][path[i]]

        baseline['%d-%d' % (src, dest)] = len(visited), cost

    return baseline


def query(G, P, pairs, pfd, runs, baseline):
    results = {}

    i = 0
    while i < runs:
        results[i] = {}
        for src, dest in pairs:
            try:
                path, visited = pfd.calc(src, dest)
            except Exception as e:
                # Okay, this probably won't be useful result...
                LOG.error(str(e))
                i -= 1
                break

            cost = 0.0
            for j in range(1, len(path)):
                cost += G[path[j - 1]][path[j]]

            if cost != baseline['%d-%d' % (src, dest)][1]:
                LOG.error(Fore.RED + "Paths doesn't match!" + Fore.RESET)
                LOG.error(Fore.RED + ("%f != %f" % (cost,
                    baseline['%d-%d' % (src, dest)][1])) + Fore.RESET)

            p = (float(len(visited)) /
                 float(baseline['%d-%d' % (src, dest)][0])) * 100

            results[i]['%d-%d' % (src, dest)] = p

        if runs > 1 and i != runs - 1:
            try:
                pfd.calculate_landmarks()
            except:
                # FIXME: Naive way of trying again
                pfd.calculate_landmarks()

        i += 1

    # We need to flatten the results using average
    flat_results = {}

    for src, dest in pairs:
        k = '%d-%d' % (src, dest)
        avg = 0.
        for i in xrange(runs):
            avg += results[i][k]

        flat_results[k] = avg / runs

    std_dev = {}
    for src, dest in pairs:
        k = '%d-%d' % (src, dest)
        s = 0.
        for i in xrange(runs):
            s += (results[i][k] - flat_results[k]) ** 2

        std_dev[k] = sqrt(s / runs)

    return flat_results, std_dev


def worker(pfd_info, pairs, alg, G, P, center, G_reversed, lm_num, baseline):
    LOG.info(Fore.RED + 'Starting %s tests.' + Style.RESET_ALL, alg)

    try:
        if not pfd_info['lm_picker']:
            pfd = pfd_info['class'](G, P)
        else:
            pfd = pfd_info['class'](G, P, center, G_reversed,
                                    pfd_info['lm_picker'], lm_num)

        return alg, query(G, P, pairs, pfd, pfd_info['runs'], baseline)
    except:
        import traceback
        traceback.print_exc()


def main(pool, db_name, lm_num, tests, filename, results_file, baseline_file,
         save_pairs):
    # Connecting to the database
    cur = connect_to_db(db_name)

    # Load the graph
    G, G_reversed, P, center = load_graph(cur)

    # Decide on vertex pairs for the tests
    pairs = get_pairs(G, filename, tests, save_pairs)
    results = {}

    # A* as baseline first
    LOG.info('Baselining with A*.')
    astar_info = pfds.pop('A*')
    astar = astar_info['class'](G, P)
    baseline = baseline_query(G, P, pairs, astar)
    with open(baseline_file, 'w') as f:
        json.dump(baseline, f)

    # And now test on per-algorithm basis
    for alg, pfd_info in pfds.iteritems():
        def callback(res):
            alg, res = res
            results[alg] = res

        pool.apply_async(worker, args=(pfd_info, pairs, alg, G, P, center,
                                       G_reversed, lm_num, baseline),
                         callback=callback)

    pool.close()
    pool.join()

    # Let's calculate averages
    avgs = {k: 0. for k in pfds.keys()}
    avg_sd = {k: 0. for k in pfds.keys()}
    for alg in pfds.keys():
        for p in results[alg][0].values():
            avgs[alg] += p

        for std in results[alg][1].values():
            avg_sd[alg] += std

        avgs[alg] /= tests
        avg_sd[alg] /= tests

    LOG.info('Average results:')
    for alg, avg in avgs.iteritems():
        LOG.info('%25s: %.2f (std_dev: %.2f)', alg, avg, avg_sd[alg])

    with open(results_file, 'w') as f:
        json.dump(results, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ALT-Tester')

    parser.add_argument('--db', action="store", default='gdansk_cleaned.sqlite')
    parser.add_argument('--landmarks', action="store", type=int, default=16)
    parser.add_argument('--random-pairs', action="store", type=int, default=50)
    parser.add_argument('--pairs-file', action="store")
    parser.add_argument('--processes', action="store", type=int, default=1)
    parser.add_argument('--baseline-file', action="store",
                        default='baseline.json')
    parser.add_argument('--results-file', action="store",
                        default='results.json')
    parser.add_argument('--save-pairs', action="store_true", default=False)

    arguments = parser.parse_args()

    # Create a process pool
    LOG.info('Creating %d processes.', arguments.processes)
    pool = Pool(processes=arguments.processes)

    # Run the program
    main(pool, arguments.db, arguments.landmarks, arguments.random_pairs,
         arguments.pairs_file, arguments.results_file, arguments.baseline_file,
         arguments.save_pairs)
