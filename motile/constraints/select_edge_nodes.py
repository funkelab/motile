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
        for u, v in solver.graph.edges:
            x_e = edge_indicators.expr((u, v), "e")
            x_u = node_indicators.expr(u, "u")
            x_v = node_indicators.expr(v, "v")

            expression = 2 * x_e - x_u - x_v <= 0
            constraints.append(expression.constraint())

        return constraints
