from __future__ import annotations

from typing import TYPE_CHECKING

import ilpy
from ilpy.expressions import Constant

from ..variables import EdgeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from motile.solver import Solver


class MaxChildren(Constraint):
    r"""Ensures that every selected node has no more than ``max_children``
    selected edges to the next frame.

    Adds the following linear constraint for each node :math:`v`:

    .. math::

      \sum_{e \in \\text{out_edges}(v)} x_e \leq \\text{max_children}

    Args:

        max_children (int):
            The maximum number of children allowed.
    """

    def __init__(self, max_children: int) -> None:
        self.max_children = max_children

    def instantiate(self, solver: Solver) -> list[ilpy.LinearConstraint]:
        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for node in solver.graph.nodes:
            n_edges = sum(
                [edge_indicators.expr(e) for e in solver.graph.next_edges[node]],
                Constant(0),
            )
            expr = n_edges <= self.max_children
            constraints.append(expr.constraint())

            # constraint = ilpy.LinearConstraint()
            # # all outgoing edges
            # for edge in solver.graph.next_edges[node]:
            #     constraint.set_coefficient(edge_indicators[edge], 1)

            # relation, value
            # constraint.set_relation(ilpy.Relation.LessEqual)

            # constraint.set_value(self.max_children)
            # constraints.append(constraint)

        return constraints
