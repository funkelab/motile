from __future__ import annotations
from typing import TYPE_CHECKING

from ..variables import NodeAppear
from .costs import Costs

if TYPE_CHECKING:
    from motile.solver import Solver


class Appear(Costs):
    """Costs for :class:`motile.variables.NodeAppear` variables.

    Args:

        constant (float):
            A constant cost for each node that starts a track.
    """

    def __init__(self, constant: float) -> None:

        self.constant = constant

    def apply(self, solver: Solver) -> None:

        appear_indicators = solver.get_variables(NodeAppear)

        for index in appear_indicators.values():
            solver.add_variable_cost(index, self.constant)
