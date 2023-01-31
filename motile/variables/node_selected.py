from .variable import Variable


class NodeSelected(Variable):
    """A binary variable for each node that indicates whether the node is part
    of the solution or not.
    """

    @staticmethod
    def instantiate(solver):
        return solver.graph.nodes
