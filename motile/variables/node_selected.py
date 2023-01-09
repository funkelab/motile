from .variable import Variable


class NodeSelected(Variable):

    def __init__(self, index, node):

        self.index = index
        self.node = node

    @staticmethod
    def instantiate(solver):

        num_nodes = solver.graph.number_of_nodes()
        indices = solver.allocate_variables(num_nodes)

        variables = {
            node: NodeSelected(index, node)
            for index, node in zip(indices, solver.graph.nodes)
        }

        return variables
