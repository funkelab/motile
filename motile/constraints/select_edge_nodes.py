from ..variables import NodeSelected, EdgeSelected
from .constraint import Constraint
import pylp


class SelectEdgeNodes(Constraint):
    """Ensures that if an edge (u, v) is selected, u and v have to be selected
    as well.

    Adds the following linear constraint for each edge::

      2 * edge(u, v) - u - v <= 0

    This constraint will be added by default to any :class:`Solver` instance.
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
