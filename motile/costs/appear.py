from ..variables import NodeAppear
from .costs import Costs
from .weight import Weight


class Appear(Costs):
    """Costs for :class:`motile.variables.NodeAppear` variables.

    Args:

        constant (float):
            A constant cost for each node that starts a track.
    """

    def __init__(self, constant):

        self.constant = Weight(constant)

    def apply(self, solver):

        appear_indicators = solver.get_variables(NodeAppear)

        for index in appear_indicators.values():
            solver.add_variable_cost(index, 1.0, self.constant)
