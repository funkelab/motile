from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    import ilpy
    from ilpy.expressions import Expression

    from motile.solver import Solver


class Constraint(ABC):
    @abstractmethod
    def instantiate(
        self, solver: Solver
    ) -> Iterable[ilpy.LinearConstraint | Expression]:
        """Create and return specific linear constraints for the given solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create linear constraints for.

        Returns:

            An iterable of :class:`ilpy.LinearConstraint`.
        """
