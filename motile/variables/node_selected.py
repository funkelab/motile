from .variable import Variable


class NodeSelected(Variable):

    @staticmethod
    def instantiate(solver):

        num_nodes = solver.graph.number_of_nodes()
        indices = solver.allocate_variables(num_nodes)

        variables = {
            node: index
            for node, index in zip(solver.graph.nodes, indices)
        }

        return variables
