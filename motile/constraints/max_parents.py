from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import ilpy
from ilpy.expressions import Constant

from ..variables import EdgeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from motile.solver import Solver


class MaxParents(Constraint):
    r"""Ensures that every selected node has no more than ``max_parents``.

    Where a "parent" is defined as an incoming selected edge from the previous frame.

    Adds the following linear constraint for each node :math:`v`:

    .. math::

      \sum_{e \in \text{in_edges}(v)} x_e \leq \text{max_parents}

    Args:
        max_parents:
            The maximum number of parents allowed.
    """

    def __init__(self, max_parents: int) -> None:
        self.max_parents = max_parents

    def instantiate(self, solver: Solver) -> Iterable[ilpy.Expression]:
        edge_indicators = solver.get_variables(EdgeSelected)

        for node in solver.graph.nodes:
            # all incoming edges
            s = sum(
                (edge_indicators[e] for e in solver.graph.prev_edges[node]),
                start=Constant(0),
            )
            yield s <= self.max_parents
