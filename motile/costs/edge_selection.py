from ..variables import EdgeSelected
from .costs import Costs


class EdgeSelection(Costs):

    def __init__(self, weight, attribute='costs', constant=0.0):

        self.weight = weight
        self.attribute = attribute
        self.constant = constant

    def apply(self, solver):

        edge_variables = solver.get_variables(EdgeSelected)

        for var in edge_variables.values():

            index = var.index
            edge = var.edge

            cost = (
                solver.graph.edges[edge][self.attribute] * self.weight +
                self.constant
            )

            solver.add_variable_cost(index, cost)
