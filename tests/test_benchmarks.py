import sys
from typing import Callable

import pytest

# only run this module if --codspeed or --benchmark is passed on the command line
if all(x not in {"--codspeed", "--benchmark", "tests/test_bench.py"} for x in sys.argv):
    pytest.skip("use --benchmark to run benchmark", allow_module_level=True)

import itertools
import random
from functools import lru_cache

import networkx
from motile import Solver, TrackGraph, constraints, costs

random.seed(0)


@lru_cache(maxsize=None)
def _fully_connected_graph(
    n_frames: int = 1000,
    nodes_per_frame: int = 100,
    rand_score: Callable = random.random,
) -> TrackGraph:
    """Create a fully connected graph with random edge weights and node scores."""
    # all node ids grouped by frame
    # e.g. [(0, 1, 2, 3, 4), (5, 6, 7, 8, 9), (10, 11, 12, 13, 14)]
    frames = [
        range(i * nodes_per_frame, (i + 1) * nodes_per_frame) for i in range(n_frames)
    ]
    nodes = [
        (i, {"id": i, "t": f, "score": rand_score()})
        for f, node_group in enumerate(frames)
        for i in node_group
    ]

    # fully connected graph, with random edge weights
    # all nodes from tn are connected to all nodes from tn+1, etc.
    a, b = itertools.tee(frames)
    next(b, None)
    edges = [
        (s, t, {"source": s, "target": t, "score": rand_score()})
        for time_pair in zip(a, b)
        for s, t in itertools.product(*time_pair)
    ]

    nx_graph = networkx.DiGraph()
    nx_graph.add_nodes_from(nodes)
    nx_graph.add_edges_from(edges)
    return TrackGraph(nx_graph)


@pytest.mark.parametrize("nodes_per_frame", [10, 40])
@pytest.mark.parametrize("n_frames", [10, 100])
def test_solve(benchmark: Callable, n_frames: int, nodes_per_frame: int) -> None:
    graph = _fully_connected_graph(n_frames, nodes_per_frame)
    solver = Solver(graph)
    solver.add_costs(
        costs.NodeSelection(weight=-1.0, attribute="score", constant=-100.0)
    )
    solver.add_costs(costs.EdgeSelection(weight=1.0, attribute="score"))
    solver.add_costs(costs.Appear(constant=200.0))
    solver.add_costs(costs.Split(constant=100.0))

    benchmark(solver.solve)


@pytest.mark.parametrize(
    "constraint",
    [
        constraints.MaxChildren(1),
        constraints.MaxParents(1),
        constraints.SelectEdgeNodes(),
    ],
    ids=lambda x: str(x.__class__.__name__),
)
@pytest.mark.parametrize("n_frames", [1 << i for i in range(1, 10, 2)])
@pytest.mark.parametrize("nodes_per_frame", [1 << i for i in range(1, 6, 2)])
def test_constraint_instantiate(
    benchmark: Callable,
    n_frames: int,
    nodes_per_frame: int,
    constraint: constraints.Constraint,
) -> None:
    graph = _fully_connected_graph(n_frames, nodes_per_frame)
    solver = Solver(graph)
    benchmark(constraint.instantiate, solver)
