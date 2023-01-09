from abc import ABC, abstractmethod


class Variable(ABC):

    @staticmethod
    @abstractmethod
    def instantiate(self, solver):
        """Create and return specific variables (and optionally linear
        constraints) for the given solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create variables (and linear
                constraints) for.

        Returns:

            Either just the created variables or a tuple of variables and a
            list of linear constraints.
        """
        pass
