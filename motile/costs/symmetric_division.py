from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..variables.edge_split_group import EdgeSplitGroup
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver
    from motile.track_graph import TrackGraph


class SymmetricDivision(Cost):
    """Cost for :class:`~motile.variables.EdgeSplitGroup` variables.

    For each pair of edges forming a split, the cost is the euclidean distance
    from the parent node's position to the midpoint of the two children's
    positions. A perfectly symmetric division (children equidistant from parent)
    has zero cost; asymmetric divisions have higher cost.

    Args:
        position_attribute:
            The name of the node attribute that corresponds to the spatial
            position. Can also be given as a tuple of multiple coordinates,
            e.g., ``('z', 'y', 'x')``.

        weight:
            The weight to apply to the distance. Default is ``1.0``.

        constant:
            A constant cost for each active split group. Default is ``0.0``.
    """

    def __init__(
        self,
        position_attribute: str | tuple[str, ...],
        weight: float = 1.0,
        constant: float = 0.0,
    ) -> None:
        self.position_attribute = position_attribute
        self.weight = Weight(weight)
        self.constant = Weight(constant)

    def apply(self, solver: Solver) -> None:
        group_variables = solver.get_variables(EdgeSplitGroup)

        for (e1, e2), index in group_variables.items():
            parent = e1[0]  # both edges share the same source
            child1 = e1[1]
            child2 = e2[1]

            pos_parent = self._get_position(solver.graph, parent)
            pos_child1 = self._get_position(solver.graph, child1)
            pos_child2 = self._get_position(solver.graph, child2)

            midpoint = (pos_child1 + pos_child2) / 2.0
            distance = np.linalg.norm(pos_parent - midpoint)

            solver.add_variable_cost(index, distance, self.weight)
            solver.add_variable_cost(index, 1.0, self.constant)

    def _get_position(self, graph: TrackGraph, node: int) -> np.ndarray:
        if isinstance(self.position_attribute, tuple):
            return np.array(
                [graph.nodes[node][p] for p in self.position_attribute],
                dtype=float,
            )
        else:
            return np.array(graph.nodes[node][self.position_attribute], dtype=float)
