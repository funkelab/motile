from __future__ import annotations

from typing import Any, Mapping, TypeAlias

# Nodes are integers
Node: TypeAlias = int

# Edges are tuples of two nodes.
# (0, 1) is an edge from node 0 to node 1.
Edge: TypeAlias = tuple[Node, Node]

# objects in the graph are represented as dicts
# eg. { "id": 1, "x": 0.5, "y": 0.5, "t": 0 }
Attributes: TypeAlias = Mapping[str, Any]
