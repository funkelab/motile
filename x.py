import sys

import motile
from motile.constraints import MaxChildren, MaxParents
from motile.costs import Appear, EdgeDistance, EdgeSelection, NodeSelection, Split
from motile.data import arlo_graph

graph = arlo_graph()

solver = motile.Solver(graph)
solver.add_costs(NodeSelection(weight=-1.0, attribute="score", constant=-100.0))
solver.add_costs(
    EdgeSelection(weight=0.5, attribute="prediction_distance", constant=-1.0)
)
solver.add_costs(EdgeDistance(position_attributes=("x",), weight=0.5))
solver.add_costs(Appear(constant=200.0, attribute="score", weight=-1.0))
solver.add_costs(Split(constant=100.0, attribute="score", weight=1.0))

solver.add_constraints(MaxParents(1))
solver.add_constraints(MaxChildren(2))
solver.solve(on_event=print, verbose=False)
sys.exit()
