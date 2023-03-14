import motile
import networkx


def create_nx_graph():
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
        {"source": 1, "target": 2, "score": 0.5},
        {"source": 2, "target": 4, "score": 0.7, "gt": 1},
        {"source": 3, "target": 5, "score": 0.7},
        {"source": 2, "target": 5, "score": 0.3, "gt": 0},
        {"source": 3, "target": 4, "score": 0.3},
        {"source": 3, "target": 6, "score": 0.8},
    ]

    graph = networkx.DiGraph()
    graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])

    # this is how to add a TrackGraph hyperedge into a nx_graph:
    graph.add_node(
        10, {"division_score": 0.1}
    )  # is a hypernode, because no frame attribute
    graph.add_edge(0, 10)
    graph.add_edge(10, 2)
    graph.add_edge(10, 3)

    return graph


def create_hnx_graph():
    # TODO
    pass


if __name__ == "__main__":
    nx_graph = create_nx_graph()
    hnx_graph = create_hnx_graph()

    # from networkx

    track_graph = motile.TrackGraph()
    track_graph.add_from_nx_graph(nx_graph)

    # and also

    track_graph = motile.TrackGraph(nx_graph)

    # optional?
    assert nx_graph == track_graph.to_nx_graph()

    # from hypernetx

    # optional for now:
    track_graph = motile.TrackGraph.from_hnx_graph(hnx_graph)
    # also optional
    assert hnx_graph == track_graph.to_hnx_graph()

    # from thin air

    track_graph = motile.TrackGraph()
    track_graph.add_node(1, {"t": 0, "x": 1, "score": 0.4})
    track_graph.add_node(2, {"t": 1, "x": 10, "score": 0.8})
    track_graph.add_node(3, {"t": 1, "x": 10, "score": 0.8})
    track_graph.add_edge((1, 2), {"score": 0.8})
    # equivalent to:
    # track_graph.add_edge(((1,), (2,)), {'score': 0.8})
    track_graph.add_edge((1, (2, 3)), {"score": 0.5})
    # equivalent to:
    # track_graph.add_edge(((1,), (2, 3)), {'score': 0.5})
