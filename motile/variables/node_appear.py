from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .edge_selected import EdgeSelected
from .node_selected import NodeSelected
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Node
    from motile.solver import Solver


class NodeAppear(Variable["Node"]):
    r"""Binary variable indicating whether a node is the start of a track.

    (i.e., the node is selected and has no selected incoming edges).

    This variable is coupled to the node and edge selection variables through
    the following linear constraints:

    .. math::

        |\text{in_edges}(v)|\cdot x_v - &\sum_{e \in \text{in_edges}(v)} x_e
        - a_v &\leq&\;\; |\text{in_edges}(v)| - 1

        |\text{in_edges}(v)|\cdot x_v - &\sum_{e \in \text{in_edges}(v)} x_e
        - a_v\cdot |\text{in_edges}(v)| &\geq&\;\; 0

    where :math:`x_v` and :math:`x_e` are selection indicators for node
    :math:`v` and edge :math:`e`, and :math:`a_v` is the appear indicator for
    node :math:`v`.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Node]:
        return solver.graph.nodes

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        appear_indicators = solver.get_variables(NodeAppear)
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        for node in solver.graph.nodes:
            prev_edges = solver.graph.prev_edges[node]
            selected = node_indicators[node]
            appear = appear_indicators[node]

            if not prev_edges:
                # special case: no incoming edges, appear indicator is equal to
                # selection indicator
                yield selected == appear
                continue

            # Ensure that the following holds:
            #
            # appear = 1 <=> sum(prev_selected) = 0 and selected
            # appear = 0 <=> sum(prev_selected) > 0 or not selected
            #
            # Two linear constraints are needed for that:
            #
            # let s = num_prev * selected - sum(prev_selected)
            # (1) s - appear <= num_prev - 1
            # (2) s - appear * num_prev >= 0

            num_prev = len(prev_edges)
            s = num_prev * selected - sum(edge_indicators[e] for e in prev_edges)

            yield s - appear <= num_prev - 1
            yield s - appear >= 0
