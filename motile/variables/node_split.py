from .edge_selected import EdgeSelected
from .variable import Variable
import pylp


class NodeSplit(Variable):

    @staticmethod
    def instantiate(solver):

        num_nodes = solver.graph.number_of_nodes()
        indices = solver.allocate_variables(num_nodes)

        split_indicators = {
            node: index
            for node, index in zip(solver.graph.nodes, indices)
        }

        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for node in solver.graph.nodes:

            next_edges = solver.graph.next_edges(node)

            # Ensure that the following holds:
            #
            # split = 0 <=> sum(next_selected) <= 1
            # split = 1 <=> sum(next_selected) > 1
            #
            # Two linear constraints are needed for that:
            #
            # (1) 2 * split - sum(next_selected) <= 0
            # (2) (num_next - 1) * split - sum(next_selected) >= -1

            constraint1 = pylp.LinearConstraint()
            constraint2 = pylp.LinearConstraint()

            constraint1.set_coefficient(
                split_indicators[node],
                2.0)
            constraint2.set_coefficient(
                split_indicators[node],
                len(next_edges) - 1.0)

            for next_edge in next_edges:
                constraint1.set_coefficient(
                    edge_indicators[next_edge],
                    -1.0)
                constraint2.set_coefficient(
                    edge_indicators[next_edge],
                    -1.0)

            constraint1.set_relation(pylp.Relation.LessEqual)
            constraint2.set_relation(pylp.Relation.GreaterEqual)

            constraint1.set_value(0.0)
            constraint2.set_value(-1.0)

            constraints.append(constraint1)
            constraints.append(constraint2)

        return split_indicators, constraints
