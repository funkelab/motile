from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..variables.edge_merge_pair import EdgeMergePair
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver
    from motile.track_graph import TrackGraph


class SymmetricMergeCost(Cost):
    """Cost for :class:`~motile.variables.EdgeMergePair` variables.

    For each pair of edges forming a merge, the cost is the euclidean distance
    from the child node's position to the midpoint of the two parents'
    positions. A perfectly symmetric merge (parents equidistant from child)
    has zero cost; asymmetric merges have higher cost.

    Args:
        position_attribute:
            The name of the node attribute that corresponds to the spatial
            position. Can also be given as a tuple of multiple coordinates,
            e.g., ``('z', 'y', 'x')``.

        weight:
            The weight to apply to the distance. Default is ``1.0``.

        constant:
            A constant cost for each active merge group. Default is ``0.0``.
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
        group_variables = solver.get_variables(EdgeMergePair)

        for (e1, e2), index in group_variables.items():
            child = e1[1]  # both edges share the same target
            parent1 = e1[0]
            parent2 = e2[0]

            pos_child = self._get_position(solver.graph, child)
            pos_parent1 = self._get_position(solver.graph, parent1)
            pos_parent2 = self._get_position(solver.graph, parent2)

            midpoint = (pos_parent1 + pos_parent2) / 2.0
            distance = np.linalg.norm(pos_child - midpoint)

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
