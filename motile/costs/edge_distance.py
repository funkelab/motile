from ..variables import EdgeSelected
from .costs import Costs
import numpy as np


class EdgeDistance(Costs):

    def __init__(self, position_attributes, weight=1.0):

        self.position_attributes = position_attributes
        self.weight = weight

    def apply(self, solver):

        edge_variables = solver.get_variables(EdgeSelected)

        for (u, v), index in edge_variables.items():

            pos_u = np.array([
                solver.graph.nodes[u][p]
                for p in self.position_attributes
            ])
            pos_v = np.array([
                solver.graph.nodes[v][p]
                for p in self.position_attributes
            ])

            cost = np.linalg.norm(pos_u - pos_v) * self.weight

            solver.add_variable_cost(index, cost)
