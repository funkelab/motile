import motile
import networkx as nx
from motile.costs import (
    Appear,
    Disappear,
    EdgeSelection,
    Merge,
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


def test_constant_merge_cost() -> None:
    """Test that merge cost prevents merges when applied.

    Graph structure:
        t=0: node 0, node 1
        t=1: node 2
        edges: 0->2, 1->2

    With only negative edge selection cost, both edges should be selected
    (resulting in a merge). Adding a merge cost should prevent the merge,
    resulting in only one edge being selected.
    """
    # Create nodes
    cells = [
        {"id": 0, "t": 0},
        {"id": 1, "t": 0},
        {"id": 2, "t": 1},
    ]

    # Create edges (both leading to node 2, creating potential merge)
    edges = [
        {"source": 0, "target": 2},
        {"source": 1, "target": 2},
    ]

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])

    graph = motile.TrackGraph(nx_graph)

    # First test: without merge cost, both edges should be selected
    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.solve()
    solution_graph = solver.get_selected_subgraph().to_nx_graph()

    # Should select all nodes and both edges (merge occurs)
    assert set(solution_graph.nodes.keys()) == {0, 1, 2}
    assert len(solution_graph.edges) == 2
    assert solution_graph.has_edge(0, 2)
    assert solution_graph.has_edge(1, 2)

    # Second test: with merge cost, only one edge should be selected
    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_cost(Merge(constant=10.0))  # High cost to prevent merge
    solver.solve()
    solution_graph = solver.get_selected_subgraph().to_nx_graph()

    # Should select all nodes but only one edge (no merge)
    assert set(solution_graph.nodes.keys()) == {0, 1, 2}
    assert len(solution_graph.edges) == 1
    # Either edge 0->2 or 1->2 should be selected, but not both
    assert solution_graph.has_edge(0, 2) or solution_graph.has_edge(1, 2)
    assert not (solution_graph.has_edge(0, 2) and solution_graph.has_edge(1, 2))


def test_variable_merge_cost() -> None:
    """Test that merge cost can use node attributes to selectively allow merges.

    Graph structure:
        t=0: node 0, node 1, node 2
        t=1: node 3 (merge_cost=-1.0), node 4 (merge_cost=5.0)
        edges: 0->3, 1->3, 1->4, 2->4

    With negative edge selection cost and attribute-based merge cost,
    only the node with negative merge_cost should have a merge (node 3).
    Node 4 with positive merge_cost should not have a merge.
    """
    # Create nodes - all nodes need merge_cost attribute
    cells = [
        {"id": 0, "t": 0, "merge_cost": 0.0},
        {"id": 1, "t": 0, "merge_cost": 0.0},
        {"id": 2, "t": 0, "merge_cost": 0.0},
        {"id": 3, "t": 1, "merge_cost": -1.0},  # negative cost = good merge
        {"id": 4, "t": 1, "merge_cost": 5.0},  # positive cost = bad merge
    ]

    # Create edges - two edges to each node in time 1 (potential merges)
    edges = [
        {"source": 0, "target": 3},
        {"source": 1, "target": 3},
        {"source": 1, "target": 4},
        {"source": 2, "target": 4},
    ]

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    nx_graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])

    graph = motile.TrackGraph(nx_graph)

    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_cost(Merge(attribute="merge_cost", weight=1.0, constant=0.0))
    solver.solve()
    solution_graph = solver.get_selected_subgraph().to_nx_graph()

    # Should select all nodes
    assert set(solution_graph.nodes.keys()) == {0, 1, 2, 3, 4}

    # Node 3 should have a merge (both edges 0->3 and 1->3 selected)
    # because its merge_cost is negative (-1.0), making the total cost attractive
    assert solution_graph.has_edge(0, 3)
    assert solution_graph.has_edge(1, 3)

    # Node 4 should NOT have a merge (only one edge selected)
    # because its merge_cost is positive (5.0), making the merge too expensive
    edges_to_4 = [
        solution_graph.has_edge(1, 4),
        solution_graph.has_edge(2, 4),
    ]
    assert sum(edges_to_4) == 1  # exactly one edge to node 4
