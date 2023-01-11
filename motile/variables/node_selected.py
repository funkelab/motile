from .variable import Variable


class NodeSelected(Variable):

    @staticmethod
    def instantiate(solver):
        return solver.graph.nodes
