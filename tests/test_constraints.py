import motile
import pytest
from motile.constraints import (
    ExclusiveNodes,
    ExpressionConstraint,
    MaxChildren,
    MaxParents,
    Pin,
)
from motile.costs import Appear, EdgeSelection, NodeSelection

from .test_api import _selected_edges, _selected_nodes


@pytest.fixture
def solver(arlo_graph):
    return motile.Solver(arlo_graph)


def test_graph_casting(arlo_graph_nx) -> None:
    with pytest.warns(UserWarning, match="Coercing networkx graph to TrackGraph"):
        motile.Solver(arlo_graph_nx)


def test_pin(solver: motile.Solver) -> None:
    # pin the value of two edges:
    solver.graph.edges[(0, 2)]["pin_to"] = False  # type: ignore
    solver.graph.edges[(3, 6)]["pin_to"] = True  # type: ignore

    assert _selected_edges(solver) != [(3, 6)], "test invalid"
    solver.add_constraint(Pin("pin_to"))
    assert _selected_edges(solver) == [(3, 6)]


def test_expression(solver: motile.Solver) -> None:
    solver.graph.nodes[5]["color"] = "red"  # type: ignore
    solver.add_cost(NodeSelection(weight=-1.0, attribute="score", constant=-1))

    assert _selected_nodes(solver) != [1, 6], "test invalid"
    # constrain solver based on attributes of nodes/edges
    expr = "x > 140 and t != 1 and color != 'red'"
    solver.add_constraint(ExpressionConstraint(expr))
    assert _selected_nodes(solver) == [1, 6]


def test_max_children(solver: motile.Solver) -> None:
    solver.add_cost(
        EdgeSelection(weight=1.0, attribute="prediction_distance", constant=-100)
    )

    expect = [(0, 2), (1, 3), (2, 4), (3, 5)]
    assert _selected_edges(solver) != expect, "test invalid"
    solver.add_constraint(MaxChildren(1))
    assert _selected_edges(solver) == expect


def test_max_parents(solver: motile.Solver) -> None:
    solver.add_cost(
        EdgeSelection(weight=1.0, attribute="prediction_distance", constant=-100)
    )

    expect = [(0, 2), (1, 3), (2, 4), (3, 5), (3, 6)]
    assert _selected_edges(solver) != expect, "test invalid"
    solver.add_constraint(MaxParents(1))
    assert _selected_edges(solver) == expect


def test_exlusive_nodes(solver: motile.Solver) -> None:
    exclusive_sets = [
        [0, 1],
        [2, 3],
        [4, 5],
    ]

    solver.add_cost(
        EdgeSelection(weight=1.0, attribute="prediction_distance", constant=-100)
    )
    solver.add_cost(Appear(constant=2.0, attribute="score", weight=0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(2))
    solver.add_constraint(ExclusiveNodes(exclusive_sets))

    assert _selected_nodes(solver) == [1, 3, 5, 6], "test invalid"
