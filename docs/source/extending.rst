.. _sec_extending:

Extending ``motile``
====================

.. admonition:: written by Jan Funke
  :class: hint

  :jupyter-download-notebook:`Download this page as a Jupyter notebook<extending>`

.. automodule:: motile
   :noindex:

``motile`` ships with some basic tracking variables, constraints, and costs
(see the :ref:`sec_api` for a complete list). In some situations, you might
want to extend ``motile`` to fit your specific application. This tutorial will
show you how to implement new constraints, variables, and costs.

Consider the following example track ``graph``, where each node is a potential
object and each edge a potential link of objects between frames:

.. admonition:: (click here to see how to create the example track graph)
  :class: hint, dropdown

  .. jupyter-execute::

    import motile
    import networkx as nx

    cells = [
            {"id": 0, "t": 0, "x": 1, "score": 0.8},
            {"id": 1, "t": 0, "x": 25, "score": 0.1},
            {"id": 2, "t": 1, "x": 0, "score": 0.3},
            {"id": 3, "t": 1, "x": 26, "score": 0.4},
            {"id": 4, "t": 2, "x": 2, "score": 0.6},
            {"id": 5, "t": 2, "x": 24, "score": 0.6},
            {"id": 6, "t": 2, "x": 35, "score": 0.7}
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
        {"source": 3, "target": 6, "score": 0.8}
    ]

    graph = nx.DiGraph()
    graph.add_nodes_from([
        (cell["id"], cell)
        for cell in cells
    ])
    graph.add_edges_from([
        (edge["source"], edge["target"], edge)
        for edge in edges
    ])

    graph = motile.TrackGraph(graph)

.. jupyter-execute::

  from motile_toolbox.visualization import draw_track_graph

  draw_track_graph(graph, alpha_attribute="score", label_attribute="score")

We will start with a simple model: the costs for selecting nodes and edges
should depend on their ``score`` attribute, and the start of a track should
have a positive cost as well. Furthermore, we are only interested in
single-object tracks, i.e., tracks don't merge or split. The solver for this
model is:

.. jupyter-execute::
  :hide-output:

  from motile.constraints import MaxParents, MaxChildren
  from motile.costs import NodeSelection, EdgeSelection, Appear

  solver = motile.Solver(graph)

  solver.add_constraint(MaxParents(1))
  solver.add_constraint(MaxChildren(1))

  solver.add_cost(NodeSelection(weight=-1, attribute="score"))
  solver.add_cost(EdgeSelection(weight=-1, attribute="score"))
  solver.add_cost(Appear(constant=1))

  solver.solve()

...and our initial solution looks like this:

.. jupyter-execute::

  from motile_toolbox.visualization import draw_solution

  draw_solution(graph, solver, label_attribute="score")

Adding Constraints
------------------

New constraints are introduced by subclassing :class:`Constraint
<motile.constraints.Constraint>` and implementing the :func:`instantiate
<motile.constraints.Constraint.instantiate>` method. This method should return
a list of ``ilpy.Constraint``.

Imagine we know precisely that we want to track at most :math:`k` objects, but
we don't know beforehand which of the many objects in the track graph those
are. We are thus interested in finding at most :math:`k` tracks with minimal
costs.

This can be done with a constraint as follows:

.. jupyter-execute::

  import ilpy
  from motile.variables import NodeAppear


  class LimitNumTracks(motile.constraints.Constraint):

    def __init__(self, num_tracks):
        self.num_tracks = num_tracks

    def instantiate(self, solver):

        appear_indicators = solver.get_variables(NodeAppear)

        constraint = ilpy.Constraint()
        for appear_indicator, index in appear_indicators.items():
          constraint.set_coefficient(index, 1.0)
        constraint.set_relation(ilpy.Relation.LessEqual)
        constraint.set_value(self.num_tracks)

        return [constraint]

The ``instantiate`` method gets access to the solver the constraint is added
to. Through the solver, we can then access variables to formulate constraints
on them. Here, we make use of the :class:`NodeAppear
<motile.variables.NodeAppear>` variables: Simply counting how many nodes are
marked as "appear" gives us the number of selected tracks. We then require that
this number be less than or equal to ``num_tracks``.

In other words, we formulated a constraint by enforcing a certain relation to
hold between a subset of variables. Note that we didn't have to do anything
special to *create* the node appear variables: we simply ask the solver for
them, and if they haven't been added to the solver already, they will be added
automatically.

Once implemented, the constraint can simply be added to the solver by
instantiating the new class:

.. jupyter-execute::
  :hide-output:

  solver.add_constraint(LimitNumTracks(1))
  solver.solve()

.. jupyter-execute::

  draw_solution(graph, solver, label_attribute="score")

Indeed, we have limited the solution to contain at most one track.

Adding Costs
------------

We might want to add custom costs to ``motile`` that are not already covered by
the existing ones. For the sake of this tutorial, let's say we want to make the
selection of nodes cheaper the higher up the node is in space. For obvious
reasons, let's call this new cost ``SillyCost``.

Costs in ``motile`` are added by subclassing :class:`Cost
<motile.costs.Cost>` and implementing the :func:`apply
<motile.costs.Cost.apply>` method:

.. jupyter-execute::

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

Similar to adding constraints, we simply ask the solver for the variables we
want to add costs for and add them to the inference problem via
:func:`Solver.add_variable_cost <motile.Solver.add_variable_cost>`.

We can now add those costs in the same way others are added, i.e.:

.. jupyter-execute::

  print("Before adding silly cost:")
  print(solver.get_variables(NodeSelected))

  solver.add_cost(SillyCost('x', weight=0.02))

  print("After adding silly cost:")
  print(solver.get_variables(NodeSelected))

As we can see, our new cost have been applied to each ``NodeSelected``
variable and nodes with a larger ``x`` value are now cheaper than others.

Solving again will now select the upper one of the possible tracks in the track
graph:

.. jupyter-execute::
  :hide-output:

  solver.solve()

.. jupyter-execute::

  draw_solution(graph, solver, label_attribute="score")

Adding Variables
----------------

Variables in ``motile`` are added by subclassing the :class:`Variable
<motile.variables.Variable>` class. Subclasses need to implement at least a
static method :func:`instantiate <motile.variables.Variable.instantiate>`. This
method should return keys for *what* kind of things we would like to create a
variable for. This should be a list of anything that is hashable (the keys will
be used in a dictionary).

If, for example, we would like to create a new variable for each edge in the
track graph, we would simply return a list of tuples, each tuple representing
an edge (``graph.edges`` would fit that, in this case).

Variables can also be introduced for other things that are not nodes or edges.
We could create variables only for a subset of nodes, for pairs of edges, or
the number of division events.

Let's say we want to add new variables for *pairs of edges* that leave and
enter the same node. Having such a variable might be useful to, for example,
measure the curvature of a track and put a cost on that.

To create our new variables, we simply return a list of all pairs of edges we
wish to have a variable for in :func:`instantiate
<motile.variables.Variable.instantiate>`. However, declaring those variables
alone is not sufficient. To give them semantic meaning, we also have to make
sure that our edge-pair variables are set to 1 if the two edges they represent
have been selected, and 0 otherwise. To that end, we also add constraints that
are specific to our variables by overriding the :func:`instantiate_constraints
<motile.variables.Variable.instantiate_constraints>` method, such that our
variables are linked to the already existing :class:`EdgeSelected
<motile.variables.EdgeSelected>` variables.

The complete variable declaration looks like this:

.. jupyter-execute::

  import ilpy
  from motile.variables import EdgeSelected


  class EdgePairs(motile.variables.Variable):

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

        edge_indicators = solver.get_variables(EdgeSelected)
        edge_pair_indicators = solver.get_variables(EdgePairs)

        constraints = []
        for (in_edge, out_edge), pair_index in edge_pair_indicators.items():

            in_edge_index = edge_indicators[in_edge]
            out_edge_index = edge_indicators[out_edge]

            # edge pair indicator = 1 <=> in edge = 1 and out edge = 1
            constraint = ilpy.Constraint()
            constraint.set_coefficient(pair_index, 2)
            constraint.set_coefficient(in_edge_index, -1)
            constraint.set_coefficient(out_edge_index, -1)
            constraint.set_relation(ilpy.Relation.LessEqual)
            constraint.set_value(0)
            constraints.append(constraint)

            constraint = ilpy.Constraint()
            constraint.set_coefficient(pair_index, -1)
            constraint.set_coefficient(in_edge_index, 1)
            constraint.set_coefficient(out_edge_index, 1)
            constraint.set_relation(ilpy.Relation.LessEqual)
            constraint.set_value(1)
            constraints.append(constraint)

        return constraints

Variables on their own, however, don't do anything yet. They only start to
affect the solution if they are involved in constraints or have a cost.

The following defines a cost on our new variables, which loosely approximate the
local curvature of the track:

.. jupyter-execute::

  class CurvatureCost(motile.costs.Cost):

      def __init__(self, position_attribute, weight=1.0):
          self.position_attribute = position_attribute
          self.weight = motile.costs.Weight(weight)

      def apply(self, solver):

          # get edge pair variables
          edge_pair_indicators = solver.get_variables(EdgePairs)

          for (in_edge, out_edge), index in edge_pair_indicators.items():

              in_offset = self.get_edge_offset(solver.graph, in_edge)
              out_offset = self.get_edge_offset(solver.graph, out_edge)

              curvature_cost = abs(out_offset - in_offset)

              solver.add_variable_cost(index, curvature_cost, self.weight)

      def get_edge_offset(self, graph, edge):

          pos_v = graph.nodes[edge[1]][self.position_attribute]
          pos_u = graph.nodes[edge[0]][self.position_attribute]

          return pos_v - pos_u

As before, we don't have to do anything special to add the variables: we simply
ask the solver for them, and if they don't exist yet, they will be
instantiated.

We can now add those costs to our solvers, which in turn makes use of our newly
added variables:

.. jupyter-execute::
  :hide-output:

  solver.add_cost(CurvatureCost('x', weight=0.1))
  solver.solve()

Let's inspect the solution!

.. jupyter-execute::

  print(solver.get_variables(EdgePairs))
  draw_solution(graph, solver, label_attribute="score")
