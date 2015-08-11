from collections import deque, defaultdict
from itertools import tee, izip
from random import choice
from lib import logger

from heap.heap import heap


LOG = logger.getLogger()

def chunks(l, n):
    """ Yield n successive chunks from l.
    """
    n = (len(l) / n) + 1
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def all_dijkstra(S, G):
    frontier = heap([])
    cost_so_far = {}
    for s in S:
        frontier[s] = 0
        cost_so_far[s] = 0

    while len(frontier):
        current = frontier.pop()

        for next in G[current].keys():
            new_cost = cost_so_far[current] + G[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier[next] = priority

    return cost_so_far


def all_bfs(S, G):
    distances = {}
    Q = deque()
    for s in S:
        distances[s] = 0
        Q.append(s)

    while Q:
        v = Q.popleft()
        for n in G[v]:
            if n not in distances:
                Q.append(n)
                distances[n] = distances[v] + 1

    return distances


def all_dijkstra_tree(S, G):
    frontier = heap([S])
    cost_so_far = {S: 0}
    tree = defaultdict(lambda: [])
    order = []

    while len(frontier):
        current = frontier.pop()
        order.append(current)

        for next in G[current].keys():
            new_cost = cost_so_far[current] + G[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier[next] = priority
                tree[current].append(next)

    return cost_so_far, tree, order


def reconstruct_path(came_from, src, dest):
    current = dest
    path = [current]
    while current != src:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def get_single_lower_bound(lm, lm_rev, v, dest):
    def get_dist(mapping, node):
        return mapping[node] if node in mapping else float('inf')

    return max(
        get_dist(lm, dest) - get_dist(lm, v),
        get_dist(lm_rev, v) - get_dist(lm_rev, dest)
    )


def get_lower_bound(lms, lms_rev, v, dest):
    if not lms:
        return 0

    candid = []
    for lm in lms.keys():
        c = get_single_lower_bound(lms[lm], lms_rev[lm], v, dest)
        candid.append(c)

    return abs(max(candid))


def get_lm_distances(G, lms):
    lms_dist = {}

    for lm in lms:
        lms_dist[lm] = all_dijkstra([lm], G)

    return lms_dist


def get_pairs(G):
    pairs = []
    K = G.keys()
    for v in K:
        u = choice(K)
        pairs.append((v, u))

    return pairs


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def optimize_lm(G, G_reversed, lm_num, lms, lm_dists, lm_dists_rev,
                cand_callback, iter_gen):
    # Let's choose a sample of vertex pairs
    LOG.info('Choosing sample...')
    pairs = get_pairs(G)
    LOG.info('Sample choosen.')

    i = 0
    for data in iter_gen:
        LOG.info('Optimizing landmark %d=%d...', i, lms[i])
        LOG.info('    Geting %d candidates...', lm_num)
        # We're getting a lm_num of new candidatesgit gui &

        cands = cand_callback(data, lm_num, lms)

        cands_scores = [0] * lm_num
        cands_dists = get_lm_distances(G, cands)
        cands_dists_rev = get_lm_distances(G_reversed, cands)

        LOG.info('    Choosen candidates: %s.', str(cands))

        # Calculate scores for each candidate
        LOG.info('    Calculating scores for candidates...')
        for S, D in pairs:
            b = get_lower_bound(lm_dists, lm_dists_rev, S, D)

            for j in xrange(lm_num):
                new_b = get_single_lower_bound(cands_dists[cands[j]],
                                               cands_dists_rev[cands[j]],
                                               S, D)
                sc = new_b - b
                if sc > 0:
                    cands_scores[j] += sc
        LOG.info('    Scores calculated.')

        # Replace lm with candidate of max score
        best_i = max(xrange(lm_num), key=lambda k: cands_scores[k])
        best = cands[best_i]
        LOG.info('    Landmark %d considered best.', best)
        if best == lms[i]:
            # If we choosen the same - leave it
            LOG.info('    It is the same, continue.')
            continue
        LOG.info('    Replacing landmark %d with %d', lms[i], best)
        del lm_dists[lms[i]]
        lms[i] = best
        lm_dists[best] = cands_dists[best]
        lm_dists_rev[best] = cands_dists_rev[best]
        i += 1

    return lms, lm_dists, lm_dists_rev
