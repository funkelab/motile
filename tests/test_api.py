from unittest.mock import Mock

import motile
import networkx as nx
import pytest
from motile.constraints import MaxChildren, MaxParents
from motile.costs import (
    Appear,
    Disappear,
    EdgeDistance,
    EdgeSelection,
    NodeSelection,
    Split,
)
from motile.variables import EdgeSelected, NodeSelected


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
