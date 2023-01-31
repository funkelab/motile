from ..variables import NodeSelected
from .costs import Costs


class NodeSelection(Costs):
    """Costs for :class:`motile.variables.NodeSelected` variables.

    Args:

        weight (float):
            The weight to apply to the cost given by the ``costs`` attribute of
            each node.

        attribute (string):
            The name of the node attribute to use to look up costs. Default is
            ``costs``.

        constant (float):
            A constant cost for each selected node.
    """

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
