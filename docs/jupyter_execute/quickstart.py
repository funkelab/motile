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


import motile
from motile_toolbox.visualization import draw_solution, draw_track_graph

draw_track_graph(graph, alpha_attribute="score", label_attribute="score")


# In[3]:


import motile

# create a motile solver
solver = motile.Solver(graph)


# In[4]:


from motile.costs import EdgeSelectedCost, NodeSelectedCost

solver.add_cost(NodeSelectedCost(weight=-1.0, attribute="score"))
solver.add_cost(EdgeSelectedCost(weight=-1.0, attribute="score"))


# In[5]:


solution = solver.solve()


# In[6]:


from motile.variables import EdgeSelected, NodeSelected

node_selected = solver.get_variables(NodeSelected)
edge_selected = solver.get_variables(EdgeSelected)

for node in graph.nodes:
    if solution[node_selected[node]] > 0.5:
        print(f"Node {node} has been selected")
for u, v in graph.edges:
    if solution[edge_selected[(u, v)]] > 0.5:
        print(f"Edge {(u, v)} has been selected")


# In[7]:


draw_solution(graph, solver, label_attribute="score")


# In[8]:


from motile.constraints import MaxChildren, MaxParents

solver.add_constraint(MaxParents(1))
solver.add_constraint(MaxChildren(1))


# In[9]:


solution = solver.solve()


# In[10]:


draw_solution(graph, solver, label_attribute="score")


# In[11]:


from motile.costs import NodeAppearCost

solver.add_cost(NodeAppearCost(constant=1.0))


# In[12]:


solution = solver.solve()


# In[13]:


draw_solution(graph, solver, label_attribute="score")


# In[14]:


# create a motile solver
solver = motile.Solver(graph)


# In[15]:


solver.add_cost(NodeSelectedCost(weight=-1.0, attribute="score"))
solver.add_cost(EdgeSelectedCost(weight=-1.0, attribute="score"))
solver.add_cost(NodeAppearCost(constant=1.0))


# In[16]:


solver.add_constraint(MaxParents(1))
solver.add_constraint(MaxChildren(2))


# In[17]:


solution = solver.solve()


# In[18]:


solution = solver.solve()
draw_solution(graph, solver, label_attribute="score")
