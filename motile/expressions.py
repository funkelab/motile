from __future__ import annotations

import ast
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, ClassVar, Sequence, Union

if TYPE_CHECKING:
    import ilpy

Number = Union[float, int]


class VariableType(IntEnum):
    """Type of a variable."""

    Continuous = 0
    Integer = auto()
    Binary = auto()


class Expression(ast.AST):
    """Base class for all expression nodes.

    Expressions allow ilpy to represent mathematical expressions in an
    intuitive syntax, and then convert to a native Constraint object.

    This class provides all of the operators and methods needed to build
    expressions. For example, to create the expression ``2 * x - y >= 0``, you can
    write ``2 * Variable('x') - Variable('y') >= 0``.

    Tip: you can use ``ast.dump`` to see the AST representation of an expression.
    Or, use ``print(expr)` to see the string representation of an expression.
    """

    def __hash__(self) -> int:
        # allow use as dict key
        return id(self)

    def as_ilpy_constraint(self) -> ilpy.Constraint:
        """Create an ilpy.Constraint object from this expression."""
        import ilpy

        l_coeffs, q_coeffs, value = _get_coeff_indices(self)
        return ilpy.Constraint.from_coefficients(
            coefficients=l_coeffs,
            quadratic_coefficients=q_coeffs,
            relation=_get_ilpy_relation(self) or ilpy.Relation.LessEqual,
            value=-value,  # negate value to convert to RHS form
        )

    def as_ilpy_objective(
        self, sense: ilpy.Sense | str | int = "Minimize"
    ) -> ilpy.Objective:
        """Create a linear objective from this expression."""
        import ilpy

        if _get_ilpy_relation(self) is not None:
            # TODO: may be supported in the future, eg. for piecewise objectives?
            raise ValueError(f"Objective function cannot have comparisons: {self}")

        l_coeffs, q_coeffs, value = _get_coeff_indices(self)
        sense = ilpy.Sense[sense] if isinstance(sense, str) else ilpy.Sense(sense)
        return ilpy.Objective.from_coefficients(
            coefficients=l_coeffs,
            quadratic_coefficients=q_coeffs,
            constant=value,
            sense=sense,
        )

    @staticmethod
    def _cast(obj: Any) -> Expression:
        """Cast object into an Expression."""
        return obj if isinstance(obj, Expression) else Constant(obj)

    def __str__(self) -> str:
        """Serialize this expression to string form."""
        return str(_ExprSerializer(self))

    # comparisons

    def __lt__(self, other: Expression | float) -> Compare:
        return Compare(self, [ast.Lt()], [other])

    def __le__(self, other: Expression | float) -> Compare:
        return Compare(self, [ast.LtE()], [other])

    def __eq__(self, other: Expression | float) -> Compare:  # type: ignore
        return Compare(self, [ast.Eq()], [other])

    def __ne__(self, other: Expression | float) -> Compare:  # type: ignore
        return Compare(self, [ast.NotEq()], [other])

    def __gt__(self, other: Expression | float) -> Compare:
        return Compare(self, [ast.Gt()], [other])

    def __ge__(self, other: Expression | float) -> Compare:
        return Compare(self, [ast.GtE()], [other])

    # binary operators
    # (note that __and__ and __or__ are reserved for boolean operators.)

    def __add__(self, other: Expression | Number) -> BinOp:
        return BinOp(self, ast.Add(), other)

    def __radd__(self, other: Expression | Number) -> BinOp:
        return BinOp(other, ast.Add(), self)

    def __sub__(self, other: Expression | Number) -> BinOp:
        return BinOp(self, ast.Sub(), other)

    def __rsub__(self, other: Expression | Number) -> BinOp:
        return BinOp(other, ast.Sub(), self)

    def __mul__(self, other: Any) -> BinOp | Constant:
        return BinOp(self, ast.Mult(), other)

    def __rmul__(self, other: Number) -> BinOp | Constant:
        if not isinstance(other, (int, float)):
            raise TypeError("Right multiplication must be with a number")
        return Constant(other) * self

    def __truediv__(self, other: Number) -> BinOp:
        return BinOp(self, ast.Div(), other)

    def __rtruediv__(self, other: Number) -> BinOp:
        return BinOp(other, ast.Div(), self)

    # unary operators

    def __neg__(self) -> UnaryOp:
        return UnaryOp(ast.USub(), self)

    def __pos__(self) -> UnaryOp:
        # usually a no-op
        return UnaryOp(ast.UAdd(), self)

    # specifically not implemented on Expression for now.
    # We don't want to reimplement a full CAS like sympy.
    # (But we could support sympy expressions!)
    # Implemented below only on Constant and Variable.

    # def __pow__(self, other: Number) -> BinOp:
    # return BinOp(self, ast.Pow(), other)


class Compare(Expression, ast.Compare):
    """A comparison of two or more values.

    `left` is the first value in the comparison, `ops` the list of operators,
    and `comparators` the list of values after the first element in the
    comparison.
    """

    def __init__(
        self,
        left: Expression,
        ops: Sequence[ast.cmpop],
        comparators: Sequence[Expression | Number],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            Expression._cast(left),
            ops,
            [Expression._cast(c) for c in comparators],
            **kwargs,
        )


class BinOp(Expression, ast.BinOp):
    """A binary operation (like addition or division).

    `op` is the operator, and `left` and `right` are any expression nodes.
    """

    def __init__(
        self,
        left: Expression | Number,
        op: ast.operator,
        right: Expression | Number,
        **kwargs: Any,
    ) -> None:
        super().__init__(Expression._cast(left), op, Expression._cast(right), **kwargs)


class UnaryOp(Expression, ast.UnaryOp):
    """A unary operation.

    `op` is the operator, and `operand` any expression node.
    """

    def __init__(self, op: ast.unaryop, operand: Expression, **kwargs: Any) -> None:
        super().__init__(op, Expression._cast(operand), **kwargs)


class Constant(Expression, ast.Constant):
    """A constant value.

    The `value` attribute contains the Python object it represents.
    types supported: int, float
    """

    def __init__(self, value: Number, kind: str | None = None, **kwargs: Any) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError("Constants must be numbers")
        super().__init__(value, kind, **kwargs)

    def __mul__(self, other: Any) -> BinOp | Constant:
        if isinstance(other, Constant):
            return Constant(self.value**other.value)
        if isinstance(other, (float, int)):
            return Constant(self.value * other)
        return super().__mul__(other)

    def __pow__(self, other: Number) -> Expression:
        if not isinstance(other, (int, float)):
            raise TypeError("Exponent must be a number")
        return Constant(self.value**other)


class Variable(Expression, ast.Name):
    """A variable.

    `id` holds the index as a string (becuase ast.Name requires a string).

    The special attribute `index` is added here for the purpose of storing
    the index of a variable in a solver's variable list: ``Variable('u', index=0)``
    """

    def __init__(self, id: str, index: int | None = None) -> None:
        self.index = index
        super().__init__(str(id), ctx=ast.Load())

    def __pow__(self, other: Number) -> Expression:
        if not isinstance(other, (int, float)):
            raise TypeError("Exponent must be a number")
        if other == 2:
            return BinOp(self, ast.Mult(), self)
        elif other == 1:
            return self
        raise ValueError("Only quadratic variables are supported")

    def __hash__(self) -> int:
        # allow use as dict key
        return id(self)

    def __int__(self) -> int:
        if self.index is None:
            raise TypeError(f"Variable {self!r} has no index")
        return int(self.index)

    __index__ = __int__

    def __repr__(self) -> str:
        return f"motile.Variables({self.id!r}, index={self.index!r})"


def _get_ilpy_relation(expr: Expression) -> ilpy.Relation | None:
    import ilpy

    # conversion between ast comparison operators and ilpy relations
    # TODO: support more less/greater than operators
    OPERATOR_MAP: dict[type[ast.cmpop], ilpy.Relation] = {
        ast.LtE: ilpy.Relation.LessEqual,
        ast.Eq: ilpy.Relation.Equal,
        ast.GtE: ilpy.Relation.GreaterEqual,
    }
    seen_compare = False
    relation: ilpy.Relation | None = None
    for sub in ast.walk(expr):
        if isinstance(sub, Compare):
            if seen_compare:
                raise ValueError("Only single comparisons are supported")

            op_type = type(sub.ops[0])
            try:
                relation = OPERATOR_MAP[op_type]
            except KeyError as e:
                raise ValueError(f"Unsupported comparison operator: {op_type}") from e
            seen_compare = True
    return ilpy.Relation(relation) if relation is not None else None


def _get_coeff_indices(
    expr: Expression,
) -> tuple[dict[int, float], dict[tuple[int, int], float], float]:
    l_coeffs: dict[int, float] = {}
    q_coeffs: dict[tuple[int, int], float] = {}
    constant = 0.0
    for var, coefficient in _get_coefficients(expr).items():
        if var is None:
            constant = coefficient
        elif isinstance(var, tuple):
            q_coeffs[(_ensure_index(var[0]), _ensure_index(var[1]))] = coefficient
        elif coefficient != 0:
            l_coeffs[_ensure_index(var)] = coefficient
    return l_coeffs, q_coeffs, constant


def _ensure_index(var: Variable) -> int:
    if var.index is None:
        raise ValueError("All variables in an Expression must have an index")
    return var.index


def _get_coefficients(
    expr: Expression | ast.expr,
    coeffs: dict[Variable | None | tuple[Variable, Variable], float] | None = None,
    scale: int = 1,
    var_scale: Variable | None = None,
) -> dict[Variable | None | tuple[Variable, Variable], float]:
    """Get the coefficients of an expression.

    The coefficients are returned as a dictionary mapping Variable to coefficient.
    The key `None` is used for the constant term.  Quadratic coefficients are
    represented with a two-tuple of variables.

    Note also that expressions on the right side of a comparison are negated,
    (so that the comparison is effectively against zero.)

    Args:
        expr: The expression to get the coefficients of.
        coeffs: The dictionary to add the coefficients to. If not given, a new
            dictionary is created.
        scale: The scale to apply to the coefficients. This is used to negate
            expressions on the right side of a comparison or scale for multiplication.
        var_scale: The variable to scale by. This is used to represent multiplication
            or division between two variables.

    Example:
        >>> u = Variable('u')
        >>> v = Variable('v')
        >>> _get_coefficients(2 * u - 5 * v <= 7)
        {u: 2, v: -5, None: -7}

        coefficients are simplified in the process:
        >>> _get_coefficients(2 * u - (u + 2 * u) <= 7)
        {u: -1, None: -7}
    """
    if coeffs is None:
        coeffs = {}

    if isinstance(expr, Constant):
        if var_scale is not None:
            breakpoint()
        coeffs.setdefault(None, 0)
        coeffs[None] += expr.value * scale

    elif isinstance(expr, UnaryOp):
        if var_scale is not None:
            breakpoint()
        if isinstance(expr.op, ast.USub):
            scale = -scale
        _get_coefficients(expr.operand, coeffs, scale, var_scale)

    elif isinstance(expr, Variable):
        if var_scale is not None:
            # multiplication or division between two variables
            key = _sort_vars(expr, var_scale)
            coeffs.setdefault(key, 0)
            coeffs[key] += scale
        else:
            coeffs.setdefault(expr, 0)
            coeffs[expr] += scale

    elif isinstance(expr, Compare):
        if len(expr.ops) != 1:
            raise ValueError("Only single comparisons are supported")
        _get_coefficients(expr.left, coeffs, scale, var_scale)
        # negate the right hand side of the comparison
        _get_coefficients(expr.comparators[0], coeffs, scale * -1, var_scale)

    elif isinstance(expr, BinOp):
        if isinstance(expr.op, (ast.Mult, ast.Div)):
            _process_mult_op(expr, coeffs, scale, var_scale)
        elif isinstance(expr.op, (ast.Add, ast.UAdd, ast.USub, ast.Sub)):
            _get_coefficients(expr.left, coeffs, scale, var_scale)
            if isinstance(expr.op, (ast.USub, ast.Sub)):
                scale = -scale
            _get_coefficients(expr.right, coeffs, scale, var_scale)
        else:
            raise ValueError(f"Unsupported binary operator: {type(expr.op)}")

    else:
        breakpoint()
        raise ValueError(f"Unsupported expression type: {type(expr)}")

    return coeffs


def _sort_vars(v1: Variable, v2: Variable) -> tuple[Variable, Variable]:
    """Sort variables by index, or by id if index is None.

    This is so that a pair of variables can be used as a dictionary key.
    Without worrying about the order of the variables (and without using a set,
    which would exclude the possibility of having the same variable twice).
    """
    # two lines are used to tell mypy it's a length 2 tuple
    _v1, _v2 = sorted((v1, v2), key=lambda v: getattr(v, "index", id(v)))
    return _v1, _v2


def _process_mult_op(
    expr: BinOp,
    coeffs: dict[Variable | None | tuple[Variable, Variable], float],
    scale: int,
    var_scale: Variable | None = None,
) -> None:
    """Helper function for _get_coefficients to process multiplication and division."""
    if isinstance(expr.right, Constant):
        v = expr.right.value
        scale *= 1 / v if isinstance(expr.op, ast.Div) else v
        _get_coefficients(expr.left, coeffs, scale, var_scale)
    elif isinstance(expr.left, Constant):
        v = expr.left.value
        scale *= 1 / v if isinstance(expr.op, ast.Div) else v
        _get_coefficients(expr.right, coeffs, scale, var_scale)
    elif isinstance(expr.left, Variable):
        if var_scale is not None:
            raise TypeError("Cannot multiply by more than two variables.")
        _get_coefficients(expr.right, coeffs, scale, expr.left)
    elif isinstance(expr.right, Variable):
        if var_scale is not None:
            raise TypeError("Cannot multiply by more than two variables.")
        _get_coefficients(expr.left, coeffs, scale, expr.right)
    else:
        raise TypeError(
            "Unexpected multiplcation or division between "
            f"{type(expr.left)} and {type(expr.right)}"
        )


class _ExprSerializer(ast.NodeVisitor):
    """Serializes an :class:`Expression` into a string.

    Used above in `Expression.__str__`.
    """

    OP_MAP: ClassVar[
        dict[type[ast.operator] | type[ast.cmpop] | type[ast.unaryop], str]
    ] = {
        # ast.cmpop
        ast.Eq: "==",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        # ast.operator
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        # ast.unaryop
        ast.UAdd: "+",
        ast.USub: "-",
    }

    def __init__(self, node: Expression | None = None) -> None:
        self._result: list[str] = []

        def write(*params: ast.AST | str) -> None:
            for item in params:
                if isinstance(item, ast.AST):
                    self.visit(item)
                elif item:
                    self._result.append(item)

        self.write = write

        if node is not None:
            self.visit(node)

    def __str__(self) -> str:
        return "".join(self._result)

    def visit_Variable(self, node: Variable) -> None:
        self.write(node.id)

    def visit_Constant(self, node: ast.Constant) -> None:
        self.write(repr(node.value))

    def visit_Compare(self, node: ast.Compare) -> None:
        self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            self.write(f" {self.OP_MAP[type(op)]} ", right)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        opstring = f" {self.OP_MAP[type(node.op)]} "
        args: list[ast.AST | str] = [node.left, opstring, node.right]
        # wrap in parentheses if the left or right side is a binary operation
        if isinstance(node.op, ast.Mult):
            if isinstance(node.left, ast.BinOp):
                args[:1] = ["(", node.left, ")"]
            if isinstance(node.right, ast.BinOp):
                args[2:] = ["(", node.right, ")"]
        self.write(*args)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        sym = self.OP_MAP[type(node.op)]
        self.write(sym, " " if sym.isalpha() else "", node.operand)
