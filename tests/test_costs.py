import motile
import networkx as nx
from motile.constraints import MaxChildren, MaxParents
from motile.costs import (
    Appear,
    Disappear,
    EdgeMergeCost,
    EdgeSelection,
    EdgeSplitCost,
    Merge,
    NodeSelection,
    Split,
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


def test_edge_split_cost_with_attribute() -> None:
    """Test that EdgeSplitCost can use edge attributes to selectively penalize splits.

    Graph structure:
        t=0: node 0
        t=1: node 1 (split_cost=10.0), node 2 (split_cost=-5.0)
        t=2: node 3, node 4

        edges: 0->1, 0->2, 1->3, 2->4

    Node 0 has two outgoing edges, so selecting both creates a split.
    We use EdgeSplitCost with attribute to make the split edge (0->1)
    expensive and (0->2) cheap. The solver should still select the split
    because the cheap edge outweighs the expensive one overall, but the
    attribute-based cost is being applied.
    """
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(
        [
            (0, {"t": 0, "x": 0}),
            (1, {"t": 1, "x": 10}),
            (2, {"t": 1, "x": -10}),
            (3, {"t": 2, "x": 10}),
            (4, {"t": 2, "x": -10}),
        ]
    )
    nx_graph.add_edges_from(
        [
            (0, 1, {"split_cost": 10.0}),
            (0, 2, {"split_cost": 10.0}),
            (1, 3, {"split_cost": 0.0}),
            (2, 4, {"split_cost": 0.0}),
        ]
    )
    graph = motile.TrackGraph(nx_graph)

    # Without EdgeSplitCost: split is free, both edges selected
    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-100.0))
    solver.add_cost(EdgeSelection(constant=-100.0))
    solver.add_constraint(MaxChildren(2))
    solver.add_constraint(MaxParents(1))
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert (0, 1) in solution_graph.edges
    assert (0, 2) in solution_graph.edges

    # With high attribute-based EdgeSplitCost: split is too expensive
    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-100.0))
    solver.add_cost(EdgeSelection(constant=-100.0))
    solver.add_cost(EdgeSplitCost(attribute="split_cost", weight=5.0))
    solver.add_constraint(MaxChildren(2))
    solver.add_constraint(MaxParents(1))
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    # Only one outgoing edge from node 0 should be selected (no split)
    outgoing_from_0 = [(u, v) for u, v in solution_graph.edges if u == 0]
    assert len(outgoing_from_0) == 1


def test_edge_merge_cost_with_attribute() -> None:
    """Test that EdgeMergeCost can use edge attributes to penalize merges.

    Graph structure:
        t=0: node 0, node 1
        t=1: node 2
        edges: 0->2 (merge_cost=10.0), 1->2 (merge_cost=10.0)

    Without EdgeMergeCost, both edges are selected (merge at node 2).
    With high attribute-based EdgeMergeCost, only one edge is selected.
    """
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(
        [
            (0, {"t": 0}),
            (1, {"t": 0}),
            (2, {"t": 1}),
        ]
    )
    nx_graph.add_edges_from(
        [
            (0, 2, {"merge_cost": 10.0}),
            (1, 2, {"merge_cost": 10.0}),
        ]
    )
    graph = motile.TrackGraph(nx_graph)

    # Without EdgeMergeCost: merge occurs
    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert len(solution_graph.edges) == 2

    # With high attribute-based EdgeMergeCost: merge is too expensive
    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_cost(EdgeMergeCost(attribute="merge_cost", weight=5.0))
    solver.solve()
    solution_graph = solver.get_selected_subgraph()
    assert len(solution_graph.edges) == 1


def test_symmetric_division_cost() -> None:
    """Test that SymmetricDivision cost penalizes asymmetric splits.

    Graph structure (t=0 -> t=1):
        node 0 at x=0 can split to:
          - node 1 at x=-5 and node 2 at x=5   (symmetric: midpoint=0, distance=0)
          - node 1 at x=-5 and node 3 at x=20   (asymmetric: midpoint=7.5, distance=7.5)
          - node 2 at x=5  and node 3 at x=20   (asymmetric: midpoint=12.5)

    With a high SymmetricDivision weight, the solver should prefer the
    symmetric split (nodes 1 and 2) over any asymmetric one.
    """
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(
        [
            (0, {"t": 0, "x": 0}),
            (1, {"t": 1, "x": -5}),
            (2, {"t": 1, "x": 5}),
            (3, {"t": 1, "x": 20}),
        ]
    )
    nx_graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    graph = motile.TrackGraph(nx_graph)

    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-100.0))
    solver.add_cost(EdgeSelection(constant=-100.0))
    solver.add_cost(Split(constant=0.0))
    solver.add_cost(SymmetricDivision(position_attribute="x", weight=50.0))
    solver.add_constraint(MaxChildren(2))
    solver.add_constraint(MaxParents(1))

    solver.solve()
    solution_graph = solver.get_selected_subgraph()

    # The symmetric split (0->1, 0->2) should be chosen
    assert (0, 1) in solution_graph.edges
    assert (0, 2) in solution_graph.edges
    assert (0, 3) not in solution_graph.edges

    # With negative weight, the solver should prefer the most asymmetric split
    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-100.0))
    solver.add_cost(EdgeSelection(constant=-100.0))
    solver.add_cost(Split(constant=0.0))
    solver.add_cost(SymmetricDivision(position_attribute="x", weight=-50.0))
    solver.add_constraint(MaxChildren(2))
    solver.add_constraint(MaxParents(1))

    solver.solve()
    solution_graph = solver.get_selected_subgraph()

    # The most asymmetric split (0->1, 0->3) or (0->2, 0->3) should be chosen
    # (0->2, 0->3) has midpoint=12.5, distance=12.5 — the most asymmetric
    assert (0, 3) in solution_graph.edges
    assert (0, 1) not in solution_graph.edges


def test_symmetric_division_cost_tuple_position() -> None:
    """Test SymmetricDivision with tuple position_attribute.

    Graph structure (t=0 -> t=1):
        node 0 at (y=0, x=0) can split to:
          - node 1 at (y=-3, x=-4) and node 2 at (y=3, x=4)  (symmetric: midpoint=(0,0))
          - node 1 at (y=-3, x=-4) and node 3 at (y=0, x=20)  (asymmetric)

    The symmetric pair should be preferred.
    """
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(
        [
            (0, {"t": 0, "y": 0, "x": 0}),
            (1, {"t": 1, "y": -3, "x": -4}),
            (2, {"t": 1, "y": 3, "x": 4}),
            (3, {"t": 1, "y": 0, "x": 20}),
        ]
    )
    nx_graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    graph = motile.TrackGraph(nx_graph)

    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(constant=-100.0))
    solver.add_cost(EdgeSelection(constant=-100.0))
    solver.add_cost(Split(constant=0.0))
    solver.add_cost(SymmetricDivision(position_attribute=("y", "x"), weight=50.0))
    solver.add_constraint(MaxChildren(2))
    solver.add_constraint(MaxParents(1))

    solver.solve()
    solution_graph = solver.get_selected_subgraph()

    # The symmetric split (0->1, 0->2) should be chosen
    assert (0, 1) in solution_graph.edges
    assert (0, 2) in solution_graph.edges
    assert (0, 3) not in solution_graph.edges
