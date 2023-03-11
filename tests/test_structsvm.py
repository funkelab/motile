import motile
import numpy as np
import pytest
from data import create_toy_example_graph
from motile.constraints import MaxChildren, MaxParents
from motile.costs import Appear, EdgeSelection, NodeSelection
from motile.variables import EdgeSelected

try:
    import structsvm  # noqa
except ImportError:
    import pytest

    pytest.skip(
        "Cannot test structsvm stuff without structsvm", allow_module_level=True
    )

def create_solver(graph):
    solver = motile.Solver(graph)

    solver.add_constraints(MaxParents(1))
    solver.add_constraints(MaxChildren(1))

    solver.add_costs(
        NodeSelection(
            weight=1.0,
            attribute='score',
            constant=-10.0))
    solver.add_costs(
        EdgeSelection(
            weight=10.0,
            attribute='score'))
    solver.add_costs(Appear(constant=10.0))
    print("====== Initial Weights ======")
    print(solver.weights)

    return solver

def test_structsvm():

    graph = create_toy_example_graph()

    solver = create_solver(graph)

    print("====== Initial Solution ======")
    solver.solve()
    print(solver.get_variables(EdgeSelected))

    # Structured Learning
    solver.fit_weights(gt_attribute='gt')

    print("====== Learnt Weights ======")
    print(solver.weights)
    print("====== Final Solution ======")
    optimal_weights = solver.weights

    assert np.isclose(
        optimal_weights[('NodeSelection', 'weight')], -2.7947596134511126)
    assert np.isclose(
        optimal_weights[('NodeSelection', 'constant')], -2.3828240341399347)
    assert np.isclose(
        optimal_weights[('EdgeSelection', 'weight')], -0.6477437066081595)
    assert np.isclose(
        optimal_weights[('EdgeSelection', 'constant')], -2.970887530069457)
    assert np.isclose(
        optimal_weights[('Appear', 'constant')], 14.88209571283641)

    solver = create_solver(graph)
    solver.weights.from_ndarray(optimal_weights.to_ndarray())

    print("====== Learnt Weights in new solver ======")
    print(solver.weights)
    solution = solver.solve()
    print(solver.get_variables(EdgeSelected))

    edge_indicators = solver.get_variables(EdgeSelected)
    selected_edges = [
        edge
        for edge, index in edge_indicators.items()
        if solution[index] > 0.5
    ]
    for u, v, gt in graph.edges(data='gt'):
        if gt == 1:
            assert (u, v) in selected_edges
        elif gt == 0:
            assert (u, v) not in selected_edges
        elif gt is None:
            pass
        else:
            raise ValueError(
                f"Ground truth {gt} for edge ({u},{v}) not valid.")

from ilpy import QuadraticSolver
try:
    QuadraticSolver(2, 0)
except RuntimeError:
    test_structsvm = pytest.mark.xfail(test_structsvm)


if __name__ == '__main__':
    test_structsvm()
