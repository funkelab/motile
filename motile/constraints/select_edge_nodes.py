from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

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

    def instantiate(self, solver: Solver) -> Iterable[ilpy.LinearConstraint]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        for edge in solver.graph.edges:
            nodes = solver.graph.nodes_of(edge)

            ind_e = edge_indicators[edge]
            nodes_ind = [node_indicators[node] for node in nodes]

            constraint = ilpy.LinearConstraint()
            constraint.set_coefficient(ind_e, len(nodes_ind))
            for node_ind in nodes_ind:
                constraint.set_coefficient(node_ind, -1)
            constraint.set_relation(ilpy.Relation.LessEqual)
            constraint.set_value(0)
            yield constraint
