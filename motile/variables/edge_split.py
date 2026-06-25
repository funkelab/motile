from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .edge_selected import EdgeSelected
from .node_split import NodeSplit
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Edge
    from motile.solver import Solver


class EdgeSplit(Variable["Edge"]):
    r"""Binary variable indicating whether an edge is part of a split.

    An edge is a split edge if it is selected and its source node has more than
    one selected outgoing edge (i.e., the source node is a split node).

    This variable is coupled to the edge selection and node split variables
    through the following linear constraints:

    .. math::

        y_e &\leq x_e

        y_e &\leq s_{\text{src}(e)}

        y_e &\geq x_e + s_{\text{src}(e)} - 1

    where :math:`x_e` is the edge selection indicator, :math:`s_v` is the
    node split indicator, and :math:`y_e` is the edge split indicator.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Edge]:
        return solver.graph.edges

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        edge_split_indicators = solver.get_variables(EdgeSplit)
        edge_indicators = solver.get_variables(EdgeSelected)
        split_indicators = solver.get_variables(NodeSplit)

        for edge in solver.graph.edges:
            src, _ = edge
            y = edge_split_indicators[edge]
            x = edge_indicators[edge]
            s = split_indicators[src]

            # y = x AND s (product of two binaries)
            yield y <= x
            yield y <= s
            yield y >= x + s - 1
