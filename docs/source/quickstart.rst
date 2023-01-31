.. _sec_quickstart:

Quickstart
==========

.. admonition:: (click here to see the plotting code we use in this tutorial)
  :class: hint, dropdown

  .. jupyter-execute::

    import matplotlib.pyplot as plt
    import motile
    import networkx as  nx

    def draw_track_graph(graph, solver=None):

      num_nodes = graph.number_of_nodes()
      frames = list(range(*graph.get_frames()))

      positions = {
        node: (data['t'], data['x'])
        for node, data in graph.nodes(data=True)
      }

      colors = ['purple'] * num_nodes

      if solver is not None:

        node_indicators = solver.get_variables(NodeSelected)
        edge_indicators = solver.get_variables(EdgeSelected)

        for node, index in node_indicators.items():
          graph.nodes[node]['selected'] = solver.solution[index] > 0.5
        for edge, index in edge_indicators.items():
          graph.edges[edge]['selected'] = solver.solution[index] > 0.5

      alpha_attribute = 'score' if solver is None else 'selected'
      node_alphas = [
        data[alpha_attribute]
        for _, data in graph.nodes(data=True)
      ]
      edge_alphas = [
        data[alpha_attribute]
        for _, _, data in graph.edges(data=True)
      ]

      node_labels = {
        node: data['score']
        for node, data in graph.nodes(data=True)
      }
      edge_labels = {
        (u, v): data['score']
        for u, v, data in graph.edges(data=True)
      }

      fig = plt.figure()
      fig.set_figheight(6)
      fig.set_figwidth(12)

      nx.draw_networkx_nodes(
        graph,
        positions,
        alpha=node_alphas,
        node_size=600,
        linewidths=2.0,
        node_color=colors)
      if solver is None:
        nx.draw_networkx_labels(
          graph,
          positions,
          node_labels)
      nx.draw_networkx_edges(
        graph,
        positions,
        alpha=edge_alphas,
        width=3.0,
        arrowsize=20,
        node_size=600,
        min_source_margin=20,
        min_target_margin=20,
        edge_color='purple')
      if solver is None:
        nx.draw_networkx_edge_labels(
          graph,
          positions,
          edge_labels,
          label_pos=0.3)

      plt.xlabel("time")
      plt.ylabel("space")
      plt.grid(True)
      plt.xticks(frames, frames)

      plt.show()

.. jupyter-execute::
  :hide-code:

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

  graph = motile.TrackGraph()
  graph.add_nodes_from([
      (cell['id'], cell)
      for cell in cells
  ])
  graph.add_edges_from([
      (edge['source'], edge['target'], edge)
      for edge in edges
  ])

.. jupyter-execute::
  :hide-code:

  draw_track_graph(graph)
