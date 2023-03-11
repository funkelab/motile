import numpy as np
import motile
import networkx

from motile.constraints import MaxParents, MaxChildren
from motile.costs import NodeSelection, EdgeSelection, Appear
from motile.variables import EdgeSelected

from data import create_toy_example_graph


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
        optimal_weights[('NodeSelection', 'weight')], -3.5972583293914795)
    assert np.isclose(
        optimal_weights[('NodeSelection', 'constant')], 0.9798323512077332)
    assert np.isclose(
        optimal_weights[('EdgeSelection', 'weight')], 3.176938772201538)
    assert np.isclose(
        optimal_weights[('EdgeSelection', 'constant')], -1.3103692531585693)
    assert np.isclose(
        optimal_weights[('Appear', 'constant')], 3.148256301879883)

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


if __name__ == '__main__':
    test_structsvm()
