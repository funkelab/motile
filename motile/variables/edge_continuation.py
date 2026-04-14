from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .edge_selected import EdgeSelected
from .node_merge import NodeMerge
from .node_split import NodeSplit
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Edge
    from motile.solver import Solver


class EdgeContinuation(Variable["Edge"]):
    r"""Binary variable indicating whether an edge is a continuation.

    A continuation edge is one that is selected and whose source node is not
    a split node and whose target node is not a merge node. In other words,
    it represents a simple one-to-one linking between frames.

    This variable is coupled to the edge selection, node split, and node merge
    variables through the following linear constraints:

    .. math::

        c_e &\leq x_e

        c_e &\leq 1 - s_{\text{src}(e)}

        c_e &\leq 1 - m_{\text{tgt}(e)}

        c_e &\geq x_e - s_{\text{src}(e)} - m_{\text{tgt}(e)}

    where :math:`x_e` is the edge selection indicator, :math:`s_v` is the
    node split indicator, :math:`m_v` is the node merge indicator, and
    :math:`c_e` is the edge continuation indicator.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Edge]:
        return solver.graph.edges

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        cont_indicators = solver.get_variables(EdgeContinuation)
        edge_indicators = solver.get_variables(EdgeSelected)
        split_indicators = solver.get_variables(NodeSplit)
        merge_indicators = solver.get_variables(NodeMerge)

        for edge in solver.graph.edges:
            src, tgt = edge
            c = cont_indicators[edge]
            x = edge_indicators[edge]
            s = split_indicators[src]
            m = merge_indicators[tgt]

            # c = x AND (NOT s) AND (NOT m)
            yield c <= x
            yield c <= 1 - s
            yield c <= 1 - m
            yield c >= x - s - m
