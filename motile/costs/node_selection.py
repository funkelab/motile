from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import NodeSelected
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class NodeSelection(Cost):
    """Cost for :class:`~motile.variables.NodeSelected` variables.

    Args:
        weight:
            The weight to apply to the cost given by the ``cost`` attribute of
            each node.

        attribute:
            The name of the node attribute to use to look up cost. Default is
            ``'cost'``.

        constant:
            A constant cost for each selected node. Default is ``0.0``.
    """

    def __init__(
        self, weight: float, attribute: str = "cost", constant: float = 0.0
    ) -> None:
        self.weight = Weight(weight)
        self.constant = Weight(constant)
        self.attribute = attribute

    def apply(self, solver: Solver) -> None:
        node_variables = solver.get_variables(NodeSelected)

        for node, index in node_variables.items():
            solver.add_variable_cost(
                index, solver.graph.nodes[node][self.attribute], self.weight
            )
            solver.add_variable_cost(index, 1.0, self.constant)
