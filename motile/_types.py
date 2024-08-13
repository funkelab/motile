from __future__ import annotations

from typing import Any, Mapping, TypeAlias, Union

# Nodes are integers
Node: TypeAlias = int
# Collections of nodes (for hyperedges) are tuples
Nodes: TypeAlias = tuple[int, ...]

# Edges are tuples of Node or Nodes.
# (0, 1) is an edge from node 0 to node 1.
# ((0,), (1, 2)) is a hyperedge from node 0 to nodes 1 and 2 (i.e. a split).
# ((0, 1), 2) is not valid.
Edge: TypeAlias = tuple[Node, Node]
HyperEdge: TypeAlias = tuple[Nodes, Nodes]
GenericEdge: TypeAlias = Union[Edge, HyperEdge]

# objects in the graph are represented as dicts
# eg. { "id": 1, "x": 0.5, "y": 0.5, "t": 0 }
Attributes: TypeAlias = Mapping[str, Any]
