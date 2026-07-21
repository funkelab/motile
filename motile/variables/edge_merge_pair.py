from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from .edge_merge import EdgeMerge
from .variable import Variable

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable

    import ilpy

    from motile.solver import Solver

MergePair = tuple[tuple[int, int], tuple[int, int]]


class EdgeMergePair(Variable["MergePair"]):
    r"""Binary variable for each pair of edges that could form a merge.

    For every node with at least two incoming edges, and for every pair of
    those incoming edges ``(e1, e2)``, this variable is 1 iff both edges are
    selected (i.e., the pair is active as a merge).

    This is coupled to the edge selection variables as a product of two
    binaries:

    .. math::

        g_{e_1,e_2} &\leq x_{e_1}

        g_{e_1,e_2} &\leq x_{e_2}

        g_{e_1,e_2} &\geq x_{e_1} + x_{e_2} - 1

    where :math:`x_e` are edge merge indicators and
    :math:`g_{e_1,e_2}` is the merge group indicator.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[MergePair]:
        groups: list[MergePair] = []
        for node in solver.graph.nodes:
            prev_edges = solver.graph.prev_edges[node]
            if len(prev_edges) >= 2:
                for e1, e2 in combinations(prev_edges, 2):
                    groups.append((e1, e2))
        return groups

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        group_indicators = solver.get_variables(EdgeMergePair)
        edge_indicators = solver.get_variables(EdgeMerge)

        for (e1, e2), _ in group_indicators.items():
            g = group_indicators[(e1, e2)]
            x1 = edge_indicators[e1]
            x2 = edge_indicators[e2]

            # g = x1 AND x2
            yield g <= x1
            yield g <= x2
            yield g >= x1 + x2 - 1
