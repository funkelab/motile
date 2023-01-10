from .variable import Variable


class EdgeSelected(Variable):

    @staticmethod
    def instantiate(solver):

        num_edges = solver.graph.number_of_edges()
        indices = solver.allocate_variables(num_edges)

        variables = {
            edge: index
            for edge, index in zip(solver.graph.edges, indices)
        }

        return variables
