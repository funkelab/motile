import motile
import networkx


def create_arlo_nx_graph() -> networkx.DiGraph:
    """Create the "Arlo graph", a simple toy graph for testing:

       x
       |
    200|           6
       |         /
    150|   1---3---5
       |     x   x
    100|   0---2---4
        ------------------------------------ t
           0   1   2
    """

    cells = [
        {"id": 0, "t": 0, "x": 101, "score": 1.0},
        {"id": 1, "t": 0, "x": 150, "score": 1.0},
        {"id": 2, "t": 1, "x": 100, "score": 1.0},
        {"id": 3, "t": 1, "x": 151, "score": 1.0},
        {"id": 4, "t": 2, "x": 102, "score": 1.0},
        {"id": 5, "t": 2, "x": 149, "score": 1.0},
        {"id": 6, "t": 2, "x": 200, "score": 1.0},
    ]

    edges = [
        {"source": 0, "target": 2, "prediction_distance": 1.0},
        {"source": 1, "target": 3, "prediction_distance": 1.0},
        {"source": 0, "target": 3, "prediction_distance": 50.0},
        {"source": 1, "target": 2, "prediction_distance": 50.0},
        {"source": 2, "target": 4, "prediction_distance": 2.0},
        {"source": 3, "target": 5, "prediction_distance": 2.0},
        {"source": 2, "target": 5, "prediction_distance": 49.0},
        {"source": 3, "target": 4, "prediction_distance": 49.0},
        {"source": 3, "target": 6, "prediction_distance": 3.0},
    ]

    nx_graph = networkx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])
    return nx_graph


def create_arlo_trackgraph() -> motile.TrackGraph:
    return motile.TrackGraph(create_arlo_nx_graph())


def create_toy_example_nx_graph() -> networkx.DiGraph:
    cells = [
        {"id": 0, "t": 0, "x": 1, "score": 0.8, "gt": 1},
        {"id": 1, "t": 0, "x": 25, "score": 0.1},
        {"id": 2, "t": 1, "x": 0, "score": 0.3, "gt": 1},
        {"id": 3, "t": 1, "x": 26, "score": 0.4},
        {"id": 4, "t": 2, "x": 2, "score": 0.6, "gt": 1},
        {"id": 5, "t": 2, "x": 24, "score": 0.3, "gt": 0},
        {"id": 6, "t": 2, "x": 35, "score": 0.7},
    ]

    edges = [
        {"source": 0, "target": 2, "score": 0.9, "gt": 1},
        {"source": 1, "target": 3, "score": 0.9},
        {"source": 0, "target": 3, "score": 0.5},
        {"source": 1, "target": 6, "score": 0.5},
        {"source": 2, "target": 4, "score": 0.7, "gt": 1},
        {"source": 3, "target": 5, "score": 0.7},
        {"source": 2, "target": 5, "score": 0.3, "gt": 0},
        {"source": 3, "target": 4, "score": 0.3},
        {"source": 3, "target": 6, "score": 0.8},
    ]
    nx_graph = networkx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])
    return nx_graph


def create_toy_example_trackgraph() -> motile.TrackGraph:
    return motile.TrackGraph(create_toy_example_nx_graph())


def create_toy_hyperedge_nx_graph() -> networkx.DiGraph:
    """Create variation of the "Arlo graph", with one simple
    edge modified and one hyperedge added.

       x
       |
       |       --- 6
       |     /   /
       |   1---3---5
       |     /   x
       |   0---2---4  Hyperedge: (0,(2,3))
        ------------------------------------ t
           0   1   2
    """
    cells = [
        {"id": 0, "t": 0, "x": 1, "score": 0.8, "gt": 1},
        {"id": 1, "t": 0, "x": 25, "score": 0.1},
        {"id": 2, "t": 1, "x": 0, "score": 0.3, "gt": 1},
        {"id": 3, "t": 1, "x": 26, "score": 0.4},
        {"id": 4, "t": 2, "x": 2, "score": 0.6, "gt": 1},
        {"id": 5, "t": 2, "x": 24, "score": 0.3, "gt": 0},
        {"id": 6, "t": 2, "x": 35, "score": 0.7},
    ]

    edges = [
        {"source": 0, "target": 2, "score": 0.9, "gt": 1},
        {"source": 1, "target": 3, "score": 0.9},
        {"source": 0, "target": 3, "score": 0.5},
        {"source": 1, "target": 6, "score": 0.2},
        {"source": 2, "target": 4, "score": 0.7, "gt": 1},
        {"source": 3, "target": 5, "score": 0.7},
        {"source": 2, "target": 5, "score": 0.3, "gt": 0},
        {"source": 3, "target": 4, "score": 0.3},
        {"source": 3, "target": 6, "score": 0.8},
    ]
    nx_graph = networkx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])

    # this is how to add a TrackGraph hyperedge into a nx_graph:
    nx_graph.add_node(
        10, division_score=0.1
    )  # is a hypernode, because it has no frame attribute
    nx_graph.add_edge(0, 10)
    nx_graph.add_edge(10, 2)
    nx_graph.add_edge(10, 3)
    return nx_graph


def create_toy_hyperedge_trackgraph() -> motile.TrackGraph:
    return motile.TrackGraph(create_toy_hyperedge_nx_graph())
