from .edge_selected import EdgeSelected
from .variable import Variable
import pylp


class NodeAppear(Variable):

    def __init__(self, index, node):

        self.index = index
        self.node = node

    @staticmethod
    def instantiate(solver):

        num_nodes = solver.graph.number_of_nodes()
        indices = solver.allocate_variables(num_nodes)

        appear_indicators = {
            node: NodeAppear(index, node)
            for index, node in zip(indices, solver.graph.nodes)
        }

        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for node in solver.graph.nodes:

            prev_edges = solver.graph.prev_edges(node)

            # Ensure that the following holds:
            #
            # appear = 1 <=> sum(prev_selected) = 0
            # appear = 0 <=> sum(prev_selected) > 0
            #
            # Two linear constraints are needed for that:
            #
            # (1) appear + sum(prev_selected) >= 1
            # (2) appear * num_prev + sum(prev_selected) <= num_prev

            constraint1 = pylp.LinearConstraint()
            constraint2 = pylp.LinearConstraint()

            constraint1.set_coefficient(
                appear_indicators[node].index,
                1.0)
            constraint2.set_coefficient(
                appear_indicators[node].index,
                len(prev_edges))

            for prev_edge in prev_edges:
                constraint1.set_coefficient(
                    edge_indicators[prev_edge].index,
                    1.0)
                constraint2.set_coefficient(
                    edge_indicators[prev_edge].index,
                    1.0)

            constraint1.set_relation(pylp.Relation.GreaterEqual)
            constraint2.set_relation(pylp.Relation.LessEqual)

            constraint1.set_value(1.0)
            constraint2.set_value(len(prev_edges))

            constraints.append(constraint1)
            constraints.append(constraint2)

        return appear_indicators, constraints
