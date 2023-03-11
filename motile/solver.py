import logging

import ilpy
import numpy as np

from .constraints import SelectEdgeNodes
from .costs import Features, Weight, Weights

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

        self.weights = Weights()
        self.weights.register_modify_callback(self._on_weights_modified)
        self._weights_changed = True
        self.features = Features()

        self.ilp_solver = None
        self.objective = None
        self.constraints = ilpy.LinearConstraints()

        self.num_variables = 0
        self.costs = np.zeros((0,), dtype=np.float32)
        self._costs_instances = {}
        self.solution = None

        if not skip_core_constraints:
            self.add_constraints(SelectEdgeNodes())

    # TODO: add getter/setter for costs, to compute when needed

    def add_costs(self, costs, name=None):
        """Add linear costs to the value of variables in this solver.

        Args:

            costs (:class:`motile.costs.Costs`):
                The costs to add.

            name (``string``):
                An optional name of the costs, used to refer to weights of
                costs in an unambiguous manner. Defaults to the name of the
                costs class, if not given.
        """

        # default name of costs is the class name
        if name is None:
            name = type(costs).__name__

        if name in self._costs_instances:
            raise RuntimeError(
                f"A cost instance with name '{name}' was already registered. "
                "Consider passing a different name with the 'name=' argument "
                "to Solver.add_costs")

        logger.info("Adding %s costs...", name)

        self._costs_instances[name] = costs

        # fish out all weights used in this cost object
        for var_name, var in costs.__dict__.items():
            if not isinstance(var, Weight):
                continue
            self.weights.add_weight(var, (name, var_name))

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

        if self._weights_changed:
            self._compute_costs()
            self._weights_changed = False

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

    def add_variable_cost(self, index, value, weight):
        """Add costs for an individual variable.

        To be used within implementations of :class:`motile.costs.Costs`.
        """

        variable_index = index
        feature_index = self.weights.index_of(weight)
        self.features.add_feature(variable_index, feature_index, value)

    def fit_weights(self, gt_attribute):
        from .ssvm import fit_weights

        optimal_weights = fit_weights(self, gt_attribute)
        self.weights.from_ndarray(optimal_weights)

    def _add_variables(self, cls):

        logger.info("Adding %s variables...", cls.__name__)

        keys = cls.instantiate(self)
        indices = self._allocate_variables(len(keys))
        variables = cls(self, {k: i for k, i in zip(keys, indices)})
        self.variables[cls] = variables

        for constraint in cls.instantiate_constraints(self):
            self.constraints.add(constraint)

    def _compute_costs(self):

        logger.info("Computing costs...")

        weights = self.weights.to_ndarray()
        features = self.features.to_ndarray()
        self.costs = np.dot(features, weights)

    # TODO: add variable_type
    def _allocate_variables(self, num_variables):

        indices = range(
            self.num_variables,
            self.num_variables + num_variables
        )

        self.num_variables += num_variables
        self.features.resize(num_variables=self.num_variables)

        return indices

    def _on_weights_modified(self, old_value, new_value):

        if old_value != new_value:

            if not self._weights_changed:
                logger.info("Weights have changed")

            self._weights_changed = True
