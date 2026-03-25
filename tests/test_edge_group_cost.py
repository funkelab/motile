import motile
import networkx as nx
from motile.constraints import MaxChildren, MaxParents
from motile.costs import EdgeSelection
from motile.costs.edge_group_selection import EdgeGroupSelection
from motile.variables import EdgeSelected
from motile.variables.edge_group import EdgeGroup


def _solve_and_get_edges(solver: motile.Solver) -> set:
    edge_indicators = solver.get_variables(EdgeSelected)
    solution = solver.solve()
    return {e for e, i in edge_indicators.items() if solution[i] > 0.5}


def _simple_chain_graph() -> motile.TrackGraph:
    """Create a simple chain graph for testing.

        t=0: 0   1
        t=1: 2   3
        t=2: 4   5

    Edges: 0->2, 0->3, 1->2, 1->3, 2->4, 2->5, 3->4, 3->5
    """
    cells = [
        {"id": 0, "t": 0},
        {"id": 1, "t": 0},
        {"id": 2, "t": 1},
        {"id": 3, "t": 1},
        {"id": 4, "t": 2},
        {"id": 5, "t": 2},
    ]
    edges = [
        {"source": 0, "target": 2},
        {"source": 0, "target": 3},
        {"source": 1, "target": 2},
        {"source": 1, "target": 3},
        {"source": 2, "target": 4},
        {"source": 2, "target": 5},
        {"source": 3, "target": 4},
        {"source": 3, "target": 5},
    ]
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from([(c["id"], c) for c in cells])
    nx_graph.add_edges_from([(e["source"], e["target"], e) for e in edges])
    return motile.TrackGraph(nx_graph)


def test_edge_group_cost_encourages_group():
    """Negative cost encourages selecting all group edges.

    Without the group cost, the solver has no reason to prefer one path over
    another. With a strong negative cost on the group {(0,2), (2,4)}, the
    solver should prefer that specific path.
    """
    graph = _simple_chain_graph()
    solver = motile.Solver(graph)

    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    # Strong negative cost for the group (0->2, 2->4) — should encourage this path
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[((0, 2), (2, 4))],
            costs=[-100.0],
            weight=1.0,
        )
    )

    selected = _solve_and_get_edges(solver)

    # The encouraged path must be selected
    assert (0, 2) in selected
    assert (2, 4) in selected


def test_edge_group_cost_discourages_group():
    """Positive cost discourages selecting all group edges.

    With a high positive cost on the group {(0,2), (2,4)}, the solver should
    avoid selecting both of those edges simultaneously, choosing an alternative
    path instead.
    """
    graph = _simple_chain_graph()
    solver = motile.Solver(graph)

    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    # High positive cost for the group (0->2, 2->4) — should discourage this combo
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[((0, 2), (2, 4))],
            costs=[100.0],
            weight=1.0,
        )
    )

    selected = _solve_and_get_edges(solver)

    # The discouraged pair should not both be selected
    assert not ((0, 2) in selected and (2, 4) in selected)


def test_edge_group_cost_multiple_groups():
    """Test that multiple edge groups can be specified with different costs."""
    graph = _simple_chain_graph()
    solver = motile.Solver(graph)

    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    # Encourage path 0->2->4 and discourage path 1->3->5
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[
                ((0, 2), (2, 4)),
                ((1, 3), (3, 5)),
            ],
            costs=[-100.0, 100.0],
            weight=1.0,
        )
    )

    selected = _solve_and_get_edges(solver)

    # The encouraged path should be selected
    assert (0, 2) in selected
    assert (2, 4) in selected
    # The discouraged pair should not both be selected
    assert not ((1, 3) in selected and (3, 5) in selected)


def test_edge_group_variable_is_one_iff_all_edges_selected():
    """Test the core invariant: group variable = 1 iff all edges in the group are 1.

    We set up a scenario where we can check the group variable value directly
    from the solution to verify the logical coupling is correct.
    """
    graph = _simple_chain_graph()
    solver = motile.Solver(graph)

    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    group = ((0, 2), (2, 4))
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[group],
            costs=[0.0],  # neutral cost — don't bias the solution
            weight=1.0,
        )
    )

    solution = solver.solve()

    edge_indicators = solver.get_variables(EdgeSelected)
    group_indicators = solver.get_variables(EdgeGroup)

    # Check: group var = 1 iff all edges in the group are selected
    group_val = solution[group_indicators[group]] > 0.5
    all_edges_selected = all(solution[edge_indicators[e]] > 0.5 for e in group)
    assert group_val == all_edges_selected


def test_edge_group_cost_with_weight():
    """Test that the weight parameter scales the group costs."""
    graph = _simple_chain_graph()

    # With weight=0, the group cost should have no effect
    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[((0, 2), (2, 4))],
            costs=[1000.0],
            weight=0.0,
        )
    )
    selected_zero_weight = _solve_and_get_edges(solver)

    # With weight=0, the huge positive cost is zeroed out, so the group
    # may still be selected (solver doesn't care about it)
    # We just verify it solves without error and the group isn't necessarily avoided
    assert len(selected_zero_weight) > 0

    # With weight=1, the group cost should take effect and discourage the group
    solver = motile.Solver(graph)
    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[((0, 2), (2, 4))],
            costs=[1000.0],
            weight=1.0,
        )
    )
    selected_with_weight = _solve_and_get_edges(solver)

    # With weight=1, the group should be avoided
    assert not ((0, 2) in selected_with_weight and (2, 4) in selected_with_weight)


def test_edge_group_cost_single_edge_group():
    """Test that a group with a single edge behaves like an extra edge cost."""
    graph = _simple_chain_graph()
    solver = motile.Solver(graph)

    solver.add_cost(EdgeSelection(constant=-1.0))
    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    # Add a very high cost to the single-edge group {(0,2)}
    # This should discourage selecting edge (0,2)
    solver.add_cost(
        EdgeGroupSelection(
            edge_groups=[((0, 2),)],
            costs=[100.0],
            weight=1.0,
        )
    )

    selected = _solve_and_get_edges(solver)
    assert (0, 2) not in selected


def test_edge_group_cost_empty_groups():
    """Test that passing no edge groups is valid and doesn't affect the solution."""
    graph = _simple_chain_graph()

    # Solve without group cost
    solver1 = motile.Solver(graph)
    solver1.add_cost(EdgeSelection(constant=-1.0))
    solver1.add_constraint(MaxParents(1))
    solver1.add_constraint(MaxChildren(1))
    selected1 = _solve_and_get_edges(solver1)

    # Solve with empty group cost
    solver2 = motile.Solver(graph)
    solver2.add_cost(EdgeSelection(constant=-1.0))
    solver2.add_constraint(MaxParents(1))
    solver2.add_constraint(MaxChildren(1))
    solver2.add_cost(
        EdgeGroupSelection(
            edge_groups=[],
            costs=[],
            weight=1.0,
        )
    )
    selected2 = _solve_and_get_edges(solver2)

    assert selected1 == selected2
