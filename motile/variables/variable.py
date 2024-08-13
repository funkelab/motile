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


class Variable(ABC, Mapping[_KT, ilpy.Variable]):
    """Base class for solver variables.

    New variables can be introduced by inheriting from this base class and
    overwriting :func:`instantiate` and optionally
    :func:`instantiate_constraints`.

    Variable classes should not be instantiated by a user. Instead, the
    :class:`~motile.Solver` provides access to concrete variables through the class
    name. The following example shows how to obtain the variable values after
    optimization::

        solver = Solver(graph)

        # add costs, constraints...

        solution = solver.solve()

        # here `node_selected` is an instance of a Variable subclass
        # specifically, it will be an instance of NodeSelected, which
        # maps node Ids to variables in the solver.
        node_selected = solver.get_variables(NodeSelected)

        for node in graph.nodes:
            if solution[node_selected[node]] > 0.5:
                print(f"Node {node} was selected")

    This allows variables to be added lazily to the solver.
    :class:`Constraints<motile.constraints.Constraint>` and
    :class:`motile.costs.Cost` can ask for variables.
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
        :meth:`motile.Solver.get_variables`::

            solver = Solver(graph)

            node_selected = solver.get_variables(NodeSelected)

            for node in graph.nodes:
                index = node_selected[node]
                print(f"Selection indicator of node {node} has index {index}")

        Args:
            solver:
                The :class:`~motile.Solver` instance to create variables for.

        Returns:
            A collection of keys (anything that is hashable, e.g., nodes of a graph),
            one for each variable to create.
        """
        pass

    @staticmethod
    def instantiate_constraints(
        solver: Solver,
    ) -> Iterable[ilpy.Constraint | ilpy.Expression]:
        """Add constraints for this variable to the solver.

        This ensures that these variables are coupled to other variables of the solver.

        Args:
            solver:
                The :class:`~motile.Solver` instance to create variable constraints for.

        Returns:
            A iterable of :class:`ilpy.Constraint` or
            :class:`ilpy.expressions.Expression.` See
            :class:`motile.constraints.Constraint` for how to create linear constraints.
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

    def __getitem__(self, key: _KT) -> ilpy.Variable:
        name = f"{type(self).__name__}({key})"
        return ilpy.Variable(name, index=self._index_map[key])

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
