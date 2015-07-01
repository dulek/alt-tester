from collections import deque

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
    visited = set()
    distances = {S: 0}
    parents = {}
    Q = deque([S])

    while Q:
        v = Q.popleft()
        for n in G[v]:
            if n not in visited:
                Q.append(n)
                visited.add(n)
                parents[n] = v
                distances[n] = distances[v] + 1

    return distances
