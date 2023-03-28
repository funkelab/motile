from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Collection,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    TypeVar,
)

import ilpy

if TYPE_CHECKING:
    from motile.solver import Solver

_KT = TypeVar("_KT", bound=Hashable)


class Variable(ABC, Mapping[_KT, int]):
    """Base class for solver variables.

    New variables can be introduced by inheriting from this base class and
    overwriting :func:`instantiate` and optionally
    :func:`instantiate_constraints`.

    Variable classes should not be instantiated by a user. Instead, the
    :class:`Solver` provides access to concrete variables through the class
    name. The following example shows how to obtain the variable values after
    optimization::

        solver = Solver(graph)

        # add costs, constraints...

        solution = solver.solve()

        node_selected = solver.get_variables(NodeSelected)

        for node in graph.nodes:
            if solution[node_selected[node]] > 0.5:
                print(f"Node {node} was selected")

    This allows variables to be added lazily to the solver.
    :class:`Constraints<motile.constraints.Constraint>` and
    :class:`motile.costs.Costs` can ask for variables.
    """

    # default variable type, replace in subclasses to override
    variable_type: ClassVar[ilpy.VariableType] = ilpy.VariableType.Binary

    @staticmethod
    @abstractmethod
    def instantiate(solver: Solver) -> Collection[_KT]:
        """Create and return keys for the variables.

        For example, to create a variable for each node, this function would
        return a list of all nodes::

            @staticmethod
            def instantiate(solver):
                return solver.graph.nodes

        The solver will create one variable for each key. The index of that
        variable can be accessed through a dictionary returned by
        :func:`Solver.get_variables`::

            solver = Solver(graph)

            node_selected = solver.get_variables(NodeSelected)

            for node in graph.nodes:
                index = node_selected[node]
                print(f"Selection indicator of node {node} has index {index}")

        Args:

            solver (:class:`Solver`):
                The solver instance to create variables for.

        Returns:

            A list of keys (anything that is hashable, e.g., nodes of a graph),
            one for each variable to create.
        """
        pass

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.LinearConstraint]:
        """Add linear constraints to the solver to ensure that these variables
        are coupled to other variables of the solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create variable constraints for.

        Returns:

            A iterable of :class:`ilpy.LinearConstraint`. See
            :class:`motile.constraints.Constraint` for how to create linear
            constraints.
        """
        return []

    def __init__(self, solver: Solver, index_map: dict[_KT, int]) -> None:
        self._solver = solver
        self._index_map = index_map

    def __repr__(self) -> str:
        rs = []
        for key, index in self._index_map.items():
            r = f"{type(self).__name__}({key}): "
            if index < len(self._solver.costs):
                r += f"cost={self._solver.costs[index]} "
            else:
                r += "cost=None "
            if self._solver.solution is not None and index < len(self._solver.solution):
                r += f"value={self._solver.solution[index]}"
            else:
                r += "value=None"
            rs.append(r)
        return "\n".join(rs)

    def __getitem__(self, key: _KT) -> int:
        return self._index_map[key]

    def __iter__(self) -> Iterator[_KT]:
        return iter(self._index_map)

    def __len__(self) -> int:
        return len(self._index_map)

    # All of these methods are provided by subclassing typing.Mapping
    # __contains__
    # keys
    # items
    # values
    # get
    # __eq__
    # __ne__
