import random
import sys

from main import connect_to_db, load_graph
from lib.utils import all_bfs

def main():
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'gdansk2.sqlite'

    # Connecting to the database
    cur = connect_to_db(db_name)

    # At first we may remove some silly road classes
    del_query = ("DELETE FROM roads WHERE class IN ('raceway', 'planned', "
                 "'construction', 'proposal')")
    cur.execute(del_query)

    # Load the graph
    G, _, _, _ = load_graph(cur)

    # To make sure we haven't chosen a cutoff node...
    while True:
        # Choose random start node and get BFS results from it
        S = random.choice(G.keys())
        distances = all_bfs([S], G)

        if len(distances) > len(G) / 2: # Fair metric I think...
            break

    removal_ids = set(G.keys()) - set(distances.keys())

    while removal_ids:
        print '%d left...' % len(removal_ids)
        chunk = [str(removal_ids.pop())
                 for i in range(0, min(20, len(removal_ids)))]
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
