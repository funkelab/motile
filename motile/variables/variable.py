from abc import ABC, abstractmethod


class Variable(ABC):

    @staticmethod
    @abstractmethod
    def instantiate(solver):
        """Create and return variable keys for the given solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create variables for.

        Returns:

            A list of keys (anything that is hashable, e.g., nodes of a graph),
            one for each variable to create.
        """
        pass

    @staticmethod
    def instantiate_constraints(solver):
        return []

    def __init__(self, solver, index_map):
        self._solver = solver
        self._index_map = index_map

    def __repr__(self):

        rs = []
        for key, index in self._index_map.items():
            r = type(self).__name__ + f"({key}): "
            r += f"cost={self._solver.costs[index]} "
            if self._solver.solution is not None:
                r += f"value={self._solver.solution[index]}"
            else:
                r += "value=None"
            rs.append(r)
        return "\n".join(rs)

    def __getitem__(self, key):
        return self._index_map[key]

    def items(self):
        return self._index_map.items()

    def keys(self):
        return self._index_map.keys()

    def values(self):
        return self._index_map.values()
