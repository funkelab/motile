from ..variables import EdgeSelected
from .costs import Costs


class EdgeSelection(Costs):
    """Costs for :class:`motile.variables.EdgeSelected` variables.

    Args:

        weight (float):
            The weight to apply to the cost given by the ``costs`` attribute of
            each edge.

        attribute (string):
            The name of the edge attribute to use to look up costs. Default is
            ``costs``.

        constant (float):
            A constant cost for each selected edge.
    """

    def __init__(self, weight, attribute='costs', constant=0.0):

        self.weight = weight
        self.attribute = attribute
        self.constant = constant

    def apply(self, solver):

        edge_variables = solver.get_variables(EdgeSelected)

        for edge, index in edge_variables.items():

            cost = (
                solver.graph.edges[edge][self.attribute] * self.weight +
                self.constant
            )

            solver.add_variable_cost(index, cost)
