import motile
import networkx as nx
from motile.costs import (
    Appear,
    Disappear,
    EdgeSelection,
    NodeSelection,
    SymmetricDivision,
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


def test_symmetric_division_cost() -> None:
    """Test that symmetric division cost favors divisions with centered children.

    Graph structure:
        t=0: node 0 at y=10
        t=1: node 1 at y=5, node 2 at y=15, node 3 at y=10

    The symmetric division (0 -> 1,2) should be chosen because the average
    of y=5 and y=15 equals y=10 (the parent's position), resulting in zero cost.
    The alternative division (0 -> 1,3) would have higher cost due to asymmetry.
    """
    # Create nodes
    cells = [
        {"id": 0, "t": 0, "y": 10.0},
        {"id": 1, "t": 1, "y": 5.0},
        {"id": 2, "t": 1, "y": 15.0},
        {"id": 3, "t": 1, "y": 10.0},
    ]

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])

    # Add hyperedge for division (0 -> 1, 2) - the symmetric division
    # Create a hypernode to represent this division
    nx_graph.add_node(10)  # hypernode (no frame attribute)
    nx_graph.add_edge(0, 10)
    nx_graph.add_edge(10, 1)
    nx_graph.add_edge(10, 2)

    # Add hyperedge for division (0 -> 1, 3) - asymmetric division
    nx_graph.add_node(11)  # another hypernode
    nx_graph.add_edge(0, 11)
    nx_graph.add_edge(11, 1)
    nx_graph.add_edge(11, 3)

    # Add hyperedge for division (0 -> 2, 3) - also asymmetric
    nx_graph.add_node(12)  # another hypernode
    nx_graph.add_edge(0, 12)
    nx_graph.add_edge(12, 2)
    nx_graph.add_edge(12, 3)

    graph = motile.TrackGraph(nx_graph)

    solver = motile.Solver(graph)

    # Add only the symmetric division cost
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_cost(SymmetricDivision(position_attribute="y", weight=1.0))

    # Solve and check that the symmetric division is chosen
    solver.solve()
    solution = solver.get_selected_subgraph().to_nx_graph(flatten_hyperedges=True)

    # The solution should select all 4 nodes (0, 1, 2, 3)
    assert set(solution.nodes.keys()) == {0, 1, 2, 3}

    # Check that the symmetric division hyperedge (through hypernode 10) is selected
    # The solution should have edges: 0->1, 0->2
    assert solution.has_edge(0, 1)
    assert solution.has_edge(0, 2)

    # The asymmetric divisions should not be selected
    assert not solution.has_edge(0, 3)
