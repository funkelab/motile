from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeSplit
from .costs import Costs
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Split(Costs):
    """Costs for :class:`~motile.variables.NodeSplit` variables.

    Args:
        weight:
            The weight to apply to the cost of each split.

        attribute:
            The name of the attribute to use to look up costs. Default is
            ``None``, which means that a constant cost is used.

        constant:
            A constant cost for each node that has more than one selected
            child.
    """

    def __init__(
        self, weight: float = 1, attribute: str | None = None, constant: float = 0
    ) -> None:
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute

    def apply(self, solver: Solver) -> None:
        split_indicators = solver.get_variables(NodeSplit)

        for node, index in split_indicators.items():
            if self.attribute is not None:
                solver.add_variable_cost(
                    index, solver.graph.nodes[node][self.attribute], self.weight
                )
            solver.add_variable_cost(index, 1.0, self.constant)
