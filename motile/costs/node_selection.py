from ..variables import NodeSelected
from .costs import Costs


class NodeSelection(Costs):

    def __init__(self, weight, attribute='costs', constant=0.0):

        self.weight = weight
        self.attribute = attribute
        self.constant = constant

    def apply(self, solver):

        node_variables = solver.get_variables(NodeSelected)

        for node, index in node_variables.items():

            cost = (
                solver.graph.nodes[node][self.attribute] * self.weight +
                self.constant
            )

            solver.add_variable_cost(index, cost)

