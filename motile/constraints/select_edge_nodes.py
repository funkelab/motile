from __future__ import annotations

from typing import TYPE_CHECKING

import ilpy

from ..variables import EdgeSelected, NodeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from motile.solver import Solver


class SelectEdgeNodes(Constraint):
    r"""Ensures that if an edge :math:`(u, v)` is selected, :math:`u` and
    :math:`v` have to be selected as well.

    Adds the following linear constraint for each edge :math:`e = (u,v)`:

    .. math::

      2 x_e - x_u - x_v \leq 0

    This constraint will be added by default to any :class:`Solver` instance.
    """

    def instantiate(self, solver: Solver) -> list[ilpy.LinearConstraint]:

        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for edge in solver.graph.edges:

            u, v = edge

            ind_e = edge_indicators[edge]
            ind_u = node_indicators[u]
            ind_v = node_indicators[v]

            constraint = ilpy.LinearConstraint()
            constraint.set_coefficient(ind_e, 2)
            constraint.set_coefficient(ind_u, -1)
            constraint.set_coefficient(ind_v, -1)
            constraint.set_relation(ilpy.Relation.LessEqual)
            constraint.set_value(0)
            constraints.append(constraint)

        return constraints
