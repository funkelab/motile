from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeAppear
from .costs import Costs
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Appear(Costs):
    """Costs for :class:`motile.variables.NodeAppear` variables.

    Args:

        weight (float):
            The weight to apply to the cost of each starting track.

        attribute (string):
            The name of the attribute to use to look up costs. Default is
            ``None``, which means that a constant cost is used.

        constant (float):
            A constant cost for each node that starts a track.
    """

    def __init__(
        self, weight: float = 1, attribute: str | None = None, constant: float = 0
    ) -> None:
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute

    def apply(self, solver: Solver) -> None:
        appear_indicators = solver.get_variables(NodeAppear)

        for node, index in appear_indicators.items():
            if self.attribute is not None:
                solver.add_variable_cost(
                    index, solver.graph.nodes[node][self.attribute], self.weight
                )
            solver.add_variable_cost(index, 1.0, self.constant)
