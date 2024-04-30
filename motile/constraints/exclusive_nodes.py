from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ..variables import NodeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    import ilpy

    from motile.solver import Solver


class ExclusiveNodes(Constraint):
    r"""Ensures that for each given set of nodes at most one node is selected.

    Adds the following linear constraint for each given exclusive set :math:`S`:

    .. math::

      \sum_{n \in S} x_n \leq 1

    Args:
        exclusive_sets:
            A list of sets of nodes that are mutually exclusive.
    """

    def __init__(self, exclusive_sets: Iterable[Iterable]) -> None:
        self.exclusive_sets = exclusive_sets

    def instantiate(self, solver: Solver) -> Iterable[ilpy.Expression]:
        node_indicators = solver.get_variables(NodeSelected)
        for exclusive_set in self.exclusive_sets:
            yield sum([node_indicators[n] for n in exclusive_set]) <= 1
