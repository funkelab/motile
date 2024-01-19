from __future__ import annotations

from typing import TYPE_CHECKING

import ilpy

from motile.constraints import Constraint
from motile.variables import EdgeSelected

if TYPE_CHECKING:
    from motile.solver import Solver


class InOutSymmetry(Constraint):
    r"""Ensures that all nodes, apart from the ones in the first and last
    frame, have as many incoming edges as outgoing edges.

    Adds the following linear constraint for nodes :math:`v` not in first or
    last frame:

    .. math::
          \sum_{e \in \\text{in_edges}(v)} x_e = \sum{e \in \\text{out_edges}(v)} x_e
    """

    def instantiate(self, solver: Solver) -> list[ilpy.Constraint]:
        edge_indicators = solver.get_variables(EdgeSelected)
        start, end = solver.graph.get_frames()

        constraints = []
        for node, attrs in solver.graph.nodes.items():
            constraint = ilpy.Constraint()

            if solver.graph.frame_attribute in attrs and attrs[
                solver.graph.frame_attribute
            ] not in (
                start,
                end - 1,  # type: ignore
            ):
                for prev_edge in solver.graph.prev_edges[node]:
                    ind_e = edge_indicators[prev_edge]
                    constraint.set_coefficient(ind_e, 1)
                for next_edge in solver.graph.next_edges[node]:
                    ind_e = edge_indicators[next_edge]
                    constraint.set_coefficient(ind_e, -1)
                constraint.set_relation(ilpy.Relation.Equal)
                constraint.set_value(0)

                constraints.append(constraint)

        return constraints
