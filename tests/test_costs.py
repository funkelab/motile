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
)


def test_ignore_attributes():
    graph = arlo_graph()

    # first solve without ignore attribute:

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

    solution = solver.solve()
    no_ignore_value = solution.get_value()

    # solve and ignore appear costs in frame 0

    for first_node in graph.nodes_by_frame(0):
        graph.nodes[first_node]["ignore_appear_cost"] = True

    solver = motile.Solver(graph)
    solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
    solver.add_costs(
        EdgeSelection(weight=0.5, attribute="prediction_distance", constant=-1.0)
    )
    solver.add_costs(EdgeDistance(position_attributes=("x",), weight=0.5))
    solver.add_costs(
        Appear(
            constant=200.0,
            attribute="score",
            weight=-1.0,
            ignore_attribute="ignore_appear_cost",
        )
    )
    solver.add_costs(Split(constant=100.0, attribute="score", weight=1.0))

    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(2))

    solution = solver.solve()
    ignore_value = solution.get_value()

    assert ignore_value < no_ignore_value
