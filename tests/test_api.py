from data import create_arlo_graph
from motile.constraints import MaxParents, MaxChildren
from motile.costs import NodeSelection, EdgeSelection, Appear, Split
import motile
import unittest


class TestAPI(unittest.TestCase):

    def test_solver(self):

        graph = create_arlo_graph()

        solver = motile.Solver(graph)
        solver.add_costs(
            NodeSelection(
                weight=-1.0,
                attribute='score',
                constant=-100.0))
        solver.add_costs(
            EdgeSelection(
                weight=1.0,
                attribute='prediction_distance'))
        solver.add_costs(Appear(constant=200.0))
        solver.add_costs(Split(constant=100.0))
        solver.add_constraints(MaxParents(1))
        solver.add_constraints(MaxChildren(2))

        solution = solver.solve()

        assert solution.get_value() == -200
