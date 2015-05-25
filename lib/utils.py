from lib.priority_queue import PriorityQueue


def chunks(l, n):
    """ Yield n successive chunks from l.
    """
    n = (len(l) / n) + 1
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def all_dijkstra(S, G):
    frontier = PriorityQueue()
    frontier.put(S, 0)
    cost_so_far = {}
    cost_so_far[S] = 0

    while not frontier.empty():
        current = frontier.get()

        for next in G[current].keys():
            new_cost = cost_so_far[current] + G[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)

    return cost_so_far
