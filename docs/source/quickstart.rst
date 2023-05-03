.. _sec_quickstart:

Quickstart
==========

.. automodule:: motile
   :noindex:

:jupyter-download-notebook:`Download this page as a Jupyter notebook<quickstart>`

Consider the following example track ``graph``, where each node is a potential
object and each edge a potential link of objects between frames:

.. admonition:: (click here to see how to create the example track graph)
  :class: hint, dropdown

  .. jupyter-execute::

    import motile
    import networkx as nx

    cells = [
            {'id': 0, 't': 0, 'x': 1, 'score': 0.8},
            {'id': 1, 't': 0, 'x': 25, 'score': 0.1},
            {'id': 2, 't': 1, 'x': 0, 'score': 0.3},
            {'id': 3, 't': 1, 'x': 26, 'score': 0.4},
            {'id': 4, 't': 2, 'x': 2, 'score': 0.6},
            {'id': 5, 't': 2, 'x': 24, 'score': 0.3},
            {'id': 6, 't': 2, 'x': 35, 'score': 0.7}
    ]

    edges = [
        {'source': 0, 'target': 2, 'score': 0.9},
        {'source': 1, 'target': 3, 'score': 0.9},
        {'source': 0, 'target': 3, 'score': 0.5},
        {'source': 1, 'target': 2, 'score': 0.5},
        {'source': 2, 'target': 4, 'score': 0.7},
        {'source': 3, 'target': 5, 'score': 0.7},
        {'source': 2, 'target': 5, 'score': 0.3},
        {'source': 3, 'target': 4, 'score': 0.3},
        {'source': 3, 'target': 6, 'score': 0.8}
    ]

    graph = nx.DiGraph()
    graph.add_nodes_from([
        (cell['id'], cell)
        for cell in cells
    ])
    graph.add_edges_from([
        (edge['source'], edge['target'], edge)
        for edge in edges
    ])

    graph = motile.TrackGraph(graph)

.. jupyter-execute::

  import motile
  from motile.plot import draw_track_graph, draw_solution

  draw_track_graph(graph, alpha_attribute='score', label_attribute='score')

The numbers in nodes show how likely it is that a node represents a true object
(versus being a false positive). Similarly, for edges the number shows how
likely the incident nodes represent the same object across time.

We want to find tracks in this graph that globally maximize the overall score,
subject to certain constraints.

We will start with a very simple case:

1. nodes and edges should be selected based on their ``score``
2. objects are not supposed to split or merge
3. there should be a small penalty for starting a new track

``motile`` comes with costs and constraints that allow us to do exactly that.

Adding Costs for Nodes and Edges
--------------------------------

First, we have to create a :class:`Solver` for our track graph:

.. jupyter-execute::

  import motile

  # create a motile solver
  solver = motile.Solver(graph)

Once a solver is created, we can add costs and constraints to it. We start with
the most basic ones: the costs for selecting a node or an edge. Both nodes and
edges in our example graph have an attribute ``score``, which indicates how
likely the node or edge is a true positive and should therefore be selected. A
higher score is better.

``motile``, however, expects us to give a "cost" for selecting nodes and edges.
It will then minimize those costs to find the globally optimal solution. Here,
lower is better. Therefore, we need to invert the scores, which we can easily
do by giving them a negative weight. We can do this by instantiating the
classes :class:`costs.NodeSelection` and
:class:`costs.EdgeSelection`:

.. jupyter-execute::

  from motile.costs import NodeSelection, EdgeSelection

  solver.add_costs(
      NodeSelection(
          weight=-1.0,
          attribute='score'))
  solver.add_costs(
      EdgeSelection(
          weight=-1.0,
          attribute='score'))

After solving the optimization problem...

.. jupyter-execute::
  :hide-output:

  solution = solver.solve()

...we are ready to inspect the solution. For that, we make use of ``motile``'s
variables. Specifically, we are interested in the assignments of the node and
edge selection variables:

.. jupyter-execute::

  from motile.variables import NodeSelected, EdgeSelected

  node_selected = solver.get_variables(NodeSelected)
  edge_selected = solver.get_variables(EdgeSelected)

  for node in graph.nodes:
    if solution[node_selected[node]] > 0.5:
      print(f"Node {node} has been selected")
  for u, v in graph.edges:
    if solution[edge_selected[(u, v)]] > 0.5:
      print(f"Edge {(u, v)} has been selected")

Variables are instantiated and managed by the solver. All we have to do is to
ask the solver for the kind of variables we are interested in via
:func:`Solver.get_variables`. The returned value (e.g., ``node_selected``) is a
dictionary that maps *what* to *where*: in the case of node variables, the
dictionary keys are the nodes themselves (an integer) and the dictionay values
are the indices in the ``solution`` vector where we can find the value of the
variable. Both node and edge indicators are binary variables (one if selected,
zero otherwise).

Here is our graph again, showing all the selected nodes and edges:

.. jupyter-execute::
  :hide-code:

  draw_solution(graph, solver, label_attribute='score')

All nodes and edges have been selected! This is indeed what we asked for, but
not what we want. Time to add some constraints.

Adding Constraints
------------------

With negative costs, the solver is incentivised to pick every node and edge,
which is not what we want. We will add two constraints to the solver,
:class:`constraints.MaxParents` and :class:`constraints.MaxChildren`, to make
sure that tracks don't merge or split:

.. jupyter-execute::

  from motile.constraints import MaxParents, MaxChildren

  solver.add_constraints(MaxParents(1))
  solver.add_constraints(MaxChildren(1))

If we solve again, the solution does now look like this:

.. jupyter-execute::
  :hide-output:

  solution = solver.solve()

.. jupyter-execute::
  :hide-code:

  draw_solution(graph, solver, label_attribute='score')

Nodes do now indeed have at most one parent (to the previous time frame) and at
most on child (to the next time frame). There are multiple possible solutions
that satisfy those constraints and the solver picked the one that has the least
total costs.

This is starting to look good, but we note that a single node was selected in
the last timeframe, without any link to the past or future. This is in fact a
track consisting of just one node. To avoid those short tracks, we can add a
constant cost for the appearance of a track: only tracks that are long enough
to offset this cost will then be selected.

Adding Costs for Starting a Track
---------------------------------

``motile`` provides :class:`costs.Appear`, which we can add to our solver to
discourage selection of short tracks. We add them similarly to how we added the
node and edge selection costs:

.. jupyter-execute::

  from motile.costs import Appear

  solver.add_costs(Appear(constant=1.0))

And if we solve the tracking problem again with those costs...

.. jupyter-execute::
  :hide-output:

  solution = solver.solve()

...we see that the orphan node is gone now. Its (negative) cost is not enough
to justify starting a new track:

.. jupyter-execute::
  :hide-code:

  draw_solution(graph, solver, label_attribute='score')

:jupyter-download-notebook:`Download this page as a Jupyter notebook<quickstart>`
