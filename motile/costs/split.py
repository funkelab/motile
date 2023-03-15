from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeSplit
from .costs import Costs
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Split(Costs):
    """Costs for :class:`motile.variables.NodeSplit` variables.

    Args:

        constant (float):
            A constant cost for each node that has more than one selected
            child.
    """

    def __init__(self, constant: float) -> None:
        self.constant = Weight(constant)

    def apply(self, solver: Solver) -> None:
        split_indicators = solver.get_variables(NodeSplit)

        for index in split_indicators.values():
            solver.add_variable_cost(index, 1.0, self.constant)
