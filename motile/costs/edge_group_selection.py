from __future__ import annotations

from typing import TYPE_CHECKING

from ..variables import EdgeSelected
from ..variables.edge_group import EdgeGroup
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile._types import Edge
    from motile.solver import Solver


class EdgeGroupSelection(Cost):
    """Cost for :class:`~motile.variables.EdgeGroup` variables.

    Associates a cost with each group of edges being selected simultaneously.
    IMPORTANT NOTE: Only one of these can exist! Instantiating a second
    EdgeGroupSelection cost will NOT work! You must accumulate all your groups and costs
    ahead of time and make one cost/set of Variables.

    Args:
        edge_groups (list[tuple[Edge, ...]]):
            A list of edge groups. Each group is a tuple of edges

        costs (list[float]):
            A list of cost values, one per group. Must be the same length as
            ``edge_groups``.

        weight (float):
            The weight to apply to the costs. Default is ``1.0``.

        subtract_base_cost (bool):
            Whether or not to subtract the base edge costs from the group cost.
            Defaults to false. This only makes sense if edges are included in at most 1
            selected group, otherwise the base cost will be subtracted multiple times.
            Also, the base edge costs have to be added to the solver first.

    """

    def __init__(
        self,
        edge_groups: list[tuple[Edge, ...]],
        costs: list[float],
        weight: float = 1.0,
        subtract_base_cost: bool = False,
    ) -> None:
        assert len(edge_groups) == len(costs), (
            f"Length of edge groups ({len(edge_groups)}) and costs "
            f"({len(costs)}) are not equal.)"
        )
        EdgeGroup._edge_groups = edge_groups
        self._group_costs = costs
        self.weight = Weight(weight)
        self.subtract_base_cost = subtract_base_cost

    def apply(self, solver: Solver) -> None:
        edge_group_variables = solver.get_variables(EdgeGroup)
        edge_variables = solver.get_variables(EdgeSelected)

        if self.subtract_base_cost:
            # Read base costs before adding group features.
            # solver.costs caches the result and marks the
            # cache as clean, so we must invalidate it after
            # adding new features below.
            all_costs = solver.costs

        for group, cost in zip(edge_group_variables, self._group_costs):
            base_cost: float = 0
            if self.subtract_base_cost:
                base_cost = sum(all_costs[int(edge_variables[e])] for e in group)
            solver.add_variable_cost(
                edge_group_variables[group],
                cost - base_cost,
                self.weight,
            )

        if self.subtract_base_cost:
            solver._weights_changed = True
