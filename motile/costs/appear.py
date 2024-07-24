from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeAppear
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Appear(Cost):
    """Cost for :class:`~motile.variables.NodeAppear` variables.

    Args:
        weight:
            The weight to apply to the cost of each starting track.

        attribute:
            The name of the attribute to use to look up cost. Default is
            ``None``, which means that a constant cost is used.

        constant:
            A constant cost for each node that starts a track.

        ignore_attribute:
            The name of an optional node attribute that, if it is set and
            evaluates to ``True``, will not set the appear cost for that node.
            This is useful to allow nodes in the first frame to appear at no
            cost.
    """

    def __init__(
        self,
        weight: float = 1,
        attribute: str | None = None,
        constant: float = 0,
        ignore_attribute: str | None = None,
    ) -> None:
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute
        self.ignore_attribute = ignore_attribute

    def apply(self, solver: Solver) -> None:
        appear_indicators = solver.get_variables(NodeAppear)

        for node, index in appear_indicators.items():
            if self.ignore_attribute is not None:
                if solver.graph.nodes[node].get(self.ignore_attribute, False):
                    continue
            if self.attribute is not None:
                solver.add_variable_cost(
                    index, solver.graph.nodes[node][self.attribute], self.weight
                )
            solver.add_variable_cost(index, 1.0, self.constant)
