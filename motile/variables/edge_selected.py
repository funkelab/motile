from .variable import Variable


class EdgeSelected(Variable):

    @staticmethod
    def instantiate(solver):
        return solver.graph.edges
