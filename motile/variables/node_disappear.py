from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .edge_selected import EdgeSelected
from .node_selected import NodeSelected
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Node
    from motile.solver import Solver


class NodeDisappear(Variable["Node"]):
    r"""Binary variable to indicate whether a node disappears.

    This variable indicates whether the node is the end of a track (i.e., the node is
    selected and has no selected outgoing edges).

    This variable is coupled to the node and edge selection variables through
    the following linear constraints:

    .. math::
        |\\text{out_edges}(v)|\cdot x_v - &\sum_{e \in \\text{out_edges}(v)} x_e
        - d_v &\leq&\;\; |\\text{out_edges}(v)| - 1

        |\\text{out_edges}(v)|\cdot x_v - &\sum_{e \in \\text{out_edges}(v)} x_e
        - d_v\cdot |\\text{out_edges}(v)| &\geq&\;\; 0

    where :math:`x_v` and :math:`x_e` are selection indicators for node
    :math:`v` and edge :math:`e`, and :math:`d_v` is the disappear indicator for
    node :math:`v`.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Node]:
        return solver.graph.nodes

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)
        disappear_indicators = solver.get_variables(NodeDisappear)

        for node in solver.graph.nodes:
            next_edges = solver.graph.next_edges[node]
            selected = node_indicators[node]
            disappear = disappear_indicators[node]

            if not next_edges:
                # special case: no outgoing edges, disappear indicator is equal to
                # selection indicator
                yield selected == disappear
                continue

            # Ensure that the following holds:
            #
            # disappear = 1 <=> sum(next_selected) = 0 and selected
            # disappear = 0 <=> sum(next_selected) > 0 or not selected
            #
            # Two linear constraints are needed for that:
            #
            # let s = num_next * selected - sum(next_selected)
            # (1) s - disappear <= num_next - 1
            # (2) s - disappear * num_next >= 0

            num_next = len(next_edges)
            s = num_next * selected - sum(edge_indicators[e] for e in next_edges)

            yield s - disappear <= num_next - 1
            yield s - disappear >= 0
