#!/usr/bin/env python

# In[1]:


import motile
import plotly.io as pio

pio.renderers.default = "sphinx_gallery"
import networkx as nx

cells = [
    {"id": 0, "t": 0, "x": 1, "score": 0.8},
    {"id": 1, "t": 0, "x": 25, "score": 0.1},
    {"id": 2, "t": 1, "x": 0, "score": 0.3},
    {"id": 3, "t": 1, "x": 26, "score": 0.4},
    {"id": 4, "t": 2, "x": 2, "score": 0.6},
    {"id": 5, "t": 2, "x": 24, "score": 0.3},
    {"id": 6, "t": 2, "x": 35, "score": 0.7},
]

edges = [
    {"source": 0, "target": 2, "score": 0.9},
    {"source": 1, "target": 3, "score": 0.9},
    {"source": 0, "target": 3, "score": 0.5},
    {"source": 1, "target": 2, "score": 0.5},
    {"source": 2, "target": 4, "score": 0.7},
    {"source": 3, "target": 5, "score": 0.7},
    {"source": 2, "target": 5, "score": 0.3},
    {"source": 3, "target": 4, "score": 0.3},
    {"source": 3, "target": 6, "score": 0.8},
]

graph = nx.DiGraph()
graph.add_nodes_from([(cell["id"], cell) for cell in cells])
graph.add_edges_from([(edge["source"], edge["target"], edge) for edge in edges])

graph = motile.TrackGraph(graph)


# In[2]:


from motile_toolbox.visualization import draw_track_graph

draw_track_graph(graph, alpha_attribute="score", label_attribute="score")


# In[3]:


from motile.constraints import MaxChildren, MaxParents
from motile.costs import EdgeSelectedCost, NodeAppearCost, NodeSelectedCost

solver = motile.Solver(graph)

solver.add_constraint(MaxParents(1))
solver.add_constraint(MaxChildren(1))

solver.add_cost(NodeSelectedCost(weight=1, attribute="score"))
solver.add_cost(EdgeSelectedCost(weight=-1, attribute="score", constant=0.5))
solver.add_cost(NodeAppearCost(constant=1))


# In[4]:


solver.weights


# In[5]:


from motile.variables import EdgeSelected, NodeSelected
from motile_toolbox.visualization import draw_solution

solver.solve()


# In[6]:


print(solver.get_variables(NodeSelected))
print(solver.get_variables(EdgeSelected))

draw_solution(graph, solver, label_attribute="score")


# In[7]:


solver.weights[("EdgeSelectedCost", "weight")] = -2

solution = solver.solve()


# In[8]:


print(solver.weights)
print(solver.get_variables(NodeSelected))
print(solver.get_variables(EdgeSelected))

draw_solution(graph, solver, label_attribute="score")


# In[9]:


graph.nodes[0]["gt"] = True
graph.nodes[2]["gt"] = True
graph.nodes[4]["gt"] = True
graph.nodes[5]["gt"] = False

graph.edges[(0, 2)]["gt"] = True
graph.edges[(2, 4)]["gt"] = True
graph.edges[(2, 5)]["gt"] = False


# In[10]:


node_colors = [
    (0, 0, 0) if "gt" not in node else ((0, 128, 0) if node["gt"] else (255, 140, 0))
    for node in graph.nodes.values()
]
edge_colors = [
    (0, 0, 0) if "gt" not in edge else ((0, 128, 0) if edge["gt"] else (255, 140, 0))
    for edge in graph.edges.values()
]

draw_track_graph(
    graph,
    alpha_func=(lambda x: "gt" in graph.nodes[x], lambda x: "gt" in graph.edges[x]),
    node_color=node_colors,
    edge_color=edge_colors,
)


# In[11]:


# this suppresses logging output from structsvm that can fail the docs build
import logging

logging.getLogger("structsvm.bundle_method").setLevel(logging.CRITICAL)


# In[12]:


solver.fit_weights(gt_attribute="gt", regularizer_weight=0.01)
optimal_weights = solver.weights


# In[13]:


optimal_weights


# In[14]:


solver = motile.Solver(graph)

solver.add_constraint(MaxParents(1))
solver.add_constraint(MaxChildren(1))

solver.add_cost(NodeSelectedCost(weight=1, attribute="score"))
solver.add_cost(EdgeSelectedCost(weight=-2, attribute="score", constant=1))
solver.add_cost(NodeAppearCost(constant=1))

solver.weights.from_ndarray(optimal_weights.to_ndarray())

solver.solve()


# In[15]:


draw_solution(graph, solver, label_attribute="score")
