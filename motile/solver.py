from .constraints import SelectEdgeNodes
import logging
import numpy as np
import pylp

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
        self.constraints = pylp.LinearConstraints()

        self.num_variables = 0
        self.costs = np.zeros((0,), dtype=np.float32)

        if not skip_core_constraints:
            self.add_constraints(SelectEdgeNodes())

    def add_costs(self, costs):

        logger.info("Adding %s costs...", type(costs).__name__)
        costs.apply(self)

    def add_constraints(self, constraints):

        logger.info("Adding %s constraints...", type(constraints).__name__)

        for constraint in constraints.instantiate(self):
            self.constraints.add(constraint)

    def solve(self, timeout=0.0, num_threads=1):

        self.objective = pylp.LinearObjective(self.num_variables)
        for i, c in enumerate(self.costs):
            logger.debug("Setting cost of var %d to %.3f", i, c)
            self.objective.set_coefficient(i, c)

        # TODO: support other variable types
        self.ilp_solver = pylp.LinearSolver(
            self.num_variables,
            pylp.VariableType.Binary,
            preference=pylp.Preference.Any)

        self.ilp_solver.set_objective(self.objective)
        self.ilp_solver.set_constraints(self.constraints)

        self.ilp_solver.set_num_threads(num_threads)
        if timeout > 0:
            self.ilp_solver.set_timeout(self.timeout)

        solution, message = self.ilp_solver.solve()
        if len(message):
            logger.info("ILP solver returned with: %s", message)

        return solution

    def get_variables(self, cls):

        if cls not in self.variables:
            self._add_variables(cls)

        return self.variables[cls]

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

    def add_variable_cost(self, index, cost):

        self.costs[index] += cost
