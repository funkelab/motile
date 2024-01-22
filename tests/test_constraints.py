import motile
import pytest
from motile.constraints import ExpressionConstraint, MaxChildren, MaxParents, Pin
from motile.costs import EdgeSelection, NodeSelection
from motile.data import arlo_graph

from .test_api import _selected_edges, _selected_nodes


@pytest.fixture
def solver():
    return motile.Solver(arlo_graph())


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
