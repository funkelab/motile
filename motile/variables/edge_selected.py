from .variable import Variable


class EdgeSelected(Variable):
    """A binary variable for each edge that indicates whether the edge is part
    of the solution or not.
    """

    @staticmethod
    def instantiate(solver):
        return solver.graph.edges
