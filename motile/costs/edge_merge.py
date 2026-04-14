from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import EdgeMerge
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class EdgeMergeCost(Cost):
    """Cost for :class:`~motile.variables.EdgeMerge` variables.

    This cost is applied to edges that are part of a merge (i.e., edges whose
    target node has more than one selected incoming edge).

    Args:
        weight:
            The weight to apply to the cost of each merge edge. Default is ``1``.

        attribute:
            The name of the edge attribute to use to look up the cost. Default
            is ``None``, which means that a constant cost is used.

        constant:
            A constant cost for each merge edge. Default is ``0``.
    """

    def __init__(
        self, weight: float = 1, attribute: str | None = None, constant: float = 0
    ) -> None:
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute

    def apply(self, solver: Solver) -> None:
        edge_merge_indicators = solver.get_variables(EdgeMerge)

        for edge, index in edge_merge_indicators.items():
            if self.attribute is not None:
                solver.add_variable_cost(
                    index, solver.graph.edges[edge][self.attribute], self.weight
                )
            solver.add_variable_cost(index, 1.0, self.constant)
