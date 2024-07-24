from __future__ import annotations

from typing import Any, Mapping, TypeAlias, Union

# Nodes are integers
NodeId: TypeAlias = int
# Collections of nodes (for hyperedges) are tuples
NodeIds: TypeAlias = tuple[int, ...]

# Edges are tuples of NodeId or NodeIds.
# (0, 1) is an edge from node 0 to node 1.
# ((0,), (1, 2)) is a hyperedge from node 0 to nodes 1 and 2 (i.e. a split).
# ((0, 1), 2) is not valid.
EdgeId: TypeAlias = tuple[NodeId, NodeId]
HyperEdgeId: TypeAlias = tuple[NodeIds, NodeIds]
GenericEdgeId: TypeAlias = Union[EdgeId, HyperEdgeId]

# objects in the graph are represented as dicts
# eg. { "id": 1, "x": 0.5, "y": 0.5, "t": 0 }
GraphObject: TypeAlias = Mapping[str, Any]
