from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeDisappear
from .costs import Costs
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Disappear(Costs):
    """Costs for :class:`motile.variables.NodeDisappear` variables.

    Args:

        constant (float):
            A constant cost for each node that ends a track.
    """

    def __init__(self, constant: float) -> None:
        self.constant = Weight(constant)

    def apply(self, solver: Solver) -> None:
        disappear_indicators = solver.get_variables(NodeDisappear)

        for index in disappear_indicators.values():
            solver.add_variable_cost(index, 1.0, self.constant)
