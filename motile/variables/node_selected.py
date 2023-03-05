from __future__ import annotations
from typing import TYPE_CHECKING, Hashable, Sequence

from .variable import Variable

if TYPE_CHECKING:
    from motile.solver import Solver


class NodeSelected(Variable):
    """A binary variable for each node that indicates whether the node is part
    of the solution or not.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Sequence[Hashable]:
        return solver.graph.nodes  # type: ignore
