from __future__ import annotations

from typing import Collection, Hashable, Iterable

import ilpy
import pytest
from motile import Solver, TrackGraph
from motile.variables import Variable


@pytest.mark.parametrize("VarCls", Variable.__subclasses__())
def test_variable_subclass_protocols(
    arlo_graph: TrackGraph, VarCls: type[Variable]
) -> None:
    """Test that all Variable subclasses properly implement the Variable protocol."""
    solver = Solver(arlo_graph)

    keys = VarCls.instantiate(solver)
    assert isinstance(keys, Collection)
    assert all(isinstance(k, Hashable) for k in keys)

    constraints = VarCls.instantiate_constraints(solver)
    assert isinstance(constraints, Iterable)
    assert all(isinstance(c, (ilpy.Expression, ilpy.Constraint)) for c in constraints)
