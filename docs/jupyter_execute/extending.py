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
    {"id": 5, "t": 2, "x": 24, "score": 0.6},
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

solver.add_cost(NodeSelectedCost(weight=-1, attribute="score"))
solver.add_cost(EdgeSelectedCost(weight=-1, attribute="score"))
solver.add_cost(NodeAppearCost(constant=1))

solver.solve()


# In[4]:


from motile_toolbox.visualization import draw_solution

draw_solution(graph, solver, label_attribute="score")


# In[5]:


from motile.variables import NodeAppear


class LimitNumTracks(motile.constraints.Constraint):
    def __init__(self, num_tracks):
        self.num_tracks = num_tracks

    def instantiate(self, solver):
        appear_indicators = solver.get_variables(NodeAppear)
        yield sum([appear_indicators[n] for n in solver.graph.nodes]) <= self.num_tracks


# In[6]:


solver.add_constraint(LimitNumTracks(1))
solver.solve()


# In[7]:


draw_solution(graph, solver, label_attribute="score")


# In[8]:


from motile.variables import NodeSelected


class SillyCost(motile.costs.Cost):
    def __init__(self, position_attribute, weight=1.0):
        self.position_attribute = position_attribute
        self.weight = motile.costs.Weight(weight)

    def apply(self, solver):
        node_indicators = solver.get_variables(NodeSelected)

        for node_indicator, index in node_indicators.items():
            # x position of the node
            x = solver.graph.nodes[node_indicator][self.position_attribute]

            # costs can be negative (i.e., a reward)
            costs = -x

            solver.add_variable_cost(index, costs, weight=self.weight)


# In[9]:


print("Before adding silly cost:")
print(solver.get_variables(NodeSelected))

solver.add_cost(SillyCost("x", weight=0.02))

print("After adding silly cost:")
print(solver.get_variables(NodeSelected))


# In[10]:


solver.solve()


# In[11]:


draw_solution(graph, solver, label_attribute="score")


# In[12]:


from motile.variables import EdgeContinuation


class ContinuationPairs(motile.variables.Variable):
    @staticmethod
    def instantiate(solver):
        edge_pairs = [
            (in_edge, out_edge)
            # for each node
            for node in solver.graph.nodes
            # for each pair of incoming and outgoing edge
            for in_edge in solver.graph.prev_edges[node]
            for out_edge in solver.graph.next_edges[node]
        ]

        return edge_pairs

    @staticmethod
    def instantiate_constraints(solver):
        cont_indicators = solver.get_variables(EdgeContinuation)
        pair_indicators = solver.get_variables(ContinuationPairs)

        for (in_edge, out_edge), pair_index in pair_indicators.items():
            c1 = cont_indicators[in_edge]
            c2 = cont_indicators[out_edge]

            # pair indicator = 1 <=> both edges are active continuations
            yield pair_index <= c1
            yield pair_index <= c2
            yield pair_index >= c1 + c2 - 1


# In[13]:


class CurvatureCost(motile.costs.Cost):
    def __init__(self, position_attribute, weight=1.0):
        self.position_attribute = position_attribute
        self.weight = motile.costs.Weight(weight)

    def apply(self, solver):
        # get continuation pair variables
        pair_indicators = solver.get_variables(ContinuationPairs)

        for (in_edge, out_edge), index in pair_indicators.items():
            in_offset = self.get_edge_offset(solver.graph, in_edge)
            out_offset = self.get_edge_offset(solver.graph, out_edge)

            curvature_cost = abs(out_offset - in_offset)

            solver.add_variable_cost(index, curvature_cost, self.weight)

    def get_edge_offset(self, graph, edge):
        pos_v = graph.nodes[edge[1]][self.position_attribute]
        pos_u = graph.nodes[edge[0]][self.position_attribute]

        return pos_v - pos_u


# In[14]:


solver.add_cost(CurvatureCost("x", weight=0.1))
solver.solve()


# In[15]:


print(solver.get_variables(ContinuationPairs))
draw_solution(graph, solver, label_attribute="score")
