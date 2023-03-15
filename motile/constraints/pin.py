from __future__ import annotations

from typing import TYPE_CHECKING

import ilpy

from ..variables import EdgeSelected, NodeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from motile.solver import Solver


class Pin(Constraint):
    """Enforces the selection of certain nodes and edges based on the value of
    a given attribute.

    Every node or edge that has the given attribute will be selected if the
    attribute value is ``True`` (and not selected if the attribute value is
    ``False``). The solver will only determine the selection of nodes and edges
    that do not have this attribute.

    This constraint is useful to complete partial tracking solutions, e.g.,
    when users have already manually selected (or unselected) certain nodes or
    edges.

    Args:

        attribute (string):
            The name of the node/edge attribute to use.
    """

    def __init__(self, attribute: str) -> None:
        self.attribute = attribute

    def instantiate(self, solver: Solver) -> list[ilpy.LinearConstraint]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        must_select = [
            node_indicators[node]
            for node, attributes in solver.graph.nodes.items()
            if self.attribute in attributes and attributes[self.attribute]
        ] + [
            edge_indicators[(u, v)]
            for (u, v), attributes in solver.graph.edges.items()
            if self.attribute in attributes and attributes[self.attribute]
        ]

        must_not_select = [
            node_indicators[node]
            for node, attributes in solver.graph.nodes.items()
            if self.attribute in attributes and not attributes[self.attribute]
        ] + [
            edge_indicators[(u, v)]
            for (u, v), attributes in solver.graph.edges.items()
            if self.attribute in attributes and not attributes[self.attribute]
        ]

        must_select_constraint = ilpy.LinearConstraint()
        must_not_select_constraint = ilpy.LinearConstraint()

        for index in must_select:
            must_select_constraint.set_coefficient(index, 1)
        for index in must_not_select:
            must_not_select_constraint.set_coefficient(index, 1)

        must_select_constraint.set_relation(ilpy.Relation.Equal)
        must_not_select_constraint.set_relation(ilpy.Relation.Equal)

        must_select_constraint.set_value(len(must_select))
        must_not_select_constraint.set_value(0)

        return [must_select_constraint, must_not_select_constraint]
