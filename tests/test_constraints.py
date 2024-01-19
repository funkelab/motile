import motile
import pytest
from motile.constraints import (
    ExpressionConstraint,
    InOutSymmetry,
    MaxChildren,
    MaxParents,
    MinTrackLength,
    Pin,
)
from motile.costs import EdgeSelection, NodeSelection
from motile.data import arlo_graph, toy_graph
from motile.variables import EdgeSelected
from motile.variables.node_selected import NodeSelected


@pytest.fixture
def solver():
    return motile.Solver(arlo_graph())


def _selected_edges(solver: motile.Solver) -> list:
    edge_indicators = solver.get_variables(EdgeSelected)
    solution = solver.solve()
    return [e for e, i in edge_indicators.items() if solution[i]]


def _selected_nodes(solver: motile.Solver) -> list:
    node_indicators = solver.get_variables(NodeSelected)
    solution = solver.solve()
    return [e for e, i in node_indicators.items() if solution[i]]


def test_pin(solver: motile.Solver) -> None:
    # pin the value of two edges:
    solver.graph.edges[(0, 2)]["pin_to"] = False  # type: ignore
    solver.graph.edges[(3, 6)]["pin_to"] = True  # type: ignore

    assert _selected_edges(solver) != [(3, 6)], "test invalid"
    solver.add_constraints(Pin("pin_to"))
    assert _selected_edges(solver) == [(3, 6)]


def test_expression(solver: motile.Solver) -> None:
    solver.graph.nodes[5]["color"] = "red"  # type: ignore
    solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-1))

    assert _selected_nodes(solver) != [1, 6], "test invalid"
    # constrain solver based on attributes of nodes/edges
    expr = "x > 140 and t != 1 and color != 'red'"
    solver.add_constraints(ExpressionConstraint(expr))
    assert _selected_nodes(solver) == [1, 6]


def test_max_children(solver: motile.Solver) -> None:
    solver.add_costs(
        EdgeSelection(weight=1.0, attribute="prediction_distance", constant=-100)
    )

    expect = [(0, 2), (1, 3), (2, 4), (3, 5)]
    assert _selected_edges(solver) != expect, "test invalid"
    solver.add_constraints(MaxChildren(1))
    assert _selected_edges(solver) == expect


def test_max_parents(solver: motile.Solver) -> None:
    solver.add_costs(
        EdgeSelection(weight=1.0, attribute="prediction_distance", constant=-100)
    )

    expect = [(0, 2), (1, 3), (2, 4), (3, 5), (3, 6)]
    assert _selected_edges(solver) != expect, "test invalid"
    solver.add_constraints(MaxParents(1))
    assert _selected_edges(solver) == expect


def test_in_out_symmetry():
    graph = toy_graph()
    solver = motile.Solver(graph)

    solver.add_costs(NodeSelection(weight=-1.0, attribute="score"))
    solver.add_costs(EdgeSelection(weight=-1.0, attribute="score"))
    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))
    solver.add_constraints(InOutSymmetry())

    solution = solver.solve()

    node_indicators = solver.get_variables(NodeSelected)
    selected_nodes = [
        node for node, index in node_indicators.items() if solution[index] > 0.5
    ]
    edge_indicators = solver.get_variables(EdgeSelected)
    selected_edges = [
        edge for edge, index in edge_indicators.items() if solution[index] > 0.5
    ]
    for node in solver.graph.nodes:
        assert node in selected_nodes

    assert (1, 3) in selected_edges
    assert (3, 6) in selected_edges
    assert (0, 2) in selected_edges
    assert (2, 4) in selected_edges


def test_min_track_length():
    graph = toy_graph()
    solver = motile.Solver(graph)

    solver.add_costs(NodeSelection(weight=-1.0, attribute="score"))
    solver.add_costs(EdgeSelection(weight=-1.0, attribute="score"))
    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))
    solver.add_constraints(MinTrackLength(1))

    solution = solver.solve()

    node_indicators = solver.get_variables(NodeSelected)
    selected_nodes = [
        node for node, index in node_indicators.items() if solution[index] > 0.5
    ]
    for node in solver.graph.nodes:
        if node == 5:
            assert node not in selected_nodes
        else:
            assert node in selected_nodes


if __name__ == "__main__":
    test_in_out_symmetry()
