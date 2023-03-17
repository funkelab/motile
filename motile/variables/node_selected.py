from __future__ import annotations

from typing import TYPE_CHECKING, Collection

from .variable import Variable

if TYPE_CHECKING:
    from motile._types import NodeId
    from motile.solver import Solver


class NodeSelected(Variable['NodeId']):
    """A binary variable for each node that indicates whether the node is part
    of the solution or not.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[NodeId]:
        return solver.graph.nodes
