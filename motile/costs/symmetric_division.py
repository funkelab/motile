from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..variables import EdgeSelected
from .cost import Cost
from .weight import Weight

if TYPE_CHECKING:
    import networkx as nx

    from motile.solver import Solver


class SymmetricDivision(Cost):
    """Cost for the distance between a parent and the mean locations of its children.

    This cost requires division to be represented as "hyperedges" in the graph.
    That is, there is an edge (a, (b,c)) for every possible division with node a
    as the parent and nodes b and c as the children.

    Args:
        position_attribute:
            The name of the node attribute that corresponds to the spatial
            position. Can also be given as a tuple of multiple coordinates,
            e.g., ``('z', 'y', 'x')``.

        weight:
            The weight to apply to the distance to convert it into a cost.

        constant:
            A constant cost for each selected division. Default is ``0.0``.
    """

    def __init__(
        self,
        position_attribute: str | tuple[str, ...],
        weight: float = 1,
        constant: float = 0,
    ) -> None:
        self.position_attribute = position_attribute
        self.weight = Weight(weight)
        self.constant = Weight(constant)

    def apply(self, solver: Solver) -> None:
        edge_variables = solver.get_variables(EdgeSelected)
        for key, index in edge_variables.items():
            if solver.graph.is_hyperedge(key):
                (start,) = key[0]
                end1, end2 = key[1]
                pos_start = self.__get_node_position(solver.graph, start)
                pos_end1 = self.__get_node_position(solver.graph, end1)
                pos_end2 = self.__get_node_position(solver.graph, end2)
                feature = np.linalg.norm(pos_start - 0.5 * (pos_end1 + pos_end2))
                solver.add_variable_cost(index, feature, self.weight)
                solver.add_variable_cost(index, 1.0, self.constant)
            else:
                solver.add_variable_cost(index, 0.0, self.weight)
                solver.add_variable_cost(index, 0.0, self.constant)

    def __get_node_position(self, graph: nx.DiGraph, node: int) -> np.ndarray:
        if isinstance(self.position_attribute, tuple):
            return np.array([graph.nodes[node][p] for p in self.position_attribute])
        else:
            return np.array(graph.nodes[node][self.position_attribute])
