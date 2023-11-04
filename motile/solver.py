from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeVar, cast

import numpy as np

from .constraints import SelectEdgeNodes
from .constraints.constraint import Constraint
from .costs import Features, Weight, Weights
from .expressions import Expression, Variable, VariableType
from .ssvm import fit_weights

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import ilpy

    from motile.costs import Costs
    from motile.track_graph import TrackGraph
    from motile.variables import Variables

    V = TypeVar("V", bound=Variables)


class Solver:
    """Create a solver for a given track graph.

    Args:
        track_graph:
            The :class:`~motile.TrackGraph` of objects to track over time.

        skip_core_constraints (:obj:`bool`, default=False):
            If true, add no constraints to the solver at all. Otherwise, core
            constraints that ensure consistencies between selected nodes and
            edges are added.
    """

    def __init__(
        self, track_graph: TrackGraph, skip_core_constraints: bool = False
    ) -> None:
        self.graph = track_graph
        self.variables: dict[type[Variables], Variables] = {}
        self.variable_types: dict[int, VariableType] = {}

        self.weights = Weights()
        self.weights.register_modify_callback(self._on_weights_modified)
        self._weights_changed = True
        self.features = Features()

        self._constraints: set[Expression] = set()

        self.num_variables: int = 0
        self._costs = np.zeros((0,), dtype=np.float32)
        self._costs_instances: dict[str, Costs] = {}
        self.solution: ilpy.Solution | None = None

        if not skip_core_constraints:
            self.add_constraints(SelectEdgeNodes())

    def add_costs(self, costs: Costs, name: str | None = None) -> None:
        """Add linear costs to the value of variables in this solver.

        Args:
            costs:
                The costs to add.  An instance of :class:`~motile.costs.Costs`.

            name:
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
                "to Solver.add_costs"
            )

        logger.info("Adding %s costs...", name)

        self._costs_instances[name] = costs

        # fish out all weights used in this cost object
        for var_name, var in costs.__dict__.items():
            if not isinstance(var, Weight):
                continue
            self.weights.add_weight(var, (name, var_name))

        costs.apply(self)

    def add_constraints(self, constraints: Constraint) -> None:
        """Add linear constraints to the solver.

        Args:
            constraints:
                The :class:`~motile.constraints.Constraint` to add.
        """
        logger.info("Adding %s constraints...", type(constraints).__name__)

        for constraint in constraints.instantiate(self):
            self._constraints.add(constraint)

    @property
    def ilpy_constraints(self) -> ilpy.Constraints:
        import ilpy

        constraints = ilpy.Constraints()
        for expr in self._constraints:
            constraints.add(expr.as_ilpy_constraint())
        return constraints

    def solve(self, timeout: float = 0.0, num_threads: int = 1) -> ilpy.Solution:
        """Solve the global optimization problem.

        Args:
            timeout:
                The timeout for the ILP solver, in seconds. Default (0.0) is no
                timeout. If the solver times out, the best solution encountered
                so far is returned (if any has been found at all).

            num_threads:
                The number of threads the ILP solver uses.

        Returns:
            :class:`ilpy.Solution`, a vector of variable values. Use
            :func:`get_variables` to find the indices of variables in this
            vector.
        """
        import ilpy

        self.objective = ilpy.Objective(self.num_variables)
        for i, c in enumerate(self.costs):
            logger.debug("Setting cost of var %d to %.3f", i, c)
            self.objective.set_coefficient(i, c)

        # TODO: support other variable types
        ilpy_var_types = {
            i: ilpy.VariableType(v) for i, v in self.variable_types.items()
        }
        self.ilp_solver = ilpy.Solver(
            self.num_variables,
            ilpy.VariableType.Binary,
            variable_types=ilpy_var_types,
            preference=ilpy.Preference.Any,
        )

        self.ilp_solver.set_objective(self.objective)
        self.ilp_solver.set_constraints(self.ilpy_constraints)

        self.ilp_solver.set_num_threads(num_threads)
        if timeout > 0:
            self.ilp_solver.set_timeout(timeout)

        self.ilp_solver.set_verbose(False)

        self.solution = self.ilp_solver.solve()
        if message := self.solution.get_status():
            logger.info("ILP solver returned with: %s", message)

        return self.solution

    def get_variables(self, cls: type[V]) -> V:
        """Get variables by their class name.

        If the solver does not yet contain those variables, they will be
        created.

        Args:
            cls (type of :class:`motile.variables.Variables`):
                A subclass of :class:`motile.variables.Variables`.

        Returns:
            A singleton instance of :class:`~motile.variables.Variables` (of whatever
            type was passed in as ``cls``), mimicking a dictionary that can be used to
            look up variable indices by their keys. See
            :class:`~motile.variables.Variables` for details.
        """
        if cls not in self.variables:
            self._add_variables(cls)
        return cast("V", self.variables[cls])

    def add_variable_cost(
        self, index: int | Variable, value: float, weight: Weight
    ) -> None:
        """Add costs for an individual variable.

        To be used within implementations of :class:`motile.costs.Costs`.
        """
        variable_index = index
        feature_index = self.weights.index_of(weight)
        self.features.add_feature(variable_index, feature_index, value)

    def fit_weights(
        self,
        gt_attribute: str,
        regularizer_weight: float = 0.1,
        max_iterations: int = 1000,
        eps: float = 1e-6,
    ) -> None:
        """Fit weights of ILP costs to ground truth with structured SVM.

        Updates the weights in the solver object to the found solution.

        See https://github.com/funkelab/structsvm for details.

        Args:
            gt_attribute:
                Node/edge attribute that marks the ground truth for fitting.
                `gt_attribute` is expected to be set to:

                - ``1`` for objects labaled as ground truth.
                - ``0`` for objects explicitly labeled as not part of the ground truth.
                - ``None`` or not set for unlabeled objects.

            regularizer_weight:
                The weight of the quadratic regularizer.

            max_iterations:
                Maximum number of gradient steps in the structured SVM.

            eps:
                Convergence threshold.
        """
        optimal_weights = fit_weights(
            self, gt_attribute, regularizer_weight, max_iterations, eps
        )
        self.weights.from_ndarray(optimal_weights)

    @property
    def costs(self) -> np.ndarray:
        """Returns the costs as a :class:`numpy.ndarray`."""
        if self._weights_changed:
            self._compute_costs()
            self._weights_changed = False

        return self._costs

    def _add_variables(self, cls: type[V]) -> None:
        logger.info("Adding %s variables...", cls.__name__)

        keys = cls.instantiate(self)
        indices = self._allocate_variables(len(keys))
        variables = cls(self, dict(zip(keys, indices)))
        self.variables[cls] = variables

        for index in indices:
            self.variable_types[index] = cls.variable_type

        for constraint in cls.instantiate_constraints(self):
            self._constraints.add(constraint)

        self.features.resize(num_variables=self.num_variables)

    def _compute_costs(self) -> None:
        logger.info("Computing costs...")

        weights = self.weights.to_ndarray()
        features = self.features.to_ndarray()
        self._costs = np.dot(features, weights)

    def _allocate_variables(self, num_variables: int) -> range:
        indices = range(self.num_variables, self.num_variables + num_variables)

        self.num_variables += num_variables
        self.features.resize(num_variables=self.num_variables)

        return indices

    def _on_weights_modified(self, old_value: float | None, new_value: float) -> None:
        if old_value != new_value:
            if not self._weights_changed:
                logger.info("Weights have changed")

            self._weights_changed = True
