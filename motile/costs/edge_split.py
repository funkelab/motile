from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import EdgeSplit
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class EdgeSplitCost(Cost):
    """Cost for :class:`~motile.variables.EdgeSplit` variables.

    This cost is applied to edges that are part of a split (i.e., edges whose
    source node has more than one selected outgoing edge).

    Args:
        weight:
            The weight to apply to the cost of each split edge. Default is ``1``.

        attribute:
            The name of the edge attribute to use to look up the cost. Default
            is ``None``, which means that a constant cost is used.

        constant:
            A constant cost for each split edge. Default is ``0``.
    """

    def __init__(
        self, weight: float = 1, attribute: str | None = None, constant: float = 0
    ) -> None:
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute

    def apply(self, solver: Solver) -> None:
        edge_split_indicators = solver.get_variables(EdgeSplit)

        for edge, index in edge_split_indicators.items():
            if self.attribute is not None:
                solver.add_variable_cost(
                    index, solver.graph.edges[edge][self.attribute], self.weight
                )
            solver.add_variable_cost(index, 1.0, self.constant)
