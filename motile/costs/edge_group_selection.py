from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables.edge_group import EdgeGroup
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile._types import Edge
    from motile.solver import Solver


class EdgeGroupSelection(Cost):
    """Cost for :class:`~motile.variables.EdgeGroup` variables.

    Associates a cost with each group of edges being
    selected simultaneously.

    Args:
        edge_groups:
            A list of edge groups. Each group is a tuple
            of edges (``tuple[Edge, ...]``).

        costs:
            A list of cost values, one per group. Must be
            the same length as ``edge_groups``.

        weight:
            The weight to apply to the costs.
            Default is ``1.0``.
    """

    def __init__(
        self,
        edge_groups: list[tuple[Edge, ...]],
        costs: list[float],
        weight: float = 1.0,
    ) -> None:
        EdgeGroup._edge_groups = edge_groups
        self._group_costs = costs
        self.weight = Weight(weight)

    def apply(self, solver: Solver) -> None:
        edge_group_variables = solver.get_variables(EdgeGroup)

        for group, cost in zip(edge_group_variables, self._group_costs):
            solver.add_variable_cost(
                edge_group_variables[group],
                cost,
                self.weight,
            )
