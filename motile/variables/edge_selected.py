from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .node_selected import NodeSelected
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Edge
    from motile.solver import Solver


class EdgeSelected(Variable["Edge"]):
    """Binary variable indicates whether an edge is part of the solution or not.

    This is the base edge variable. All constraints operate on this variable.
    Costs on this variable affect all edges, while costs on the semantic
    edge variables (EdgeContinuation, EdgeSplit, EdgeMerge) affect only a subset.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Edge]:
        return solver.graph.edges

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        for edge in solver.graph.edges:
            u, v = edge
            x_e = edge_indicators[edge]
            yield 2 * x_e - node_indicators[u] - node_indicators[v] <= 0
