from .edge_selected import EdgeSelected
from .node_selected import NodeSelected
from .variable import Variable
import pylp


class NodeAppear(Variable):

    @staticmethod
    def instantiate(solver):
        return solver.graph.nodes

    @staticmethod
    def instantiate_constraints(solver):

        appear_indicators = solver.get_variables(NodeAppear)
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for node in solver.graph.nodes:

            prev_edges = solver.graph.prev_edges(node)
            num_prev_edges = len(prev_edges)

            # Ensure that the following holds:
            #
            # appear = 1 <=> sum(prev_selected) = 0 and selected
            # appear = 0 <=> sum(prev_selected) > 0 or not selected
            #
            # Two linear constraints are needed for that:
            #
            # let s = num_prev * selected - sum(prev_selected)
            # (1) s - appear <= num_prev - 1
            # (2) s - appear * num_prev >= 0

            constraint1 = pylp.LinearConstraint()
            constraint2 = pylp.LinearConstraint()

            # set s for both constraints:

            # num_prev * selected
            constraint1.set_coefficient(
                node_indicators[node],
                num_prev_edges)
            constraint2.set_coefficient(
                node_indicators[node],
                num_prev_edges)

            # - sum(prev_selected)
            for prev_edge in prev_edges:
                constraint1.set_coefficient(
                    edge_indicators[prev_edge],
                    -1.0)
                constraint2.set_coefficient(
                    edge_indicators[prev_edge],
                    -1.0)

            # constraint specific parts:

            # - appear
            constraint1.set_coefficient(
                appear_indicators[node],
                -1.0)

            # - appear * num_prev
            constraint2.set_coefficient(
                appear_indicators[node],
                -num_prev_edges)

            constraint1.set_relation(pylp.Relation.LessEqual)
            constraint2.set_relation(pylp.Relation.GreaterEqual)

            constraint1.set_value(num_prev_edges - 1)
            constraint2.set_value(0)

            constraints.append(constraint1)
            constraints.append(constraint2)

        return constraints
