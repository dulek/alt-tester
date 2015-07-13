from collections import deque, defaultdict

from heap.heap import heap

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
    parents = {}

    while len(frontier):
        current = frontier.pop()

        for next in G[current].keys():
            new_cost = cost_so_far[current] + G[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier[next] = priority
                tree[current].append(next)
                parents[next] = current

    return cost_so_far, tree, parents


def reconstruct_path(came_from, src, dest):
    current = dest
    path = [current]
    while current != src:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def get_lower_bound(lms, lms_rev, v, dest):
    def get_dist(mapping, node):
        return mapping[node] if node in mapping else float('inf')

    candid = []
    for lm in lms.keys():
        c = max(
            get_dist(lms[lm], dest) - get_dist(lms[lm], v),
            get_dist(lms_rev[lm], v) - get_dist(lms_rev[lm], dest)
        )
        candid.append(c)

    return abs(max(candid))

def get_lm_distances(G, lms):
    lms_dist = {}

    for lm in lms:
        lms_dist[lm] = all_dijkstra([lm], G)

    return lms_dist
