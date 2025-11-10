import motile
import networkx as nx
from motile.costs import EdgeSelection, NodeSelection


def test_empty_graph() -> None:
    """Test that solving an empty graph does not error and returns empty solution."""
    nx_graph = nx.DiGraph()
    graph = motile.TrackGraph(nx_graph)

    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-1))
    solver.add_cost(EdgeSelection(constant=-1))

    # Should not error
    solver.solve()
    solution_graph = solver.get_selected_subgraph()

    # Solution should be empty
    assert len(solution_graph.nodes) == 0
    assert len(solution_graph.edges) == 0


def test_graph_with_no_edges() -> None:
    """Test that solving a graph with nodes but no edges does not error."""
    cells = [
        {"id": 0, "t": 0},
        {"id": 1, "t": 0},
        {"id": 2, "t": 1},
    ]

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    # No edges added

    graph = motile.TrackGraph(nx_graph)

    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-1))
    solver.add_cost(EdgeSelection(constant=-1))

    # Should not error
    solver.solve()
    solution_graph = solver.get_selected_subgraph()

    # All nodes should be selected due to negative cost
    assert set(solution_graph.nodes.keys()) == {0, 1, 2}
    # No edges should be selected (none exist)
    assert len(solution_graph.edges) == 0
