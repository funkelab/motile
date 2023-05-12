from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from motile.solver import Solver


class Costs(ABC):
    """A base class for costs that can be added to a solver."""

    @abstractmethod
    def apply(self, solver: Solver) -> None:
        """Apply costs to the given solver. Use
        :func:`motile.Solver.get_variables` and
        :func:`motile.Solver.add_variable_cost`.

        Args:
            solver (:class:`Solver`):
                The solver to create costs for.
        """
        pass
