from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Collection, Iterable

from .edge_selected import EdgeSelected
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile._types import Edge
    from motile.solver import Solver

    EdgeGroupKey = tuple[Edge, ...]


class EdgeGroup(Variable["EdgeGroupKey"]):
    r"""Binary variable for groups of edges.

    Each group variable is 1 if and only if all edges in
    the group are selected.

    This is enforced by two linear constraints per group:

    .. math::

        n \\cdot x_g - \\sum_{e \\in g} x_e &\\leq 0

        x_g - \\sum_{e \\in g} x_e &\\geq -(n - 1)

    where :math:`x_g` is the group indicator, :math:`x_e`
    are edge selection indicators, and :math:`n` is the
    number of edges in the group.

    Edge groups are set via the class variable
    ``_edge_groups`` by
    :class:`~motile.costs.EdgeGroupSelection` before
    instantiation.
    """

    _edge_groups: ClassVar[list[EdgeGroupKey]] = []

    @staticmethod
    def instantiate(
        solver: Solver,
    ) -> Collection[EdgeGroupKey]:
        return EdgeGroup._edge_groups

    @staticmethod
    def instantiate_constraints(
        solver: Solver,
    ) -> Iterable[ilpy.Expression]:
        edge_indicators = solver.get_variables(EdgeSelected)
        group_indicators = solver.get_variables(EdgeGroup)

        for group in EdgeGroup._edge_groups:
            x_g = group_indicators[group]
            n = len(group)
            s = sum(edge_indicators[e] for e in group)
            yield n * x_g - s <= 0
            yield x_g - s >= -(n - 1)
