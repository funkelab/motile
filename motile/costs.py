from .variables import NodeSelected, EdgeSelected, NodeAppear


class NodeSelection:

    def __init__(self, weight, attribute='score', constant=0.0):

        self.weight = weight
        self.attribute = attribute
        self.constant = constant

    def apply(self, solver):

        node_variables = solver.get_variables(NodeSelected)

        for var in node_variables.values():

            index = var.index
            node = var.node

            cost = (
                solver.graph.nodes[node][self.attribute] * self.weight +
                self.constant
            )

            solver.add_variable_cost(index, cost)


class EdgeSelection:

    def __init__(self, weight, attribute='score', constant=0.0):

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


class Appear:

    def __init__(self, constant):

        self.constant = constant

    def apply(self, solver):

        appear_indicators = solver.get_variables(NodeAppear)

        for var in appear_indicators.values():
            solver.add_variable_cost(var.index, self.constant)
