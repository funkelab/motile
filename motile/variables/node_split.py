from __future__ import annotations
from typing import TYPE_CHECKING

import ilpy

from .edge_selected import EdgeSelected
from .variable import Variable

if TYPE_CHECKING:
    from motile.solver import Solver


class NodeSplit(Variable):
    r"""A binary variable for each node that indicates whether the node has
    more than one children (i.e., the node is selected and has more than one
    selected outgoing edge).

    This variable is coupled to the edge selection variables through the
    following linear constraints:

    .. math::

        2 s_v\; - &\sum_{e\in\\text{out_edges}(v)} x_e &\leq&\;\; 0

        (|\\text{out_edges}(v)| - 1) s_v\; - &\sum_{e\in\\text{out_edges}(v)}
        x_e &\geq&\;\; -1

    where :math:`x_e` are selection indicators for edge :math:`e`, and
    :math:`s_v` is the split indicator for node :math:`v`.
    """

    @staticmethod
    def instantiate(solver):
        return solver.graph.nodes

    @staticmethod
    def instantiate_constraints(solver: Solver) -> list[ilpy.LinearConstraint]:

        split_indicators = solver.get_variables(NodeSplit)
        edge_indicators = solver.get_variables(EdgeSelected)

        constraints = []
        for node in solver.graph.nodes:

            next_edges = solver.graph.next_edges(node)

            # Ensure that the following holds:
            #
            # split = 0 <=> sum(next_selected) <= 1
            # split = 1 <=> sum(next_selected) > 1
            #
            # Two linear constraints are needed for that:
            #
            # (1) 2 * split - sum(next_selected) <= 0
            # (2) (num_next - 1) * split - sum(next_selected) >= -1

            constraint1 = ilpy.LinearConstraint()
            constraint2 = ilpy.LinearConstraint()

            constraint1.set_coefficient(
                split_indicators[node],
                2.0)
            constraint2.set_coefficient(
                split_indicators[node],
                len(next_edges) - 1.0)

            for next_edge in next_edges:
                constraint1.set_coefficient(
                    edge_indicators[next_edge],
                    -1.0)
                constraint2.set_coefficient(
                    edge_indicators[next_edge],
                    -1.0)

            constraint1.set_relation(ilpy.Relation.LessEqual)
            constraint2.set_relation(ilpy.Relation.GreaterEqual)

            constraint1.set_value(0.0)
            constraint2.set_value(-1.0)

            constraints.append(constraint1)
            constraints.append(constraint2)

        return constraints
