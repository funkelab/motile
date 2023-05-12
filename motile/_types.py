from __future__ import annotations

from typing import Any, Mapping, TypeAlias, Union

# Nodes are represented as integers, or a "meta-node" tuple of integers.
NodeId: TypeAlias = Union[int, tuple[int, ...]]

# objects in the graph are represented as dicts
# eg. { "id": 1, "x": 0.5, "y": 0.5, "t": 0 }
GraphObject: TypeAlias = Mapping[str, Any]

# Edges are represented as tuples of NodeId.
# (0, 1) is an edge from node 0 to node 1.
# ((0, 1), 2) is a hyperedge from nodes 0 and 1 to node 2 (i.e. a merge).
# ((0,), (1, 2)) is a hyperedge from node 0 to nodes 1 and 2 (i.e. a split).
EdgeId: TypeAlias = tuple[NodeId, ...]
