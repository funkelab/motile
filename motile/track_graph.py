from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, DefaultDict, Hashable

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from networkx.classes import DiGraph

    from motile._types import EdgeId, NodeId


class TrackGraph:
    """A :class:`networkx.DiGraph` of objects with positions in time and space,
    and inter-frame edges between them.

    Provides a few convenience methods for time series graphs in addition to
    all the methods inherited from :class:`networkx.DiGraph`.

    Args:

        graph (:class:`networkx.DiGraph`):

            Optional graph data to pass to the :class:`networkx.DiGraph`
            constructor as ``incoming_graph_data``. This can be used to
            populate a track graph with entries from a generic
            ``networkx`` graph. If None (default) an empty
            graph is created.  The data can be an edge list, or any
            NetworkX graph object.  If the corresponding optional Python
            packages are installed the data can also be a 2D NumPy array, a
            SciPy sparse array, or a PyGraphviz graph.

        frame_attribute (``string``, optional):

            The name of the node attribute that corresponds to the frame (i.e.,
            the time dimension) of the object. Defaults to ``'t'``.

        is_bipartite (``bool``, optional):

            Whether the graph is bipartite. If True, the graph is assumed to
            be bipartite, and the edges are assumed to be assignment nodes
            (i.e., nodes with no frame attribute). Defaults to False.

    Attributes:

        nodes (``dict``):

            A dictionary of nodes in the graph, keyed by node ID. Each node
            is a dictionary of attributes.

        edges (``dict``):

            A dictionary of edges in the graph, keyed by edge ID. Each edge
            is a dictionary of attributes.

        prev_edges (``dict``):

            A dictionary of edges in the graph, keyed by node ID. Each node
            is a list of edges that have the node as their target.

        next_edges (``dict``):

            A dictionary of edges in the graph, keyed by node ID. Each node
            is a list of edges that have the node as their source.

    """

    edges: dict[EdgeId, dict[str, Any]]
    nodes: dict[NodeId, dict[str, Any]]
    prev_edges: DefaultDict[NodeId, list[EdgeId]]
    next_edges: DefaultDict[NodeId, list[EdgeId]]

    def __init__(
        self,
        graph: DiGraph,
        frame_attribute: str = "t",
        is_bipartite: bool = False,
    ):
        self.frame_attribute = frame_attribute
        self.is_bipartite = is_bipartite
        self._graph_changed = True

        self.nx_graph = graph

        self.nodes = {
            node_id: node
            for node_id, node in graph.nodes.values()
            if frame_attribute in node
        }

        self.prev_edges = DefaultDict(list)
        self.next_edges = DefaultDict(list)

        if is_bipartite:
            self.edges = {
                self._assignment_node_to_edge_tuple(graph, node_id): assignment_node
                for node_id, assignment_node in graph.nodes.values()
                if frame_attribute not in assignment_node
            }
        else:
            self.edges = graph.edges
            for u, v in graph.edges:
                self.prev_edges[v].append((u, v))
                self.next_edges[u].append((u, v))

        self._update_metadata()

    def _assignment_node_to_edge_tuple(
        self, graph: DiGraph, assignment_node: Hashable
    ) -> tuple[tuple[Any, ...], ...]:
        in_nodes = graph.predecessors(assignment_node)
        out_nodes = graph.successors(assignment_node)
        nodes = in_nodes + out_nodes

        frames = sorted(node[self.frame_attribute] for node in nodes)

        edge_tuple = tuple(
            tuple(node for node in nodes if node[self.frame_attribute] == frame)
            for frame in frames
        )

        for in_node in in_nodes:
            self.next_edges[in_nodes].append(edge_tuple)
        for out_node in out_nodes:
            self.prev_edges[out_nodes].append(edge_tuple)

        return edge_tuple

    def get_frames(self) -> tuple[int | None, int | None]:
        """Get a tuple ``(t_begin, t_end)`` of the first and last frame
        (exclusive) this track graph has nodes for."""

        self._update_metadata()

        return (self.t_begin, self.t_end)

    def nodes_by_frame(self, t: int) -> list[Hashable]:
        """Get all nodes in frame ``t``."""

        self._update_metadata()

        if t not in self._nodes_by_frame:
            return []
        return self._nodes_by_frame[t]

    def _update_metadata(self) -> None:
        if not self._graph_changed:
            return

        self._graph_changed = False
        self._nodes_by_frame: dict[int, list[Hashable]] = {}

        if not self.nodes:
            self._nodes_by_frame = {}
            self.t_begin = None
            self.t_end = None
            return

        self._nodes_by_frame = {}
        for node, data in self.nodes.items():
            t = data[self.frame_attribute]
            if t not in self._nodes_by_frame:
                self._nodes_by_frame[t] = []
            self._nodes_by_frame[t].append(node)

        frames = self._nodes_by_frame.keys()
        self.t_begin = min(frames)
        self.t_end = max(frames) + 1
        # ensure edges point forwards in time
        if not self.is_bipartite:
            for u, v in self.edges:
                t_u = self.nodes[u][self.frame_attribute]
                t_v = self.nodes[v][self.frame_attribute]
                assert t_u < t_v, (
                    f"Edge ({u}, {v}) does not point forwards in time, but "
                    f"from frame {t_u} to {t_v}"
                )

        self._graph_changed = False
