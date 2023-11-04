from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

from motile.expressions import Expression

if TYPE_CHECKING:
    from motile.solver import Solver


class Constraint(ABC):
    """A base class for a constraint that can be added to a solver."""

    @abstractmethod
    def instantiate(self, solver: Solver) -> Iterable[Expression]:
        """Create and return specific linear constraints for the given solver.

        Args:
            solver:
                The :class:`~motile.Solver` instance to create linear constraints for.

        Returns:
            An iterable of :class:`ilpy.Constraint`.
        """
