from ..variables import NodeSplit
from .costs import Costs
from .weight import Weight


class Split(Costs):
    """Costs for :class:`motile.variables.NodeSplit` variables.

    Args:

        constant (float):
            A constant cost for each node that has more than one selected
            child.
    """

    def __init__(self, constant):

        self.constant = Weight(constant)

    def apply(self, solver):

        split_indicators = solver.get_variables(NodeSplit)

        for index in split_indicators.values():
            solver.add_variable_cost(index, 1.0, self.constant)
