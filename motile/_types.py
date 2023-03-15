from __future__ import annotations

from typing import TypeAlias

# Nodes are represented as integers, or a "meta-node" tuple of integers.
NodeId: TypeAlias = "int | tuple[int, ...]"

# Edges are represented as tuples of NodeId.
# (0, 1) is an edge from node 0 to node 1.
# ((0, 1), 2) is a hyperedge from nodes 0 and 1 to node 2 (i.e. a merge).
# ((0,), (1, 2)) is a hyperedge from node 0 to nodes 1 and 2 (i.e. a split).
EdgeId: TypeAlias = tuple[NodeId, ...]
