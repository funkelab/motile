# import networkx as nx
# import numpy as np

# import motile
# from motile import TrackGraph
# from motile.costs import NodeSelection
# from motile.linear_svm import fit_weights
# from motile.variables import NodeSelected


# def test_linear_svm_node_selection():
#     """Test linear SVM fitting with node selection costs.

#     Graph structure:
#         t=0: Four nodes with different score1 and score2 values
#             - node 0: score1=0.0, score2=0.0, gt=False
#             - node 1: score1=1.0, score2=0.0, gt=False
#             - node 2: score1=0.0, score2=1.0, gt=False
#             - node 3: score1=1.0, score2=1.0, gt=True

#     The linear SVM should learn that both features are needed to
#     select the correct node (node 3).
#     """
#     # Create nodes with different feature combinations
#     cells = [
#         {"id": 0, "t": 0, "score1": 0.0, "score2": 0.0, "gt": 0},
#         {"id": 1, "t": 0, "score1": 1.0, "score2": 0.0, "gt": 0},
#         {"id": 2, "t": 0, "score1": 0.0, "score2": 1.0, "gt": 0},
#         {"id": 3, "t": 0, "score1": 1.0, "score2": 1.0, "gt": 1},
#     ]

#     nx_graph = nx.DiGraph()
#     nx_graph.add_nodes_from([(cell["id"], cell) for cell in cells])

#     graph = TrackGraph(nx_graph)

#     # Create solver with two node selection costs
#     solver = motile.Solver(graph)
#     solver.add_cost(NodeSelection(weight=1.0, attribute="score1", constant=0.0))
#     solver.add_cost(NodeSelection(weight=1.0, attribute="score2", constant=0.0))

#     # Fit weights using linear SVM
#     learned_weights = fit_weights(solver, gt_attribute="gt")

#     # The learned weights should be positive for both features
#     # since both are needed to identify the correct node
#     assert len(learned_weights) == 4  # 2 costs � 2 parameters (weight + constant)

#     # Check that the learned weights make sense
#     # Both weight parameters should be positive (or at least non-negative)
#     # to encourage selection when both scores are high
#     assert learned_weights[0] >= 0  # score1 weight
#     assert learned_weights[2] >= 0  # score2 weight

#     # Apply learned weights and verify the solution
#     solver.weights.from_ndarray(learned_weights)
#     solution = solver.solve()

#     node_indicators = solver.get_variables(NodeSelected)
#     selected_nodes = [
#         node for node, index in node_indicators.items() if solution[index] > 0.5
#     ]

#     # Only node 3 (with gt=True) should be selected
#     assert selected_nodes == [3]
