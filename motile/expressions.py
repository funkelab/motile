from __future__ import annotations

import ast
from typing import Any, Sequence

from ilpy import LinearConstraint, Relation


class Expr(ast.AST):
    def constraint(self) -> LinearConstraint:
        """Return a linear constraint from this expression."""
        return to_constraint(self)

    # comparisons
    @staticmethod
    def _cast(obj: Any) -> Expr:
        """Cast object into an Expression."""
        return obj if isinstance(obj, Expr) else Constant(obj)

    def __lt__(self, other: Expr | float) -> Compare:
        return Compare(self, [ast.Lt()], [other])

    def __le__(self, other: Expr | float) -> Compare:
        return Compare(self, [ast.LtE()], [other])

    def __eq__(self, other: Expr | float) -> Compare:  # type: ignore
        return Compare(self, [ast.Eq()], [other])

    def __ne__(self, other: Expr | float) -> Compare:  # type: ignore
        return Compare(self, [ast.NotEq()], [other])

    def __gt__(self, other: Expr | float) -> Compare:
        return Compare(self, [ast.Gt()], [other])

    def __ge__(self, other: Expr | float) -> Compare:
        return Compare(self, [ast.GtE()], [other])

    # binary operators
    # (note that __and__ and __or__ are reserved for boolean operators.)

    def __add__(self, other: Expr) -> BinOp:
        return BinOp(self, ast.Add(), other)

    def __radd__(self, other: Expr) -> BinOp:
        return BinOp(self, ast.Add(), other)

    def __sub__(self, other: Expr) -> BinOp:
        return BinOp(self, ast.Sub(), other)

    def __rmul__(self, other: float) -> BinOp:
        return BinOp(other, ast.Mult(), self)

    def __mul__(self, other: float) -> BinOp:
        return BinOp(self, ast.Mult(), other)

    def __truediv__(self, other: float) -> BinOp:
        return BinOp(self, ast.Div(), other)

    # unary operators

    def __neg__(self) -> UnaryOp:
        return UnaryOp(ast.USub(), self)

    def __pos__(self) -> UnaryOp:
        # usually a no-op
        return UnaryOp(ast.UAdd(), self)


class Compare(Expr, ast.Compare):
    """A comparison of two or more values.

    `left` is the first value in the comparison, `ops` the list of operators,
    and `comparators` the list of values after the first element in the
    comparison.
    """

    def __init__(
        self,
        left: Expr,
        ops: Sequence[ast.cmpop],
        comparators: Sequence[Expr | float],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            Expr._cast(left),
            ops,
            [Expr._cast(c) for c in comparators],
            **kwargs,
        )


class BinOp(Expr, ast.BinOp):
    """A binary operation (like addition or division).

    `op` is the operator, and `left` and `right` are any expression nodes.
    """

    def __init__(
        self,
        left: T | Expr,
        op: ast.operator,
        right: T | Expr,
        **k: Any,
    ) -> None:
        super().__init__(Expr._cast(left), op, Expr._cast(right), **k)


class UnaryOp(Expr, ast.UnaryOp):
    """A unary operation.

    `op` is the operator, and `operand` any expression node.
    """

    def __init__(self, op: ast.unaryop, operand: Expr, **kwargs: Any) -> None:
        super().__init__(op, Expr._cast(operand), **kwargs)


class Constant(Expr, ast.Constant):
    """A constant value.

    The `value` attribute contains the Python object it represents.
    types supported: NoneType, str, bytes, bool, int, float
    """

    def __init__(self, value: float, kind: str | None = None, **kwargs: Any) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError("Constants must be numbers")
        super().__init__(value, kind, **kwargs)


class Index(Expr, ast.Name):
    """A solution index.

    `id` holds the index as a string (becuase ast.Name requires a string).
    """

    def __init__(self, index: int) -> None:
        self.index = index
        super().__init__(str(index), ctx=ast.Load())


op_map: dict[type[ast.cmpop], Relation] = {
    ast.LtE: Relation.LessEqual,
    ast.Eq: Relation.Equal,
    ast.Gt: Relation.GreaterEqual,
}


def to_constraint(expr: Expr) -> LinearConstraint:
    constraint = LinearConstraint()

    seen_compare = False
    for sub in ast.walk(expr):
        if not isinstance(sub, Compare):
            continue
        if seen_compare:
            raise ValueError("Only single comparisons are supported")

        op_type = type(sub.ops[0])
        try:
            constraint.set_relation(op_map[op_type])
        except KeyError as e:
            raise ValueError(f"Unsupported comparison operator: {op_type}") from e

        seen_compare = True

    for index, coeff in get_coefficients(expr).items():
        if index is None:
            constraint.set_value(-coeff)
        else:
            constraint.set_coefficient(index, coeff)
    return constraint


def get_coefficients(
    expr: ast.expr, coeffs: dict[int | None, float] | None = None, scale: int = 1
) -> dict[int | None, float]:
    if coeffs is None:
        coeffs = {}

    if isinstance(expr, Compare):
        if len(expr.ops) != 1:
            raise ValueError("Only single comparisons are supported")
        get_coefficients(expr.left, coeffs)
        get_coefficients(expr.comparators[0], coeffs, -1)

    elif isinstance(expr, BinOp):
        if isinstance(expr.op, (ast.Mult, ast.Div)):
            if isinstance(expr.right, Constant):
                e = expr.left
                v = expr.right.value
            elif isinstance(expr.left, Constant):
                e = expr.right
                v = expr.left.value
            else:
                raise ValueError("Multiplication must be by a constant")
            assert isinstance(e, Index)
            scale *= 1 / v if isinstance(expr.op, ast.Div) else v
            get_coefficients(e, coeffs, scale)

        else:
            get_coefficients(expr.left, coeffs, scale)
            if isinstance(expr.op, (ast.USub, ast.Sub)):
                scale = -scale
            get_coefficients(expr.right, coeffs, scale)
    elif isinstance(expr, UnaryOp):
        if isinstance(expr.op, ast.USub):
            scale = -scale
        get_coefficients(expr.operand, coeffs, scale)
    elif isinstance(expr, Constant):
        coeffs[None] = expr.value * scale
    elif isinstance(expr, Index):
        coeffs.setdefault(expr.index, 0)
        coeffs[expr.index] += scale
    else:
        raise ValueError("Unsupported expression")

    return coeffs


# -u + 2*e - (v + 4 - u)
