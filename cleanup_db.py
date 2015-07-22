import random
import sys

from main import connect_to_db, load_graph
from lib import logger
from lib.utils import all_bfs

LOG = logger.getLogger()


def main():
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'gdansk_cleaned.sqlite'

    # Connecting to the database
    cur = connect_to_db(db_name)

    # At first we may remove some silly road classes
    del_query = ("DELETE FROM roads WHERE class IN ('raceway', 'planned', "
                 "'construction', 'proposal')")
    cur.execute(del_query)

    # Load the graph
    G, G_reversed, _, _ = load_graph(cur)

    # To make sure we haven't chosen a cutoff node...
    while True:
        # Choose random start node and get BFS results from it
        S = random.choice(G.keys())
        distances = all_bfs([S], G)

        if len(distances) > len(G) / 2:  # Fair metric I think...
            break

    removal_ids1 = set(G.keys()) - set(distances.keys())

    # Let's do that again on reversed graph
    while True:
        # Choose random start node and get BFS results from it
        S = random.choice(G_reversed.keys())
        distances = all_bfs([S], G_reversed)

        if len(distances) > len(G_reversed) / 2:  # Fair metric I think...
            break

    removal_ids2 = set(G.keys()) - set(distances.keys())

    removal_ids = removal_ids1 | removal_ids2

    while removal_ids:
        LOG.info('%d left...', len(removal_ids))
        chunk = [str(removal_ids.pop())
                 for _ in range(0, min(20, len(removal_ids)))]
        chunk = ','.join(chunk)
        del_query = 'DELETE FROM roads_nodes WHERE node_id IN (%s)' % chunk
        cur.execute(del_query)
        del_query = 'DELETE FROM roads WHERE node_from IN (%s)' % chunk
        cur.execute(del_query)
        del_query = 'DELETE FROM roads WHERE node_to IN (%s)' % chunk
        cur.execute(del_query)

    cur.close()

if __name__ == '__main__':
    main()
