from __future__ import annotations

from typing import Collection, Hashable, Iterable

import pytest
from motile import Solver, data
from motile.expressions import Expression
from motile.variables import Variables


@pytest.mark.parametrize("VarCls", Variables.__subclasses__())
def test_variable_subclass_protocols(VarCls: type[Variables]) -> None:
    """Test that all Variable subclasses properly implement the Variable protocol."""
    solver = Solver(data.arlo_graph())

    keys = VarCls.instantiate(solver)
    assert isinstance(keys, Collection)
    assert all(isinstance(k, Hashable) for k in keys)

    constraints = VarCls.instantiate_constraints(solver)
    assert isinstance(constraints, Iterable)
    assert all(isinstance(c, Expression) for c in constraints)
