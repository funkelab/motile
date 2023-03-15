from __future__ import annotations

from typing import TYPE_CHECKING, Hashable, Sequence

from .variable import Variable

if TYPE_CHECKING:
    from motile.solver import Solver


class EdgeSelected(Variable):
    """A binary variable for each edge that indicates whether the edge is part
    of the solution or not.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Sequence[Hashable]:
        return solver.graph.edges  # type: ignore
