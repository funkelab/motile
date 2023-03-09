from abc import ABC, abstractmethod


class Constraint(ABC):

    @abstractmethod
    def instantiate(self, solver):
        """Create and return specific linear constraints for the given solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create linear constraints for.

        Returns:

            A list of :class:`ilpy.LinearConstraint`.
        """
        pass
