from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, cast
from .constraints import SelectEdgeNodes
import logging
import numpy as np
import ilpy

from motile.constraints.constraint import Constraint

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from motile.variables import Variable
    from motile.costs import Costs
    from motile.track_graph import TrackGraph

    V = TypeVar('V', bound=Variable)


class Solver:
    """Create a solver for a given track graph.

    Args:

        track_graph (:class:`TrackGraph`):
            The graph of objects to track over time.

        skip_core_constraints (bool, default=False):
            If true, add no constraints to the solver at all. Otherwise, core
            constraints that ensure consistencies between selected nodes and
            edges are added.
    """

    def __init__(
        self, track_graph: TrackGraph, skip_core_constraints: bool = False
    ) -> None:

        self.graph = track_graph
        self.variables: dict[type[Variable], Variable] = {}

        self.ilp_solver: ilpy.LinearSolver | None = None
        self.objective: ilpy.LinearObjective | None = None
        self.constraints = ilpy.LinearConstraints()

        self.num_variables: int = 0
        self.costs = np.zeros((0,), dtype=np.float32)
        self.solution: ilpy.Solution | None = None

        if not skip_core_constraints:
            self.add_constraints(SelectEdgeNodes())

    def add_costs(self, costs: Costs) -> None:
        """Add linear costs to the value of variables in this solver.

        Args:

            costs (:class:`motile.costs.Costs`):
                The costs to add.
        """
        logger.info("Adding %s costs...", type(costs).__name__)
        costs.apply(self)

    def add_constraints(self, constraints: Constraint) -> None:
        """Add linear constraints to the solver.

        Args:

            constraints (:class:`motile.constraints.Constraint`)
                The constraints to add.
        """

        logger.info("Adding %s constraints...", type(constraints).__name__)

        for constraint in constraints.instantiate(self):
            self.constraints.add(constraint)

    def solve(
        self, timeout: float = 0.0, num_threads: int = 1
    ) -> ilpy.Solution:
        """Solve the global optimization problem.

        Args:

            timeout (float):
                The timeout for the ILP solver, in seconds. Default (0.0) is no
                timeout. If the solver times out, the best solution encountered
                so far is returned (if any has been found at all).

            num_threads (int):
                The number of threads the ILP solver uses.

        Returns:

            :class:`ilpy.Solution`, a vector of variable values. Use
            :func:`get_variables` to find the indices of variables in this
            vector.
        """

        self.objective = ilpy.LinearObjective(self.num_variables)
        for i, c in enumerate(self.costs):
            logger.debug("Setting cost of var %d to %.3f", i, c)
            self.objective.set_coefficient(i, c)

        # TODO: support other variable types
        self.ilp_solver = ilpy.LinearSolver(
            self.num_variables,
            ilpy.VariableType.Binary,
            preference=ilpy.Preference.Any)

        self.ilp_solver.set_objective(self.objective)
        self.ilp_solver.set_constraints(self.constraints)

        self.ilp_solver.set_num_threads(num_threads)
        if timeout > 0:
            self.ilp_solver.set_timeout(timeout)

        self.solution, message = self.ilp_solver.solve()
        if len(message):
            logger.info("ILP solver returned with: %s", message)

        return self.solution

    def get_variables(self, cls: type[V]) -> V:
        """Get variables by their class name.

        If the solver does not yet contain those variables, they will be
        created.

        Args:

            cls (type of :class:`motile.variables.Variable`):
                A subclass of :class:`motile.variables.Variable`.

        Returns:

            A singleton instance of :class:`motile.variables.Variable`,
            mimicking a dictionary that can be used to look up variable indices
            by their keys. See :class:`motile.variables.Variable` for details.
        """

        if cls not in self.variables:
            self._add_variables(cls)
        return cast('V', self.variables[cls])

    def add_variable_cost(self, index: int, cost: float) -> None:
        """Add costs for an individual variable.

        To be used within implementations of :class:`motile.costs.Costs`.
        """
        self.costs[index] += cost

    def _add_variables(self, cls: type[V]) -> None:

        logger.info("Adding %s variables...", cls.__name__)

        keys = cls.instantiate(self)
        indices = self._allocate_variables(len(keys))
        variables = cls(self, dict(zip(keys, indices)))
        self.variables[cls] = variables

        for constraint in cls.instantiate_constraints(self):
            self.constraints.add(constraint)

    # TODO: add variable_type
    def _allocate_variables(self, num_variables: int) -> range:

        indices = range(
            self.num_variables,
            self.num_variables + num_variables
        )

        self.num_variables += num_variables
        self.costs.resize(self.num_variables, refcheck=False)

        return indices
