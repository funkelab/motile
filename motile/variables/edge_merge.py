from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .edge_selected import EdgeSelected
from .node_merge import NodeMerge
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Edge
    from motile.solver import Solver


class EdgeMerge(Variable["Edge"]):
    r"""Binary variable indicating whether an edge is part of a merge.

    An edge is a merge edge if it is selected and its target node has more than
    one selected incoming edge (i.e., the target node is a merge node).

    This variable is coupled to the edge selection and node merge variables
    through the following linear constraints:

    .. math::

        y_e &\leq x_e

        y_e &\leq m_{\text{tgt}(e)}

        y_e &\geq x_e + m_{\text{tgt}(e)} - 1

    where :math:`x_e` is the edge selection indicator, :math:`m_v` is the
    node merge indicator, and :math:`y_e` is the edge merge indicator.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Edge]:
        return solver.graph.edges

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        edge_merge_indicators = solver.get_variables(EdgeMerge)
        edge_indicators = solver.get_variables(EdgeSelected)
        merge_indicators = solver.get_variables(NodeMerge)

        for edge in solver.graph.edges:
            _, tgt = edge
            y = edge_merge_indicators[edge]
            x = edge_indicators[edge]
            m = merge_indicators[tgt]

            # y = x AND m (product of two binaries)
            yield y <= x
            yield y <= m
            yield y >= x + m - 1
