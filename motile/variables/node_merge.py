from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

import ilpy

from .edge_selected import EdgeSelected
from .variable import Variable

if TYPE_CHECKING:
    from motile._types import Node
    from motile.solver import Solver


class NodeMerge(Variable):
    r"""Binary variable indicating whether a node has more than one parent.

    (i.e., the node is selected and has more than one selected incoming edge).

    This variable is coupled to the edge selection variables through the
    following linear constraints:

    .. math::

        2 m_v\; - &\sum_{e\in\text{in_edges}(v)} x_e &\leq&\;\; 0

        (|\text{in_edges}(v)| - 1) m_v\; - &\sum_{e\in\text{in_edges}(v)}
        x_e &\geq&\;\; -1

    where :math:`x_e` are selection indicators for edge :math:`e`, and
    :math:`m_v` is the merge indicator for node :math:`v`.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[Node]:
        return solver.graph.nodes

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Constraint]:
        merge_indicators = solver.get_variables(NodeMerge)
        edge_indicators = solver.get_variables(EdgeSelected)

        for node in solver.graph.nodes:
            prev_edges = solver.graph.prev_edges[node]

            # Ensure that the following holds:
            #
            # merge = 0 <=> sum(prev_selected) <= 1
            # merge = 1 <=> sum(prev_selected) > 1
            #
            # Two linear constraints are needed for that:
            #
            # (1) 2 * merge - sum(prev_selected) <= 0
            # (2) (num_prev - 1) * merge - sum(prev_selected) >= -1

            constraint1 = ilpy.Constraint()
            constraint2 = ilpy.Constraint()

            constraint1.set_coefficient(merge_indicators[node], 2.0)
            constraint2.set_coefficient(merge_indicators[node], len(prev_edges) - 1.0)

            for prev_edge in prev_edges:
                constraint1.set_coefficient(edge_indicators[prev_edge], -1.0)
                constraint2.set_coefficient(edge_indicators[prev_edge], -1.0)

            constraint1.set_relation(ilpy.Relation.LessEqual)
            constraint2.set_relation(ilpy.Relation.GreaterEqual)

            constraint1.set_value(0.0)
            constraint2.set_value(-1.0)

            yield constraint1
            yield constraint2
