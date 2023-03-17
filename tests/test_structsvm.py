import logging

import motile
import numpy as np
import pytest
from data import create_ssvm_noise_trackgraph, create_toy_example_trackgraph
from ilpy import QuadraticSolver
from motile.constraints import MaxChildren, MaxParents
from motile.costs import Appear, EdgeSelection, NodeSelection
from motile.variables import EdgeSelected, NodeSelected

logger = logging.getLogger(__name__)


def create_toy_solver(graph):
    solver = motile.Solver(graph)

    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))

    solver.add_costs(NodeSelection(weight=1.0, attribute="score", constant=-10.0))
    solver.add_costs(EdgeSelection(weight=10.0, attribute="score"))
    solver.add_costs(Appear(constant=10.0))

    logger.debug("====== Initial Weights ======")
    logger.debug(solver.weights)

    return solver


def test_structsvm_common_toy_example():
    graph = create_toy_example_trackgraph()

    solver = create_toy_solver(graph)

    logger.debug("====== Initial Solution ======")
    solver.solve()
    logger.debug(solver.get_variables(EdgeSelected))

    # Structured Learning
    solver.fit_weights(
        gt_attribute="gt", regularizer_weight=0.03, max_iterations=50, eps=1e-6
    )

    logger.debug("====== Learnt Weights ======")
    logger.debug(solver.weights)
    logger.debug("====== Final Solution ======")
    optimal_weights = solver.weights

    np.testing.assert_allclose(
        optimal_weights[("NodeSelection", "weight")], -4.9771062468440785, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("NodeSelection", "constant")], -3.60083857250377, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("EdgeSelection", "weight")], -6.209937259450144, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("EdgeSelection", "constant")], -2.4005590483600203, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("Appear", "constant")], 32.13305455424766, rtol=0.01
    )

    solver = create_toy_solver(graph)
    solver.weights.from_ndarray(optimal_weights.to_ndarray())

    logger.debug("====== Learnt Weights in new solver ======")
    logger.debug(solver.weights)
    solution = solver.solve()
    logger.debug(solver.get_variables(EdgeSelected))

    edge_indicators = solver.get_variables(EdgeSelected)
    selected_edges = [
        edge for edge, index in edge_indicators.items() if solution[index] > 0.5
    ]
    for u, v, gt in graph.edges(data="gt"):
        if gt == 1:
            assert (u, v) in selected_edges
        elif gt == 0:
            assert (u, v) not in selected_edges
        elif gt is None:
            pass
        else:
            raise ValueError(f"Ground truth {gt} for edge ({u},{v}) not valid.")


def create_noise_solver(graph):
    solver = motile.Solver(graph)

    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))

    solver.add_costs(NodeSelection(weight=1.0, attribute="score", constant=-10.0))
    solver.add_costs(EdgeSelection(weight=10.0, attribute="score", constant=3.0))
    solver.add_costs(Appear(constant=10.0))

    solver.add_costs(
        NodeSelection(
            weight=2,
            constant=4,
            attribute="noise",
        ),
        name="NodeNoise",
    )
    solver.add_costs(
        EdgeSelection(
            weight=6,
            constant=8,
            attribute="noise",
        ),
        name="EdgeNoise",
    )

    logger.debug("====== Initial Weights ======")
    logger.debug(solver.weights)

    return solver


def test_structsvm_noise():
    graph = create_ssvm_noise_trackgraph()
    solver = create_noise_solver(graph)

    logger.debug("====== Initial Solution ======")
    solver.solve()
    logger.debug(solver.get_variables(EdgeSelected))

    # Structured Learning
    solver.fit_weights(
        gt_attribute="gt", regularizer_weight=0.1, max_iterations=100, eps=1e-6
    )

    logger.debug("====== Learnt Weights ======")
    logger.debug(solver.weights)
    solution = solver.solve()

    logger.debug("====== Final Solution ======")
    optimal_weights = solver.weights
    logger.debug(solver.get_variables(NodeSelected))
    logger.debug(solver.get_variables(EdgeSelected))
    logger.debug(solver.features.to_ndarray())

    np.testing.assert_allclose(
        optimal_weights[("NodeSelection", "weight")], -2.7777798708004564, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("NodeSelection", "constant")], -1.3883786845544988, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("EdgeSelection", "weight")], -3.3333338262308043, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("EdgeSelection", "constant")], -0.9255857897041805, rtol=0.01
    )
    np.testing.assert_allclose(
        optimal_weights[("Appear", "constant")], 19.53720680712646, rtol=0.01
    )

    def _assert_edges(solver, solution):
        edge_indicators = solver.get_variables(EdgeSelected)
        selected_edges = [
            edge for edge, index in edge_indicators.items() if solution[index] > 0.5
        ]
        for u, v, gt in solver.graph.edges(data="gt"):
            if gt == 1:
                assert (u, v) in selected_edges
            elif gt == 0:
                assert (u, v) not in selected_edges
            elif gt is None:
                pass
            else:
                raise ValueError(f"Ground truth {gt} for edge ({u},{v}) not valid.")

    _assert_edges(solver, solution)

    solver = create_noise_solver(graph)
    solver.weights.from_ndarray(optimal_weights.to_ndarray())

    logger.debug("====== Learnt Weights in new solver ======")
    solution = solver.solve()
    logger.debug(solver.get_variables(NodeSelected))
    logger.debug(solver.get_variables(EdgeSelected))

    _assert_edges(solver, solution)


if __name__ == "__main__":
    test_structsvm_noise()
