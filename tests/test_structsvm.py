import motile
import numpy as np
from data import create_ssvm_noise_graph, create_toy_example_graph
from motile.constraints import MaxChildren, MaxParents
from motile.costs import Appear, EdgeSelection, NodeSelection
from motile.variables import EdgeSelected, NodeSelected


def create_toy_solver(graph):
    solver = motile.Solver(graph)

    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))

    solver.add_costs(NodeSelection(weight=1.0, attribute="score", constant=-10.0))
    solver.add_costs(EdgeSelection(weight=10.0, attribute="score"))
    solver.add_costs(Appear(constant=10.0))

    print("====== Initial Weights ======")
    print(solver.weights)

    return solver


def test_structsvm_common_toy_example():
    graph = create_toy_example_graph()

    solver = create_toy_solver(graph)

    print("====== Initial Solution ======")
    solver.solve()
    print(solver.get_variables(EdgeSelected))

    # Structured Learning
    solver.fit_weights(
        gt_attribute="gt", regularizer_weight=0.03, max_iterations=50, eps=1e-6
    )

    print("====== Learnt Weights ======")
    print(solver.weights)
    print("====== Final Solution ======")
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

    print("====== Learnt Weights in new solver ======")
    print(solver.weights)
    solution = solver.solve()
    print(solver.get_variables(EdgeSelected))

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
            weight=np.random.randint(-10, 10, 1)[0],
            constant=np.random.randint(-10, 10, 1)[0],
            attribute="noise",
        ),
        name="NodeNoise",
    )
    solver.add_costs(
        EdgeSelection(
            weight=np.random.randint(-10, 10, 1)[0],
            constant=np.random.randint(-10, 10, 1)[0],
            attribute="noise",
        ),
        name="EdgeNoise",
    )

    print("====== Initial Weights ======")
    print(solver.weights)

    return solver


def test_structsvm_noise():
    np.set_printoptions(precision=2)
    graph = create_ssvm_noise_graph()
    solver = create_noise_solver(graph)

    print("====== Initial Solution ======")
    solver.solve()
    print(solver.get_variables(EdgeSelected))

    # Structured Learning
    solver.fit_weights(
        gt_attribute="gt", regularizer_weight=0.1, max_iterations=100, eps=1e-6
    )

    print("====== Learnt Weights ======")
    print(solver.weights)
    solution = solver.solve()

    print("====== Final Solution ======")
    optimal_weights = solver.weights
    print(solver.get_variables(NodeSelected))
    print(solver.get_variables(EdgeSelected))
    print(solver.features.to_ndarray())

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

    print("====== Learnt Weights in new solver ======")
    solution = solver.solve()
    print(solver.get_variables(NodeSelected))
    print(solver.get_variables(EdgeSelected))

    _assert_edges(solver, solution)


if __name__ == "__main__":
    test_structsvm_noise()
