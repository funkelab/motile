from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ilpy
    from motile.solver import Solver


class Constraint(ABC):
    @abstractmethod
    def instantiate(self, solver: Solver) -> list[ilpy.LinearConstraint]:
        """Create and return specific linear constraints for the given solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create linear constraints for.

        Returns:

            A list of :class:`ilpy.LinearConstraint`.
        """
