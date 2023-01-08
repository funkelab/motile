from .variables import NodeSelected, EdgeSelected, NodeAppear
import pylp


class EnsureEdgeEndpoints:
    """If an edge (u, v) is selected, u and v have to be selected as well.

    Constraint:
      2 * edge(u, v) - u - v <= 0
    """

    def instantiate(self, solver):

        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for edge in solver.graph.edges:

            u, v = edge

            ind_e = edge_indicators[edge].index
            ind_u = node_indicators[u].index
            ind_v = node_indicators[v].index

            constraint = pylp.LinearConstraint()
            constraint.set_coefficient(ind_e, 2)
            constraint.set_coefficient(ind_u, -1)
            constraint.set_coefficient(ind_v, -1)
            constraint.set_relation(pylp.Relation.LessEqual)
            constraint.set_value(0)
            constraints.append(constraint)

        return constraints

class ExactlyOneParent:
    """Every selected node has exactly one selected edge to the previous frame
    This includes the special "appear" edge.

    Constraint:
      sum(prev) - node = 0 # exactly one prev edge,
                             iff node selected
    """

    def instantiate(self, solver):

        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)
        appear_indicators = solver.get_variables(NodeAppear)

        constraints = []
        for node in solver.graph.nodes:

            constraint = pylp.LinearConstraint()

            # all neighbors in previous frame
            for edge in solver.graph.prev_edges(node):
                constraint.set_coefficient(edge_indicators[edge].index, 1)

            # plus "appear"
            constraint.set_coefficient(appear_indicators[node].index, 1)

            # node
            constraint.set_coefficient(node_indicators[node].index, -1)

            # relation, value
            constraint.set_relation(pylp.Relation.Equal)

            constraint.set_value(0)
            constraints.append(constraint)

        return constraints
