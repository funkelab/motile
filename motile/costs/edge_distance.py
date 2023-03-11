import numpy as np

from ..variables import EdgeSelected
from .costs import Costs
from .weight import Weight
import numpy as np


class EdgeDistance(Costs):
    """Costs for :class:`motile.variables.EdgeSelected` variables, based on the
    spatial distance of the incident nodes.

    Args:

        position_attributes (tuple of string):
            The names of the node attributes that correspond to their spatial
            position, e.g., ``('z', 'y', 'x')``.

        weight (float):
            The weight to apply to the distance to convert it into a cost.
    """

    def __init__(self, position_attributes, weight=1.0):

        self.position_attributes = position_attributes
        self.weight = Weight(weight)

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

            feature = np.linalg.norm(pos_u - pos_v)

            solver.add_variable_cost(index, feature, self.weight)
