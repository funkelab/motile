from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Iterable

from .edge_continuation import EdgeContinuation
from .variable import Variable

if TYPE_CHECKING:
    import ilpy

    from motile.solver import Solver

# A continuation pair is two edges sharing a middle node, both continuations.
# Each edge is tuple[int, int], so a pair is tuple[tuple[int, int], tuple[int, int]].
ContinuationPair = tuple[tuple[int, int], tuple[int, int]]


class EdgeContinuationPair(Variable["ContinuationPair"]):
    r"""Binary variable for each pair of consecutive continuation edges.

    For every node ``b`` with at least one incoming edge and one outgoing edge,
    and for every pair ``(e1, e2)`` where ``e1 = (a, b)`` and ``e2 = (b, c)``,
    this variable is 1 iff both edges are active continuations.

    This is coupled to the edge continuation variables as a product of two
    binaries:

    .. math::

        g_{e_1,e_2} &\leq c_{e_1}

        g_{e_1,e_2} &\leq c_{e_2}

        g_{e_1,e_2} &\geq c_{e_1} + c_{e_2} - 1

    where :math:`c_e` are edge continuation indicators and
    :math:`g_{e_1,e_2}` is the continuation pair indicator.
    """

    @staticmethod
    def instantiate(solver: Solver) -> Collection[ContinuationPair]:
        pairs: list[ContinuationPair] = []
        for node in solver.graph.nodes:
            prev_edges = solver.graph.prev_edges[node]
            next_edges = solver.graph.next_edges[node]
            if prev_edges and next_edges:
                for e_in in prev_edges:
                    for e_out in next_edges:
                        pairs.append((e_in, e_out))
        return pairs

    @staticmethod
    def instantiate_constraints(solver: Solver) -> Iterable[ilpy.Expression]:
        pair_indicators = solver.get_variables(EdgeContinuationPair)
        cont_indicators = solver.get_variables(EdgeContinuation)

        for (e1, e2), _ in pair_indicators.items():
            g = pair_indicators[(e1, e2)]
            c1 = cont_indicators[e1]
            c2 = cont_indicators[e2]

            # g = c1 AND c2
            yield g <= c1
            yield g <= c2
            yield g >= c1 + c2 - 1
