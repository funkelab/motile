from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..variables.edge_continuation_pair import EdgeContinuationPair
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    from motile.solver import Solver
    from motile.track_graph import TrackGraph


class Curvature(Cost):
    """Cost for :class:`~motile.variables.EdgeContinuationPair` variables.

    For each pair of consecutive continuation edges ``(a, b)`` and ``(b, c)``,
    the cost is based on the angle between the two edge vectors. A straight
    continuation (angle = 0) has zero cost; sharper turns have higher cost.

    Specifically, the cost is ``1 - cos(angle)``, which ranges from 0 (straight)
    to 2 (perfect reversal).

    Args:
        position_attribute:
            The name of the node attribute that corresponds to the spatial
            position. Can also be given as a tuple of multiple coordinates,
            e.g., ``('z', 'y', 'x')``.

        weight:
            The weight to apply to the curvature cost. Default is ``1.0``.

        constant:
            A constant cost for each active continuation pair. Default is ``0.0``.
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
        pair_variables = solver.get_variables(EdgeContinuationPair)

        for (e1, e2), index in pair_variables.items():
            a = e1[0]  # source of first edge
            b = e1[1]  # shared middle node (= e2[0])
            c = e2[1]  # target of second edge

            pos_a = self._get_position(solver.graph, a)
            pos_b = self._get_position(solver.graph, b)
            pos_c = self._get_position(solver.graph, c)

            vec1 = pos_b - pos_a
            vec2 = pos_c - pos_b

            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 > 0 and norm2 > 0:
                cos_angle = np.dot(vec1, vec2) / (norm1 * norm2)
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                feature = 1.0 - cos_angle  # 0 = straight, 2 = reversal
            else:
                feature = 0.0

            solver.add_variable_cost(index, feature, self.weight)
            solver.add_variable_cost(index, 1.0, self.constant)

    def _get_position(self, graph: TrackGraph, node: int) -> np.ndarray:
        if isinstance(self.position_attribute, tuple):
            return np.array(
                [graph.nodes[node][p] for p in self.position_attribute],
                dtype=float,
            )
        else:
            return np.array(graph.nodes[node][self.position_attribute], dtype=float)
