from __future__ import annotations

from typing import TYPE_CHECKING, Collection

from .variable import Variable

if TYPE_CHECKING:
    from motile._types import Node
    from motile.solver import Solver


class NodeSelected(Variable["Node"]):
    """Binary variable indicating whether a node is part of the solution or not."""

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Node]:
        return solver.graph.nodes
