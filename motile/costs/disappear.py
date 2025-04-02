from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeDisappear
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class Disappear(Cost):
    """Cost for :class:`motile.variables.NodeDisappear` variables.

    This is cost is not applied to nodes in the last frame of the graph.

    Args:
        weight:
            The weight to apply to the cost of each ending track. Defaults to 1.

        attribute:
            The name of the attribute to use to look up cost. Default is
            ``None``, which means that a constant cost is used.

        constant:
            A constant cost for each node that starts a track. Defaults to 0.

        ignore_attribute:
            The name of an optional node attribute that, if it is set and
            evaluates to ``True``, will not set the disappear cost for that node.
            Defaults to None.
    """

    def __init__(
        self,
        weight: float = 1,
        attribute: str | None = None,
        constant: float = 0,
        ignore_attribute: str | None = None,
    ):
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute
        self.ignore_attribute = ignore_attribute

    def apply(self, solver: Solver) -> None:
        disappear_indicators = solver.get_variables(NodeDisappear)
        G = solver.graph

        for node, index in disappear_indicators.items():
            if self.ignore_attribute is not None:
                if G.nodes[node].get(self.ignore_attribute, False):
                    continue
            if G.nodes[node][G.frame_attribute] == G.get_frames()[1] - 1:
                continue
            if self.attribute is not None:
                solver.add_variable_cost(
                    index, G.nodes[node][self.attribute], self.weight
                )
            solver.add_variable_cost(index, 1.0, self.constant)
