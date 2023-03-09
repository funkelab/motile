import motile
import networkx


def create_arlo_graph():
    '''Create the "Arlo graph", a simple toy graph for testing:

       x
       |
    200|           6
       |         /
    150|   1---3---5
       |     x   x
    100|   0---2---4
        ------------------------------------ t
           0   1   2
    '''

    cells = [
            {'id': 0, 't': 0, 'x': 101, 'score': 1.0},
            {'id': 1, 't': 0, 'x': 150, 'score': 1.0},
            {'id': 2, 't': 1, 'x': 100, 'score': 1.0},
            {'id': 3, 't': 1, 'x': 151, 'score': 1.0},
            {'id': 4, 't': 2, 'x': 102, 'score': 1.0},
            {'id': 5, 't': 2, 'x': 149, 'score': 1.0},
            {'id': 6, 't': 2, 'x': 200, 'score': 1.0}
    ]

    edges = [
        {'source': 0, 'target': 2, 'prediction_distance': 1.0},
        {'source': 1, 'target': 3, 'prediction_distance': 1.0},
        {'source': 0, 'target': 3, 'prediction_distance': 50.0},
        {'source': 1, 'target': 2, 'prediction_distance': 50.0},
        {'source': 2, 'target': 4, 'prediction_distance': 2.0},
        {'source': 3, 'target': 5, 'prediction_distance': 2.0},
        {'source': 2, 'target': 5, 'prediction_distance': 49.0},
        {'source': 3, 'target': 4, 'prediction_distance': 49.0},
        {'source': 3, 'target': 6, 'prediction_distance': 3.0}
    ]

    graph = networkx.DiGraph()
    graph.add_nodes_from([
        (cell['id'], cell)
        for cell in cells
    ])
    graph.add_edges_from([
        (edge['source'], edge['target'], edge)
        for edge in edges
    ])

    return motile.TrackGraph(graph)
