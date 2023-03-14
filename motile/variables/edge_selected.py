from __future__ import annotations

from typing import TYPE_CHECKING, Collection

from .variable import Variable

if TYPE_CHECKING:
    from motile._types import EdgeId
    from motile.solver import Solver


class EdgeSelected(Variable[EdgeId]):
    """A binary variable for each edge that indicates whether the edge is part
    of the solution or not.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[EdgeId]:
        return solver.graph.edges
