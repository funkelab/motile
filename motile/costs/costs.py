from abc import ABC, abstractmethod


class Costs(ABC):

    @abstractmethod
    def apply(self, solver):
        """Apply costs to the given solver. Use
        :func:`motile.Solver.get_variables` and
        :func:`motile.Solver.add_variable_cost`.

        Args:

            solver (:class:`Solver`):
                The solver to create costs for.
        """
        pass
