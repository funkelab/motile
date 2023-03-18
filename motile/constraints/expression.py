from __future__ import annotations

import ast
import contextlib
from typing import TYPE_CHECKING

import ilpy

from ..variables import EdgeSelected, NodeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from motile.solver import Solver


class ExpressionConstraint(Constraint):
    """Enforces the selection of nodes/edges based on an expression evaluated
    with the node/edge dict as a namespace.

    Args:

        expression (string):
            An expression to evaluate for each node/edge. The expression must
            evaluate to a boolean value. The expression can use any names of
            node/edge attributes as variables.

    Example:

    If the nodes of a graph are:
        cells = [
            {"id": 0, "t": 0, "color": "red", "score": 1.0},
            {"id": 1, "t": 0, "color": "green", "score": 1.0},
            {"id": 2, "t": 1, "color": "blue", "score": 1.0},
        ]

    Then the following constraint will select node 0:
        >>> expr = "t == 0 and color != 'green'"
        >>> solver.add_constraints(ExpressionConstraint(expr))
    """

    def __init__(
        self, expression: str, eval_nodes: bool = True, eval_edges: bool = True
    ) -> None:
        try:
            tree = ast.parse(expression, mode="eval")
            if not isinstance(tree, ast.Expression):
                raise SyntaxError
        except SyntaxError:
            raise ValueError(f"Invalid expression: {expression}") from None

        self.expression = expression
        self.eval_nodes = eval_nodes
        self.eval_edges = eval_edges

    def instantiate(self, solver: Solver) -> list[ilpy.LinearConstraint]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        select = ilpy.LinearConstraint()
        exclude = ilpy.LinearConstraint()
        n_selected = 0

        for do_evaluate, graph_part, indicators in [
            (self.eval_nodes, solver.graph.nodes, node_indicators),
            (self.eval_edges, solver.graph.edges, edge_indicators),
        ]:
            if do_evaluate:
                for id_, namespace in graph_part.items():  # type: ignore
                    with contextlib.suppress(NameError):
                        if eval(self.expression, None, namespace):
                            select.set_coefficient(indicators[id_], 1)  # type: ignore
                            n_selected += 1
                        else:
                            exclude.set_coefficient(indicators[id_], 1)  # type: ignore

        select.set_relation(ilpy.Relation.Equal)
        select.set_value(n_selected)

        exclude.set_relation(ilpy.Relation.Equal)
        exclude.set_value(0)

        return [select, exclude]
