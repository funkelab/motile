import unittest

import motile
from data import create_arlo_trackgraph
from motile.constraints import ExpressionConstraint, MaxChildren, MaxParents, Pin
from motile.costs import Appear, EdgeSelection, NodeSelection, Split
from motile.variables import EdgeSelected
from motile.variables.node_selected import NodeSelected


class TestConstraints(unittest.TestCase):
    def test_pin(self):
        graph = create_arlo_trackgraph()

        # pin the value of two edges:
        graph.edges[(0, 2)]["pin_to"] = False
        graph.edges[(3, 6)]["pin_to"] = True

        solver = motile.Solver(graph)
        solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
        solver.add_costs(EdgeSelection(weight=1.0, attribute="prediction_distance"))
        solver.add_costs(Appear(constant=200.0))
        solver.add_costs(Split(constant=100.0))
        solver.add_constraints(MaxParents(1))
        solver.add_constraints(MaxChildren(2))
        solver.add_constraints(Pin("pin_to"))

        solution = solver.solve()

        edge_indicators = solver.get_variables(EdgeSelected)

        selected_edges = [
            edge for edge, index in edge_indicators.items() if solution[index] > 0.5
        ]

        assert (0, 2) not in selected_edges
        assert (3, 6) in selected_edges

    def test_complex_expression(self):
        graph = create_arlo_trackgraph()
        graph.nodes[5]["color"] = "red"

        solver = motile.Solver(graph)
        solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
        solver.add_costs(EdgeSelection(weight=1.0, attribute="prediction_distance"))

        # constrain solver based on attributes of nodes/edges
        expr = "x > 140 and t != 1 and color != 'red'"
        solver.add_constraints(ExpressionConstraint(expr))

        solution = solver.solve()
        node_indicators = solver.get_variables(NodeSelected)
        selected_nodes = [
            node for node, index in node_indicators.items() if solution[index] > 0.5
        ]

        assert selected_nodes == [1, 6]
