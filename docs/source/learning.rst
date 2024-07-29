.. _sec_learning:

Learning of Cost Weights
========================

.. admonition:: written by Benjamin Gallusser, edited by Jan Funke
  :class: hint

  :jupyter-download-notebook:`Download this page as a Jupyter notebook<learning>`

.. automodule:: motile
   :noindex:

``motile`` supports learning of cost weights, given (sparse) ground-truth
annotations on the track graph. This tutorial will show you:

1. What those weights are and how to modify them by hand.

2. How to annotate nodes and edges as being part of the ground-truth.

3. How to learn optimal weights for the costs for a given annotated track
   graph.

Cost Weights
------------

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
            {"id": 5, "t": 2, "x": 24, "score": 0.3},
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

For this tutorial, we will use a simple model: The costs for selecting nodes
and edges should depend on their ``score`` attribute, and the start of a track
should have a positive cost as well. Furthermore, we are only interested in
single-object tracks, i.e., tracks don't merge or split. The solver for this
model is:

.. jupyter-execute::

  from motile.constraints import MaxParents, MaxChildren
  from motile.costs import NodeSelection, EdgeSelection, Appear

  solver = motile.Solver(graph)

  solver.add_constraint(MaxParents(1))
  solver.add_constraint(MaxChildren(1))

  solver.add_cost(NodeSelection(weight=1, attribute="score"))
  solver.add_cost(EdgeSelection(weight=-2, attribute="score", constant=1))
  solver.add_cost(Appear(constant=1))

Each of those costs is calculated as the product of `weights` and `features`:

:class:`motile.costs.NodeSelection` and :class:`motile.costs.EdgeSelection`
each have a weight (given as argument ``weight``) by which to scale a node or
edge feature (given by argument ``attribute``). Both cost terms also support a
constant cost (given by argument ``constant``), which is in fact also a weight
on an implicit "feature" with value 1.0.

More generally, the cost :math:`c_y` of a variable :math:`y` is

.. math::

  \def\vct#1{\mathbf{#1}}
  c_y = \vct{w}^\intercal\vct{f}_y
  \text{.}

The variable :math:`y` can be an indicator for the selection of a node, the
selection of an edge, a node that starts a track, or any other variable added
to the solver.

In the example above, the :class:`motile.variables.EdgeSelected` variable
(which is the target of the cost :class:`motile.costs.EdgeSelection`), has the
following weights and features:

.. math::
  \vct{w}
    = \begin{pmatrix} w_\text{attr} \\ w_\text{const} \end{pmatrix}
    = \begin{pmatrix} -2 \\ 1 \end{pmatrix}
  \;\;\;
  \text{and}
  \;\;\;
  \vct{f}_e
    = \begin{pmatrix}\text{attr} \\ 1.0 \end{pmatrix}
  \text{,}

where :math:`\text{attr}` is the value of the attribute ``score`` of edge :math:`e`.

The ``motile`` solver knows about all the weights that have been introduced through cost functions:

.. jupyter-execute::

  solver.weights

Our initial weights are just a guess, let's solve...

.. jupyter-execute::
  :hide-output:

  from motile.variables import NodeSelected, EdgeSelected
  from motile_toolbox.visualization import draw_solution

  solver.solve()

...and inspect the solution:

.. jupyter-execute::

  print(solver.get_variables(NodeSelected))
  print(solver.get_variables(EdgeSelected))

  draw_solution(graph, solver, label_attribute="score")

None of the nodes or edges were selected, which is indeed the cost minimal
solution: the cost for selecting nodes or edges is too high.

We can use the ``solver.weights`` object to directly modify the weights on the
costs. Here, we further lower the cost of edges for example:

.. jupyter-execute::
  :hide-output:

  solver.weights[("EdgeSelection", "weight")] = -3
  solver.weights[("Appear", "constant")] = 0.5

  solution = solver.solve()

.. jupyter-execute::

  print(solver.weights)
  print(solver.get_variables(NodeSelected))
  print(solver.get_variables(EdgeSelected))

  draw_solution(graph, solver, label_attribute="score")

Annotate Ground-Truth
---------------------

Ground-truth nodes and edges are annotated by giving them a boolean attribute:
``True`` for nodes/edges that should be selected, ``False`` for nodes/edges
that should not be selected, and ``None`` (or simply no attribute) for
nodes/edges for which it is unknown. The name of the attribute can be freely chosen.

We can do this directly on the track graph. We will add a new attribute ``gt``:

.. jupyter-execute::

  graph.nodes[0]["gt"] = True
  graph.nodes[2]["gt"] = True
  graph.nodes[4]["gt"] = True
  graph.nodes[5]["gt"] = False

  graph.edges[(0, 2)]["gt"] = True
  graph.edges[(2, 4)]["gt"] = True
  graph.edges[(2, 5)]["gt"] = False

The following shows which nodes and edges are part of the ground-truth (green:
should be selected, orange: should not be selected):

.. jupyter-execute::

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
    alpha_func=(
      lambda x: "gt" in graph.nodes[x],
      lambda x: "gt" in graph.edges[x]),
    node_color=node_colors,
    edge_color=edge_colors)

Learn Weights
-------------

Learning the weights is done by calling :func:`motile.Solver.fit_weights` on the
ground-truth attribute ``gt`` that we just added:

.. jupyter-execute::
  :hide-code:

  # this suppresses logging output from structsvm that can fail the docs build
  import logging
  logging.getLogger("structsvm.bundle_method").setLevel(logging.CRITICAL)

.. jupyter-execute::
  :hide-output:

  solver.fit_weights(gt_attribute="gt", regularizer_weight=0.01)
  optimal_weights = solver.weights

.. jupyter-execute::

  optimal_weights

To see whether those weights are any good, we will solve again...

.. jupyter-execute::
  :hide-output:

  solver = motile.Solver(graph)

  solver.add_constraint(MaxParents(1))
  solver.add_constraint(MaxChildren(1))

  solver.add_cost(NodeSelection(weight=1, attribute="score"))
  solver.add_cost(EdgeSelection(weight=-2, attribute="score", constant=1))
  solver.add_cost(Appear(constant=1))

  solver.weights.from_ndarray(optimal_weights.to_ndarray())

  solver.solve()

...and look at the solution:

.. jupyter-execute::

  draw_solution(graph, solver, label_attribute="score")

Indeed, the solution from the learnt weights agrees with the ground-truth where
given. Note that this is, in general, not the case: for larger graphs and more
noisy features than what we use here as a toy example, there might simply be no
set of weights that exactly reproduces the ground-truth. In those cases, the
learning will at least try to find weights that result in a solution that is
`as close as possible` to the ground-truth.
