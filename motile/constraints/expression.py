from __future__ import annotations

import ast
import contextlib
from typing import TYPE_CHECKING, Union

import ilpy

from ..variables import EdgeSelected, NodeSelected, Variable
from .constraint import Constraint

if TYPE_CHECKING:
    from motile._types import Attributes, GenericEdge, Node
    from motile.solver import Solver

    NodesOrEdges = Union[dict[Node, Attributes], dict[GenericEdge, Attributes]]


class ExpressionConstraint(Constraint):
    """Enforce selection of nodes/edges based on an expression.

    The expression string is evaluated with the node/edge dict as a namespace.

    This is a powerful general constraint that allows you to select nodes/edges based on
    any combination of node/edge attributes. The `expression` string is evaluated for
    each node/edge (assuming eval_nodes/eval_edges is True) using the actual node object
    as a namespace to populate any variables names used in the provided expression. If
    the expression evaluates to True, the node/edge is selected; otherwise, it is
    excluded.

    This takes advantaged of python's `eval` function, like this:

    .. code-block:: python

        my_expression = "some_attribute == True"
        eval(my_expression, None, {"some_attribute": True})  # returns True (select)
        eval(my_expression, None, {"some_attribute": False})  # returns False (exclude)
        eval(my_expression, None, {})  # raises NameError (do nothing)

    Args:
        expression:
            An expression to evaluate for each node/edge. The expression must
            evaluate to a boolean value. The expression can use any names of
            node/edge attributes as variables.
        eval_nodes:
            Whether to evaluate the expression for nodes. By default, True.
        eval_edges:
            Whether to evaluate the expression for edges. By default, True.

    Example:
        If the nodes of a graph are:

        >>> cells = [
        ...     {"id": 0, "t": 0, "color": "red", "score": 1.0},
        ...     {"id": 1, "t": 0, "color": "green", "score": 1.0},
        ...     {"id": 2, "t": 1, "color": "blue", "score": 1.0},
        ... ]

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

        self._expression = compile(expression, "<string>", "eval")
        self.eval_nodes = eval_nodes
        self.eval_edges = eval_edges

    def instantiate(self, solver: Solver) -> list[ilpy.Constraint]:
        # create two constraints: one to select nodes/edges, and one to exclude
        select = ilpy.Constraint()
        exclude = ilpy.Constraint()
        n_selected = 0  # number of nodes/edges selected

        to_evaluate: list[tuple[NodesOrEdges, type[Variable]]] = []
        if self.eval_nodes:
            to_evaluate.append((solver.graph.nodes, NodeSelected))
        if self.eval_edges:
            to_evaluate.append((solver.graph.edges, EdgeSelected))

        for nodes_or_edges, VariableType in to_evaluate:
            indicator_variables = solver.get_variables(VariableType)
            for id_, node_or_edge in nodes_or_edges.items():
                with contextlib.suppress(NameError):
                    # Here is where the expression string is evaluated.
                    # We use the node/edge dict as a namespace to look up variables.
                    # if the expression uses a variable name that is not in the dict,
                    # a NameError will be raised.
                    # contextlib.suppress (above) will just skip it and move on...
                    if eval(self._expression, None, node_or_edge):
                        # if the expression evaluates to True, we select the node/edge
                        select.set_coefficient(indicator_variables[id_], 1)
                        n_selected += 1
                    else:
                        # Otherwise, we exclude it.
                        exclude.set_coefficient(indicator_variables[id_], 1)

        # finally, apply the relation and value to the constraints
        select.set_relation(ilpy.Relation.Equal)
        select.set_value(n_selected)

        exclude.set_relation(ilpy.Relation.Equal)
        exclude.set_value(0)

        return [select, exclude]
