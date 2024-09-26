import motile
from motile.costs import (
    Appear,
    Disappear,
    EdgeSelection,
    NodeSelection,
)


def test_appear_cost(arlo_graph):
    solver = motile.Solver(arlo_graph)

    # Make a slightly negative node cost, and a very positive appear cost and edge
    # cost. We expect only selecting nodes in the first frame, where by default the
    # appear cost is ignored, and not selecting any edges
    solver.add_cost(NodeSelection(weight=0, attribute="score", constant=-1))
    solver.add_cost(Appear(constant=100))
    solver.add_cost(
        EdgeSelection(weight=0, attribute="prediction_distance", constant=100)
    )
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert list(solution_graph.nodes.keys()) == [0, 1]
    assert len(solution_graph.edges) == 0

    ignore_attr = "ignore"
    # now also ignore the appear cost in the second frame
    for second_node in arlo_graph.nodes_by_frame(1):
        arlo_graph.nodes[second_node][ignore_attr] = True
    # but not the third frame
    for third_node in arlo_graph.nodes_by_frame(2):
        arlo_graph.nodes[third_node][ignore_attr] = False

    solver = motile.Solver(arlo_graph)

    # Resolving should also select nodes in second frame
    solver.add_cost(NodeSelection(weight=0, attribute="score", constant=-1))
    solver.add_cost(Appear(constant=100, ignore_attribute=ignore_attr))
    solver.add_cost(
        EdgeSelection(weight=0, attribute="prediction_distance", constant=100)
    )
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert list(solution_graph.nodes.keys()) == [0, 1, 2, 3]
    assert len(solution_graph.edges) == 0


def test_disappear_cost(arlo_graph):
    solver = motile.Solver(arlo_graph)

    # make a slightly negative node cost, and a positive disappear cost and edge cost
    # we expect only selecting nodes in the last frame, where by default the disappear
    # cost is ignored, and not selecting any edges
    solver.add_cost(NodeSelection(weight=0, attribute="score", constant=-1))
    solver.add_cost(Disappear(constant=100))
    solver.add_cost(
        EdgeSelection(weight=0, attribute="prediction_distance", constant=100)
    )
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert list(solution_graph.nodes.keys()) == [4, 5, 6]
    assert len(solution_graph.edges) == 0

    ignore_attr = "ignore"
    # now also ignore the disappear cost in the second frame
    for second_node in arlo_graph.nodes_by_frame(1):
        arlo_graph.nodes[second_node][ignore_attr] = True
    # but not the first frame
    for first_node in arlo_graph.nodes_by_frame(0):
        arlo_graph.nodes[first_node][ignore_attr] = False

    solver = motile.Solver(arlo_graph)

    # Resolving should also select nodes in second frame
    solver.add_cost(NodeSelection(weight=0, attribute="score", constant=-1))
    solver.add_cost(Disappear(constant=100, ignore_attribute=ignore_attr))
    solver.add_cost(
        EdgeSelection(weight=0, attribute="prediction_distance", constant=100)
    )
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert list(solution_graph.nodes.keys()) == [2, 3, 4, 5, 6]
    assert len(solution_graph.edges) == 0
