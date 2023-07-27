from __future__ import annotations

from typing import TYPE_CHECKING

import ilpy

from motile.constraints import Constraint
from motile.variables import EdgeSelected, NodeAppear

if TYPE_CHECKING:
    pass


class MinTrackLength(Constraint):
    r"""Ensures that each appearing track consists of at least ``min_edges``
    edges.

    Currently only supports ``min_edges = 1``.

    Args:

        min_edges: The minimum number of edges per track.
    """

    def __init__(self, min_edges: int) -> None:
        if min_edges != 1:
            raise NotImplementedError(
                "Can only enforce minimum track length of 1 edge."
            )
        self.min_edges = min_edges

    def instantiate(self, solver):
        appear_indicators = solver.get_variables(NodeAppear)
        edge_indicators = solver.get_variables(EdgeSelected)
        for node in solver.graph.nodes:
            constraint = ilpy.Constraint()
            constraint.set_coefficient(appear_indicators[node], 1)
            for edge in solver.graph.next_edges[node]:
                constraint.set_coefficient(edge_indicators[edge], -1)
            constraint.set_relation(ilpy.Relation.LessEqual)
            constraint.set_value(0)
            yield constraint
