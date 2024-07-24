from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeDisappear
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Disappear(Cost):
    """Cost for :class:`motile.variables.NodeDisappear` variables.

    Args:
        constant (float):
            A constant cost for each node that ends a track.

        ignore_attribute:
            The name of an optional node attribute that, if it is set and
            evaluates to ``True``, will not set the disappear cost for that
            node. This is useful to allow nodes in the last frame to disappear
            at no cost.
    """

    def __init__(self, constant: float, ignore_attribute: str | None = None) -> None:
        self.constant = Weight(constant)
        self.ignore_attribute = ignore_attribute

    def apply(self, solver: Solver) -> None:
        disappear_indicators = solver.get_variables(NodeDisappear)

        for node, index in disappear_indicators.items():
            if self.ignore_attribute is not None:
                if solver.graph.nodes[node].get(self.ignore_attribute, False):
                    continue
            solver.add_variable_cost(index, 1.0, self.constant)
