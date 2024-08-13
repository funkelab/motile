import logging

import motile
import networkx
import numpy as np
from motile.constraints import MaxChildren, MaxParents
from motile.costs import Appear, EdgeSelection, NodeSelection
from motile.variables import EdgeSelected, NodeSelected

logger = logging.getLogger(__name__)


def create_ssvm_noise_trackgraph() -> motile.TrackGraph:
    cells = [
        {"id": 0, "t": 0, "x": 1, "score": 0.8, "gt": 1, "noise": 0.5},
        {"id": 1, "t": 0, "x": 25, "score": 0.9, "gt": 1, "noise": -0.5},
        {"id": 2, "t": 1, "x": 0, "score": 0.9, "gt": 1, "noise": 0.5},
        {"id": 3, "t": 1, "x": 26, "score": 0.8, "gt": 1, "noise": -0.5},
        {"id": 4, "t": 2, "x": 2, "score": 0.9, "gt": 1, "noise": 0.5},
        {"id": 5, "t": 2, "x": 24, "score": 0.1, "gt": 0, "noise": -0.5},
        {"id": 6, "t": 2, "x": 35, "score": 0.7, "gt": 1, "noise": -0.5},
    ]

    edges = [
        {"source": 0, "target": 2, "score": 0.9, "gt": 1, "noise": 0.5},
        {"source": 1, "target": 3, "score": 0.9, "gt": 1, "noise": -0.5},
        {"source": 0, "target": 3, "score": 0.2, "gt": 0, "noise": 0.5},
        {"source": 1, "target": 2, "score": 0.2, "gt": 0, "noise": -0.5},
        {"source": 2, "target": 4, "score": 0.9, "gt": 1, "noise": 0.5},
        {"source": 3, "target": 5, "score": 0.1, "gt": 0, "noise": -0.5},
        {"source": 2, "target": 5, "score": 0.2, "gt": 0, "noise": 0.5},
        {"source": 3, "target": 4, "score": 0.2, "gt": 0, "noise": -0.5},
        {"source": 3, "target": 6, "score": 0.8, "gt": 1, "noise": -0.5},
    ]
    graph = networkx.DiGraph()
    graph.add_nodes_from([(cell["id"], cell) for cell in cells])
    graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])

    return motile.TrackGraph(graph)


def create_toy_solver(graph):
    solver = motile.Solver(graph)

    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    solver.add_cost(NodeSelection(weight=1.0, attribute="score", constant=-10.0))
    solver.add_cost(EdgeSelection(weight=10.0, attribute="score"))
    solver.add_cost(Appear(constant=10.0))

    logger.debug("====== Initial Weights ======")
    logger.debug(solver.weights)

    return solver


def test_structsvm_common_toy_example(toy_graph):
    graph = toy_graph

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
    for (u, v), attrs in graph.edges.items():
        gt = attrs.get("gt", None)
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

    solver.add_constraint(MaxParents(1))
    solver.add_constraint(MaxChildren(1))

    solver.add_cost(NodeSelection(weight=1.0, attribute="score", constant=-10.0))
    solver.add_cost(EdgeSelection(weight=10.0, attribute="score", constant=3.0))
    solver.add_cost(Appear(constant=10.0))

    solver.add_cost(
        NodeSelection(
            weight=2,
            constant=4,
            attribute="noise",
        ),
        name="NodeNoise",
    )
    solver.add_cost(
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
        for (u, v), attrs in graph.edges.items():
            gt = attrs.get("gt", None)
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
