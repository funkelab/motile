import unittest

import motile
from data import *
from motile.constraints import MaxChildren, MaxParents
from motile.costs import Appear, EdgeSelection, NodeSelection, Split


class TestAPI(unittest.TestCase):
    def test_graph_creation_with_hyperedges(self):
        graph = create_toy_hyperedge_trackgraph()
        assert len(graph.nodes)==7
        assert len(graph.edges)==10

    def test_graph_creation_from_multiple_nx_graphs(self):
        g1 = create_toy_hyperedge_nx_graph()
        g2 = create_arlo_nx_graph()
        graph = motile.TrackGraph()

        graph.add_from_nx_graph(g1)
        assert len(graph.nodes)==7
        assert len(graph.edges)==10
        assert graph.nodes[6]['x']==35
        assert 'prediction_distance' not in graph.edges[(0,2)]

        graph.add_from_nx_graph(g2)
        assert len(graph.nodes)==7
        assert len(graph.edges)==11
        assert graph.nodes[6]['x']==200
        assert 'prediction_distance' in graph.edges[(0,2)]

    def test_solver(self):
        graph = create_arlo_trackgraph()

        solver = motile.Solver(graph)
        solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
        solver.add_costs(EdgeSelection(weight=1.0, attribute="prediction_distance"))
        solver.add_costs(Appear(constant=200.0))
        solver.add_costs(Split(constant=100.0))
        solver.add_constraints(MaxParents(1))
        solver.add_constraints(MaxChildren(2))

        solution = solver.solve()

        assert solution.get_value() == -200
