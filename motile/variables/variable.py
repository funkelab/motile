from abc import ABC, abstractmethod


class Variable(ABC):
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

    @staticmethod
    @abstractmethod
    def instantiate(solver):
        """Create and return keys for the variables.

        For example, to create a variable for each node, this function would
        return a list of all nodes::

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
    def instantiate_constraints(solver):
        """Add linear constraints to the solver to ensure that these variables
        are coupled to other variables of the solver.

        Args:

            solver (:class:`Solver`):
                The solver instance to create variable constraints for.

        Returns:

            A list of :class:`pylp.LinearConstraint`. See
            :class:`motile.constraints.Constraint` for how to create linear
            constraints.
        """
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
