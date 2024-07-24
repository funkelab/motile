import networkx as nx
import pytest
from motile import TrackGraph


@pytest.fixture
def arlo_graph_nx() -> nx.DiGraph:
    """Create the "Arlo graph", a simple toy graph for testing.

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

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])
    return nx_graph


@pytest.fixture
def arlo_graph(arlo_graph_nx) -> TrackGraph:
    """Return the "Arlo graph" as a :class:`motile.TrackGraph` instance."""
    return TrackGraph(arlo_graph_nx)


@pytest.fixture
def toy_graph_nx() -> nx.DiGraph:
    """Return variation of the "Arlo graph".

    Relative to arlo_graph, this graph has:
    - one simple edge modified.
    - normalized node and edge scores.
    - sparse ground truth annotations.

       x
       |
       |       --- 6
       |     /   /
       |   1---3---5
       |     /   x
       |   0---2---4
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
        {"source": 1, "target": 6, "score": 0.5},
        {"source": 2, "target": 4, "score": 0.7, "gt": 1},
        {"source": 3, "target": 5, "score": 0.7},
        {"source": 2, "target": 5, "score": 0.3, "gt": 0},
        {"source": 3, "target": 4, "score": 0.3},
        {"source": 3, "target": 6, "score": 0.8},
    ]
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])
    return nx_graph


@pytest.fixture
def toy_graph(toy_graph_nx) -> TrackGraph:
    """Return the `toy_graph_nx` as a :class:`motile.TrackGraph` instance."""
    return TrackGraph(toy_graph_nx)


@pytest.fixture
def toy_hypergraph_nx() -> nx.DiGraph:
    """Return variation of `toy_graph` with an edge modified and one hyperedge added.

    Visually:

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
        {"id": 6, "t": 2, "x": 35, "score": 0.7, "gt": None},
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
        {"source": 3, "target": 6, "score": 0.8, "gt": None},
    ]

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])  # type: ignore
    nx_graph.add_edges_from(
        [(edge["source"], edge["target"], edge) for edge in edges]  # type: ignore
    )

    # this is how to add a TrackGraph hyperedge into a nx_graph:
    nx_graph.add_node(
        10, division_score=0.1
    )  # is a hypernode, because it has no frame attribute
    nx_graph.add_edge(0, 10)
    nx_graph.add_edge(10, 2)
    nx_graph.add_edge(10, 3)
    return nx_graph


@pytest.fixture
def toy_hypergraph(toy_hypergraph_nx) -> TrackGraph:
    """Return the `toy_hypergraph_nx` as a :class:`motile.TrackGraph` instance."""
    return TrackGraph(toy_hypergraph_nx)
