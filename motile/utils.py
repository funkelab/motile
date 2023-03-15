import networkx as nx

from motile.track_graph import TrackGraph


def get_tracks(
    graph: TrackGraph,
    require_selected: bool = False,
    selected_attribute: str = "selected",
) -> list[TrackGraph]:
    """Return a list of track graphs, each corresponding to one track.

    (i.e., a connected component in the track graph).

    Args:
        graph (:class:`TrackGraph`):

            The track graph to split into tracks.

        require_selected (``bool``):

            If ``True``, consider only edges that have a selected_attribute
            attribute that is set to ``True``. Otherwise, each edge will be
            considered for the connected component analysis.

        selected_attribute (``str``):

            Only used if require_selected=True. Determines the attribute
            name to check if an edge is selected. Default value is
            'selected'.

    Returns:

        A generator object of graphs, one for each track.
    """

    if require_selected:
        selected_edges = [
            e
            for e in graph.edges
            if (
                selected_attribute in graph.edges[e]
                and graph.edges[e][selected_attribute]
            )
        ]
        graph = graph.nx_graph.edge_subgraph(selected_edges)

    if len(graph.nodes) == 0:
        return []

    return [
        TrackGraph(
            graph=graph.nx_graph.subgraph(g).copy(),
            frame_attribute=graph.frame_attribute,
        )
        for g in nx.weakly_connected_components(graph)
    ]


def get_networkx_graph(
    graph: TrackGraph,
    require_selected: bool = False,
    selected_attribute: str = "selected",
) -> list[TrackGraph]:
    """Return the physical directed graph (no hyperedges Flo!) as networkx.DiGraph

    Args:
        graph (:class:`TrackGraph`):

            The track graph.

        require_selected (``bool``):

            If ``True``, consider only edges that have a selected_attribute
            attribute that is set to ``True``.

        selected_attribute (``str``):

            Only used if require_selected=True. Determines the attribute
            name to check if an edge is selected. Default value is
            'selected'.

    Returns:

        networkx.DiGraph
    """

    if require_selected:
        selected_edges = [
            e
            for e in graph.edges
            if (
                selected_attribute in graph.edges[e]
                and graph.edges[e][selected_attribute]
            )
        ]

        # TODO edge_subgraph will miss nodes with in- and out-deg 0
        graph = graph.nx_graph.edge_subgraph(selected_edges)
    else:
        graph = graph.nx_graph

    return graph


def create_toy_example_graph():
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
    graph = nx.DiGraph()
    graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])
    return TrackGraph(graph)


if __name__ == "__main__":
    tg = create_toy_example_graph()

    # toy solver
    from motile import Solver
    from motile.constraints import MaxChildren, MaxParents
    from motile.costs import Appear, EdgeSelection, NodeSelection

    solver = Solver(tg)

    # tell it how to compute costs for selecting nodes and edges
    solver.add_costs(NodeSelection(weight=-1.0, attribute="score"))
    solver.add_costs(EdgeSelection(weight=-1.0, attribute="score"))

    # add a small penalty to start a new track
    solver.add_costs(Appear(constant=1.0))

    # add constraints on the solution (no splits, no merges)
    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))

    # solve
    solution = solver.solve()

    # mark solution with attribute
    tg.mark_solution(solver, solution_attribute="selected")

    full_graph = get_networkx_graph(tg)
    print(full_graph)

    sol_graph = get_networkx_graph(
        tg, require_selected=True, selected_attribute="selected"
    )
    print(sol_graph)
