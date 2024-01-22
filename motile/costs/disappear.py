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

        ignore_attribute:
            The name of an optional node attribute that, if it is set and
            evaluates to ``True``, will not set the disappear costs for that
            node. This is useful to allow nodes in the last frame to disappear
            at no cost.
    """

    def __init__(self, constant: float) -> None:
        self.constant = Weight(constant)
        self.ignore_attribute = ignore_attribute

    def apply(self, solver: Solver) -> None:
        disappear_indicators = solver.get_variables(NodeDisappear)

        for index in disappear_indicators.values():
            if self.ignore_attribute is not None:
                if solver.graph.nodes[node].get(self.ignore_attribute, False):
                    continue
            solver.add_variable_cost(index, 1.0, self.constant)
