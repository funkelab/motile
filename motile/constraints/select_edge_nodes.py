from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ..variables import EdgeSelected, NodeSelected
from .constraint import Constraint

if TYPE_CHECKING:
    from ilpy.expressions import Expression

    from motile.solver import Solver


class SelectEdgeNodes(Constraint):
    r"""Ensures that if an edge is selected, its nodes are selected as well.

    .. NOTE::

        This class is for internal use.

    If :math:`(u, v)` is selected, :math:`u` and :math:`v` have to be selected as well.

    Adds the following linear constraint for each edge :math:`e = (u,v)`:

    .. math::

      2 x_e - x_u - x_v \leq 0

    This constraint will be added by default to any :class:`~motile.Solver` instance.
    """

    def instantiate(self, solver: Solver) -> Iterable[Expression]:
        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        for edge in solver.graph.edges:
            nodes = list(solver.graph.nodes_of(edge))
            x_e = edge_indicators[edge]
            yield len(nodes) * x_e - sum(node_indicators[n] for n in nodes) <= 0
