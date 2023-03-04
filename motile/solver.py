import logging

import ilpy
import numpy as np

from .constraints import SelectEdgeNodes

logger = logging.getLogger(__name__)


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

    def __init__(self, track_graph, skip_core_constraints=False):

        self.graph = track_graph
        self.variables = {}

        self.ilp_solver = None
        self.objective = None
        self.constraints = ilpy.LinearConstraints()

        self.num_variables = 0
        self.costs = np.zeros((0,), dtype=np.float32)
        self.solution = None

        if not skip_core_constraints:
            self.add_constraints(SelectEdgeNodes())

    def add_costs(self, costs):
        """Add linear costs to the value of variables in this solver.

        Args:

            costs (:class:`motile.costs.Costs`):
                The costs to add.
        """

        logger.info("Adding %s costs...", type(costs).__name__)
        costs.apply(self)

    def add_constraints(self, constraints):
        """Add linear constraints to the solver.

        Args:

            constraints (:class:`motile.constraints.Constraint`)
                The constraints to add.
        """

        logger.info("Adding %s constraints...", type(constraints).__name__)

        for constraint in constraints.instantiate(self):
            self.constraints.add(constraint)

    def solve(self, timeout=0.0, num_threads=1):
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
            self.ilp_solver.set_timeout(self.timeout)

        self.solution, message = self.ilp_solver.solve()
        if len(message):
            logger.info("ILP solver returned with: %s", message)

        return self.solution

    def get_variables(self, cls):
        """Get variables by their class name.

        If the solver does not yet contain those variables, they will be
        created.

        Args:

            cls (class name):
                The name of a class inheriting from
                :class:`motile.variables.Variable`.

        Returns:

            A singleton instance of :class:`motile.variables.Variable`,
            mimicking a dictionary that can be used to look up variable indices
            by their keys. See :class:`motile.variables.Variable` for details.
        """

        if cls not in self.variables:
            self._add_variables(cls)

        return self.variables[cls]

    def add_variable_cost(self, index, cost):
        """Add costs for an individual variable.

        To be used within implementations of :class:`motile.costs.Costs`.
        """

        self.costs[index] += cost

    def _add_variables(self, cls):

        logger.info("Adding %s variables...", cls.__name__)

        keys = cls.instantiate(self)
        indices = self._allocate_variables(len(keys))
        variables = cls(self, {k: i for k, i in zip(keys, indices)})
        self.variables[cls] = variables

        for constraint in cls.instantiate_constraints(self):
            self.constraints.add(constraint)

    # TODO: add variable_type
    def _allocate_variables(self, num_variables):

        indices = range(
            self.num_variables,
            self.num_variables + num_variables
        )

        self.num_variables += num_variables
        self.costs.resize(self.num_variables, refcheck=False)

        return indices
