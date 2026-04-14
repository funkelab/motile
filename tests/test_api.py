from unittest.mock import Mock

import motile
import networkx as nx
import pytest
from motile import TrackGraph
from motile.constraints import MaxChildren, MaxParents
from motile.costs import (
    Appear,
    Disappear,
    EdgeDistance,
    EdgeMergeCost,
    EdgeSelection,
    EdgeSplitCost,
    NodeSelection,
    Split,
)
from motile.variables import (
    EdgeContinuation,
    EdgeMerge,
    EdgeSelected,
    EdgeSplit,
    NodeMerge,
    NodeSelected,
    NodeSplit,
)


def _selected_nodes(solver: motile.Solver) -> list:
    node_indicators = solver.get_variables(NodeSelected)
    solution = solver.solve()
    return sorted([n for n, i in node_indicators.items() if solution[i] > 0.5])


def _selected_edges(solver: motile.Solver) -> list:
    edge_indicators = solver.get_variables(EdgeSelected)
    solution = solver.solve()
    return sorted([e for e, i in edge_indicators.items() if solution[i] > 0.5])


def test_graph_creation_from_multiple_nx_graphs(arlo_graph_nx):
    g1 = arlo_graph_nx
    # Create a second graph that overlaps but adds an edge
    g2 = nx.DiGraph()
    g2.add_nodes_from([(cell_id, data) for cell_id, data in g1.nodes(data=True)])
    # Override node 6's x position
    g2.nodes[6]["x"] = 200
    # Add a new edge
    g2.add_edge(0, 2, prediction_distance=1.0)

    graph = motile.TrackGraph()
    graph.add_from_nx_graph(g1)
    assert len(graph.nodes) == 7
    assert len(graph.edges) == 9

    graph.add_from_nx_graph(g2)
    assert len(graph.nodes) == 7
    assert len(graph.edges) == 9  # no new edges since (0,2) already exists
    assert graph.nodes[6]["x"] == 200


def test_graph_to_nx(arlo_graph_nx: nx.DiGraph):
    track_graph = motile.TrackGraph(nx_graph=arlo_graph_nx)
    nx_graph = track_graph.to_nx_graph()
    assert set(arlo_graph_nx.nodes) == set(nx_graph.nodes)
    assert set(arlo_graph_nx.edges) == set(nx_graph.edges)


def test_graph_creation_wrong_frame_attr(arlo_graph_nx):
    with pytest.raises(KeyError):
        motile.TrackGraph(arlo_graph_nx, frame_attribute="time")


def test_solver(arlo_graph):
    graph = arlo_graph

    solver = motile.Solver(graph)
    solver.add_cost(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
    solver.add_cost(
        EdgeSelection(weight=0.5, attribute="prediction_distance", constant=-1.0)
    )
    solver.add_cost(EdgeDistance(position_attribute=("x",), weight=0.5))
    solver.add_cost(Appear(constant=200.0, attribute="score", weight=-1.0))
    solver.add_cost(Disappear(constant=55.0))
    solver.add_cost(Split(constant=100.0, attribute="score", weight=1.0))

    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(2))

    callback = Mock()
    solver.solve(on_event=callback)
    assert callback.call_count
    subgraph = solver.get_selected_subgraph()

    assert (
        list(subgraph.edges)
        == _selected_edges(solver)
        == [(0, 2), (1, 3), (2, 4), (3, 5)]
    )
    assert list(subgraph.nodes) == _selected_nodes(solver) == [0, 1, 2, 3, 4, 5]


def test_edge_types_split_and_merge():
    """Test edge that is simultaneously part of a split and a merge.

    Graph structure:

        0 --- 2
         \\ /
          X      edge (0,3) has src=split node, tgt=merge node
         / \\
        1 --- 3
        t=0   t=1

    Edges: (0,2), (0,3), (1,3)
    Node 0 has 2 outgoing edges -> split node
    Node 3 has 2 incoming edges -> merge node
    Edge (0,3) is both a split edge AND a merge edge

    We use a large negative node selection cost to encourage selecting
    all nodes, and a large negative edge selection cost (on EdgeSelected
    directly, via NodeSelection trick) to encourage selecting all edges.
    MaxChildren(2) and MaxParents(2) allow splits and merges.
    """
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(
        [
            (0, {"t": 0, "x": 0}),
            (1, {"t": 0, "x": 10}),
            (2, {"t": 1, "x": 0}),
            (3, {"t": 1, "x": 10}),
        ]
    )
    nx_graph.add_edges_from([(0, 2), (0, 3), (1, 3)])
    graph = TrackGraph(nx_graph)

    solver = motile.Solver(graph)
    # Large negative costs to encourage selecting everything
    solver.add_cost(NodeSelection(constant=-100.0))
    # EdgeSelection only applies to continuation edges, so also add
    # split and merge costs to incentivize selecting all edge types
    solver.add_cost(EdgeSelection(constant=-100.0))
    solver.add_cost(EdgeSplitCost(constant=-100.0))
    solver.add_cost(EdgeMergeCost(constant=-100.0))
    solver.add_constraint(MaxParents(2))
    solver.add_constraint(MaxChildren(2))

    solution = solver.solve()

    # Check all edges are selected
    edge_indicators = solver.get_variables(EdgeSelected)
    selected_edges = sorted(
        [e for e, i in edge_indicators.items() if solution[i] > 0.5]
    )
    assert selected_edges == [(0, 2), (0, 3), (1, 3)]

    # Check node split/merge indicators
    split_indicators = solver.get_variables(NodeSplit)
    merge_indicators = solver.get_variables(NodeMerge)

    # Node 0 should be a split node (2 outgoing edges selected)
    assert solution[split_indicators[0]] > 0.5, "Node 0 should be a split node"
    # Node 1 should NOT be a split node (only 1 outgoing edge)
    assert solution[split_indicators[1]] < 0.5, "Node 1 should not be a split node"
    # Node 3 should be a merge node (2 incoming edges selected)
    assert solution[merge_indicators[3]] > 0.5, "Node 3 should be a merge node"
    # Node 2 should NOT be a merge node (only 1 incoming edge)
    assert solution[merge_indicators[2]] < 0.5, "Node 2 should not be a merge node"

    # Check edge type indicators
    cont_indicators = solver.get_variables(EdgeContinuation)
    split_edge_indicators = solver.get_variables(EdgeSplit)
    merge_edge_indicators = solver.get_variables(EdgeMerge)

    # Edge (0,2): src is split, tgt is not merge
    #   -> EdgeSplit=1, EdgeMerge=0, EdgeContinuation=0
    assert solution[split_edge_indicators[(0, 2)]] > 0.5, "(0,2) should be a split edge"
    assert solution[merge_edge_indicators[(0, 2)]] < 0.5, (
        "(0,2) should not be a merge edge"
    )
    assert solution[cont_indicators[(0, 2)]] < 0.5, (
        "(0,2) should not be a continuation edge"
    )

    # Edge (1,3): src is not split, tgt is merge
    #   -> EdgeSplit=0, EdgeMerge=1, EdgeContinuation=0
    assert solution[split_edge_indicators[(1, 3)]] < 0.5, (
        "(1,3) should not be a split edge"
    )
    assert solution[merge_edge_indicators[(1, 3)]] > 0.5, "(1,3) should be a merge edge"
    assert solution[cont_indicators[(1, 3)]] < 0.5, (
        "(1,3) should not be a continuation edge"
    )

    # Edge (0,3): src IS split, tgt IS merge
    #   -> EdgeSplit=1, EdgeMerge=1, EdgeContinuation=0
    #   This edge is BOTH a split edge and a merge edge.
    assert solution[split_edge_indicators[(0, 3)]] > 0.5, "(0,3) should be a split edge"
    assert solution[merge_edge_indicators[(0, 3)]] > 0.5, "(0,3) should be a merge edge"
    assert solution[cont_indicators[(0, 3)]] < 0.5, (
        "(0,3) should not be a continuation edge"
    )
