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
from motile.data import (
    arlo_graph,
    arlo_graph_nx,
    toy_hypergraph,
    toy_hypergraph_nx,
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


def test_graph_creation_with_hyperedges():
    graph = toy_hypergraph()
    assert len(graph.nodes) == 7
    assert len(graph.edges) == 10


def test_graph_creation_from_multiple_nx_graphs():
    g1 = toy_hypergraph_nx()
    g2 = arlo_graph_nx()
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


def test_solver():
    graph = arlo_graph()

    solver = motile.Solver(graph)
    solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
    solver.add_costs(
        EdgeSelection(weight=0.5, attribute="prediction_distance", constant=-1.0)
    )
    solver.add_costs(EdgeDistance(position_attributes=("x",), weight=0.5))
    solver.add_costs(Appear(constant=200.0, attribute="score", weight=-1.0))
    solver.add_costs(Split(constant=100.0, attribute="score", weight=1.0))

    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(2))

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
