from __future__ import annotations

from typing import TYPE_CHECKING, Collection

from .variable import Variables

if TYPE_CHECKING:
    from motile._types import NodeId
    from motile.solver import Solver


class NodeSelected(Variables["NodeId"]):
    """Binary variable indicating whether a node is part of the solution or not."""

    @staticmethod
    def instantiate(solver: Solver) -> Collection[NodeId]:
        return solver.graph.nodes
