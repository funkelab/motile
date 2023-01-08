class NodeSelected:

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


class EdgeSelected:

    def __init__(self, index, edge):

        self.index = index
        self.edge = edge

    @staticmethod
    def instantiate(solver):

        num_edges = solver.graph.number_of_edges()
        indices = solver.allocate_variables(num_edges)

        variables = {
            edge: EdgeSelected(index, edge)
            for index, edge in zip(indices, solver.graph.edges)
        }

        return variables

class NodeAppear:

    def __init__(self, index, node):

        self.index = index
        self.node = node

    @staticmethod
    def instantiate(solver):

        num_nodes = solver.graph.number_of_nodes()
        indices = solver.allocate_variables(num_nodes)

        variables = {
            node: NodeAppear(index, node)
            for index, node in zip(indices, solver.graph.nodes)
        }

        return variables
