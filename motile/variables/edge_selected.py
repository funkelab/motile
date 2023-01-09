from .variable import Variable


class EdgeSelected(Variable):

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
