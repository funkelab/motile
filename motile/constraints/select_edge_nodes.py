from ..variables import NodeSelected, EdgeSelected
from .constraint import Constraint
import ilpy


class SelectEdgeNodes(Constraint):
    r"""Ensures that if an edge :math:`(u, v)` is selected, :math:`u` and
    :math:`v` have to be selected as well.

    Adds the following linear constraint for each edge :math:`e = (u,v)`:

    .. math::

      2 x_e - x_u - x_v \leq 0

    This constraint will be added by default to any :class:`Solver` instance.
    """

    def _flatten_node_ids(self, edge):
        if isinstance(edge, tuple):
            for x in edge:
                yield from self._flatten_node_ids(x)
        else:
            yield edge

    def instantiate(self, solver):

        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for edge in solver.graph.edges:

            nodes = self._flatten_node_ids(edge)

            ind_e = edge_indicators[edge]
            nodes_ind = [node_indicators[node] for node in nodes]

            constraint = ilpy.LinearConstraint()
            constraint.set_coefficient(ind_e, len(nodes_ind))
            for node_ind in nodes_ind:
                constraint.set_coefficient(node_ind, -1)
            constraint.set_relation(ilpy.Relation.LessEqual)
            constraint.set_value(0)
            constraints.append(constraint)

        return constraints
