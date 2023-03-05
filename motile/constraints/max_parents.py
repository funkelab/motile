from __future__ import annotations
from typing import TYPE_CHECKING

import ilpy

from ..variables import EdgeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from motile.solver import Solver


class MaxParents(Constraint):
    r"""Ensures that every selected node has no more than ``max_parents``
    selected edges to the previous frame.

    Adds the following linear constraint for each node :math:`v`:

    .. math::

      \sum_{e \in \\text{in_edges}(v)} x_e \leq \\text{max_parents}

    Args:

        max_parents (int):
            The maximum number of parents allowed.
    """

    def __init__(self, max_parents: int) -> None:

        self.max_parents = max_parents

    def instantiate(self, solver: Solver) -> list[ilpy.LinearConstraint]:

        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for node in solver.graph.nodes:

            constraint = ilpy.LinearConstraint()

            # all incoming edges
            for edge in solver.graph.prev_edges(node):
                constraint.set_coefficient(edge_indicators[edge], 1)

            # relation, value
            constraint.set_relation(ilpy.Relation.LessEqual)

            constraint.set_value(self.max_parents)
            constraints.append(constraint)

        return constraints
