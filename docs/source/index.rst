.. motile documentation master file

What is ``motile`` ?
====================

``motile`` tracks multiple objects over time, given a graph of candidate
objects (nodes) and possible ways they could be linked over time frames
(edges).

It does so by solving a global optimization problem. The objective function and
constraints on the solution are highly customizable: ``motile`` provides common
costs and constraints, and custom extensions can easily be added.

Show me an example!
-------------------

Consider the following example track ``graph``, where each node is a potential
object and each edge a potential link of objects between frames:

.. jupyter-execute::
  :hide-code:

  import motile
  from motile.variables import NodeSelected, EdgeSelected
  from motile_toolbox.visualization import draw_track_graph, draw_solution


.. jupyter-execute::
  :hide-code:

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
  :hide-code:

  draw_track_graph(
      graph,
      alpha_attribute='score',
      label_attribute='score',
  )

The numbers in nodes show how likely it is that a node represents a true object
(versus being a false positive). Similarly, for edges the number shows how
likely the incident nodes represent the same object across time.

We want to find tracks in this graph that globally maximize the overall score,
subject to certain constraints. This can be done with ``motile`` as follows:

.. jupyter-execute::
  :hide-output:

  from motile.constraints import MaxParents, MaxChildren
  from motile.costs import NodeSelection, EdgeSelection, Appear

  # create a motile solver
  solver = motile.Solver(graph)

  # tell it how to compute costs for selecting nodes and edges
  solver.add_cost(
      NodeSelection(
          weight=-1.0,
          attribute='score'))
  solver.add_cost(
      EdgeSelection(
          weight=-1.0,
          attribute='score'))

  # add a small penalty to start a new track
  solver.add_cost(Appear(constant=1.0))

  # add constraints on the solution (no splits, no merges)
  solver.add_constraint(MaxParents(1))
  solver.add_constraint(MaxChildren(1))

  # solve
  solution = solver.solve()

Inspecting the solution will reveal that the following nodes and edges were
selected:

.. jupyter-execute::
  :hide-code:

  draw_solution(graph, solver, label_attribute='score')

This is just a simple example of what can be done with ``motile``. See the
:ref:`sec_quickstart` for a quick tour of what can be done with it, and the
:ref:`sec_api` for a full list of costs, constraints, and variables that are
shipped with ``motile``.

``motile`` can also be extended to fit your own needs. See :ref:`sec_extending`
for a tutorial on how to write your own variable, constraints, and costs.

Why is it called ``motile``?
----------------------------

``motile`` stands for **M**\ ulti **O**\ bject **T**\ racking with **I**\ nteger
**L**\ inear **E**\ quations (which is precisely what ``motile`` does). "motile"
also means having the ability to move, which is neat.

Full Documentation:
===================

.. toctree::
  :maxdepth: 2

  install
  quickstart
  extending
  learning
  api
