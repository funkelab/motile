from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .node_selected import NodeSelected
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import GenericEdge
    from motile.solver import Solver


class EdgeSelected(Variable["GenericEdge"]):
    """Binary variable indicates whether an edge is part of the solution or not."""

    @staticmethod
    def instantiate(solver: Solver) -> Collection[GenericEdge]:
        return solver.graph.edges

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        for edge in solver.graph.edges:
            nodes = list(solver.graph.nodes_of(edge))
            x_e = edge_indicators[edge]
            yield len(nodes) * x_e - sum(node_indicators[n] for n in nodes) <= 0
