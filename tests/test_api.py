from unittest.mock import Mock

import motile
from motile.constraints import MaxChildren, MaxParents
from motile.costs import (
    Appear,
    EdgeDistance,
    EdgeSelection,
    NodeSelection,
    Split,
)
from motile.variables import EdgeSelected, NodeSelected


def _selected_nodes(solver: motile.Solver) -> list:
    node_indicators = solver.get_variables(NodeSelected)
    solution = solver.solve()
    return sorted([n for n, i in node_indicators.items() if solution[i] > 0.5])


def _selected_edges(solver: motile.Solver) -> list:
    edge_indicators = solver.get_variables(EdgeSelected)
    solution = solver.solve()
    return sorted([e for e, i in edge_indicators.items() if solution[i] > 0.5])


def test_graph_creation_with_hyperedges(toy_hypergraph):
    graph = toy_hypergraph
    assert len(graph.nodes) == 7
    assert len(graph.edges) == 10


def test_graph_creation_from_multiple_nx_graphs(toy_hypergraph_nx, arlo_graph_nx):
    g1 = toy_hypergraph_nx
    g2 = arlo_graph_nx
    graph = motile.TrackGraph()

    graph.add_from_nx_graph(g1)
    assert len(graph.nodes) == 7
    assert len(graph.edges) == 10
    assert graph.nodes[6]["x"] == 35
    assert "prediction_distance" not in graph.edges[(0, 2)]

    graph.add_from_nx_graph(g2)
    assert len(graph.nodes) == 7
    assert len(graph.edges) == 11
    assert graph.nodes[6]["x"] == 200
    assert "prediction_distance" in graph.edges[(0, 2)]


def test_solver(arlo_graph):
    graph = arlo_graph

    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
    solver.add_cost(
        EdgeSelection(weight=0.5, attribute="prediction_distance", constant=-1.0)
    )
    solver.add_cost(EdgeDistance(position_attribute=("x",), weight=0.5))
    solver.add_cost(Appear(constant=200.0, attribute="score", weight=-1.0))
    solver.add_cost(Split(constant=100.0, attribute="score", weight=1.0))

    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(2))

    callback = Mock()
    solution = solver.solve(on_event=callback)
    assert callback.call_count
    subgraph = solver.get_selected_subgraph()

    assert (
        list(subgraph.edges)
        == _selected_edges(solver)
        == [(0, 2), (1, 3), (2, 4), (3, 5)]
    )
    assert list(subgraph.nodes) == _selected_nodes(solver) == [0, 1, 2, 3, 4, 5]
    cost = solution.get_value()
    assert cost == -206.0, f"{cost=}"
