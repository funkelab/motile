from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from motile.expressions import Constant, Expression

from .edge_selected import EdgeSelected
from .variable import Variables

if TYPE_CHECKING:
    from motile._types import NodeId
    from motile.solver import Solver


class NodeSplit(Variables):
    r"""Binary variable indicating whether a node has more than one child.

    (i.e., the node is selected and has more than one selected outgoing edge).

    This variable is coupled to the edge selection variables through the
    following linear constraints:

    .. math::

        2 s_v\; - &\sum_{e\in\text{out_edges}(v)} x_e &\leq&\;\; 0

        (|\text{out_edges}(v)| - 1) s_v\; - &\sum_{e\in\text{out_edges}(v)}
        x_e &\geq&\;\; -1

    where :math:`x_e` are selection indicators for edge :math:`e`, and
    :math:`s_v` is the split indicator for node :math:`v`.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[NodeId]:
        return solver.graph.nodes

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[Expression]:
        split_indicators = solver.get_variables(NodeSplit)
        edge_indicators = solver.get_variables(EdgeSelected)

        for node in solver.graph.nodes:
            # Ensure that the following holds:
            #
            # split = 0 <=> sum(next_selected) <= 1
            # split = 1 <=> sum(next_selected) > 1
            #
            # Two linear constraints are needed for that:
            #
            # (1) 2 * split - sum(next_selected) <= 0
            # (2) (num_next - 1) * split - sum(next_selected) >= -1

            c1: Expression = Constant(0)
            c2: Expression = Constant(0)

            next_edges = solver.graph.next_edges[node]
            c1 += 2.0 * split_indicators[node]
            c2 += (len(next_edges) - 1.0) * split_indicators[node]

            for next_edge in next_edges:
                c1 -= edge_indicators[next_edge]
                c2 -= edge_indicators[next_edge]

            yield c1 <= 0.0
            yield c2 >= -1.0
