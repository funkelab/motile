import motile
import pytest
from motile.costs import Appear, EdgeSelection, NodeSelection, Split
from motile.plot import draw_solution, draw_track_graph

try:
    import plotly.graph_objects as go
except ImportError:
    pytest.skip("plotly not installed", allow_module_level=True)


@pytest.fixture
def solver(arlo_graph: motile.TrackGraph) -> motile.Solver:
    solver = motile.Solver(arlo_graph)
    solver.add_cost(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
    solver.add_cost(EdgeSelection(weight=1.0, attribute="prediction_distance"))
    solver.add_cost(Appear(constant=200.0))
    solver.add_cost(Split(constant=100.0))
    return solver


def test_plot_graph(arlo_graph: motile.TrackGraph) -> None:
    graph = arlo_graph
    assert isinstance(draw_track_graph(graph), go.Figure)
    assert isinstance(draw_track_graph(graph, alpha_attribute="score"), go.Figure)
    assert isinstance(draw_track_graph(graph, alpha_func=lambda _: 0.5), go.Figure)
    assert isinstance(draw_track_graph(graph, label_attribute="id"), go.Figure)

    def label_func(node):
        return "hi"

    assert isinstance(draw_track_graph(graph, label_func=label_func), go.Figure)
    assert isinstance(
        draw_track_graph(graph, label_func=(label_func, label_func)), go.Figure
    )


def test_plot_solution(arlo_graph: motile.TrackGraph, solver: motile.Solver) -> None:
    graph = arlo_graph
    with pytest.raises(RuntimeError):
        draw_solution(graph, solver)
    solver.solve()
    assert isinstance(draw_solution(graph, solver), go.Figure)
