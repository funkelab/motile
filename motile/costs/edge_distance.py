from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np

from ..variables import EdgeSelected
from .costs import Costs
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver


class EdgeDistance(Costs):
    """Costs for :class:`motile.variables.EdgeSelected` variables.

    Costs are based on the spatial distance of the incident nodes.

    Args:
        position_attributes (tuple of string):
            The names of the node attributes that correspond to their spatial
            position, e.g., ``('z', 'y', 'x')``.

        weight (float):
            The weight to apply to the distance to convert it into a cost.
    """

    def __init__(
        self, position_attributes: tuple[str, ...], weight: float = 1.0
    ) -> None:
        self.position_attributes = position_attributes
        self.weight = Weight(weight)

    def apply(self, solver: Solver) -> None:
        edge_variables = solver.get_variables(EdgeSelected)
        for key, index in edge_variables.items():
            u, v = cast("tuple[int, int]", key)
            pos_u = np.array(
                [solver.graph.nodes[u][p] for p in self.position_attributes]
            )
            pos_v = np.array(
                [solver.graph.nodes[v][p] for p in self.position_attributes]
            )

            feature = np.linalg.norm(pos_u - pos_v)

            solver.add_variable_cost(index, feature, self.weight)
