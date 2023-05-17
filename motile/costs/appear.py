from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeAppear
from .costs import Costs
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Appear(Costs):
    """Costs for :class:`~motile.variables.NodeAppear` variables.

    Args:
        constant:
            A constant cost for each node that starts a track.
    """

    def __init__(self, constant: float) -> None:
        self.constant = Weight(constant)

    def apply(self, solver: Solver) -> None:
        appear_indicators = solver.get_variables(NodeAppear)

        for index in appear_indicators.values():
            solver.add_variable_cost(index, 1.0, self.constant)
