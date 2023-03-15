from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Hashable

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from networkx.classes import DiGraph

EdgeTuple = "tuple[int|tuple[int,...],...]"


class TrackGraph:
    """A :class:`networkx.DiGraph` of objects with positions in time and space,
    and inter-frame edges between them.

    Provides a few convenience methods for time series graphs in addition to
    all the methods inherited from :class:`networkx.DiGraph`.

    Args:

        graph (:class:`networkx.DiGraph`):

            Optional graph data to pass to the :class:`networkx.DiGraph`
            constructor as ``graph_data``. This can be used to
            populate a track graph with entries from a generic
            ``networkx`` graph. If None (default) an empty
            graph is created.  The data can be an edge list, or any
            NetworkX graph object.  If the corresponding optional Python
            packages are installed the data can also be a 2D NumPy array, a
            SciPy sparse array, or a PyGraphviz graph.

        frame_attribute (``string``, optional):

            The name of the node attribute that corresponds to the frame (i.e.,
            the time dimension) of the object. Defaults to ``'t'``.

        has_hyperedges (``boolean``, optional):

            Indicates if the given ``graph_data`` contains nodes that indicate
            hyper edges. In the given ``networkx`` graph a hyperedge is represented
            by a node that does not have the ``frame_attribute`` and is itself
            connected to all nodes that should form a hyper edge.
    """

    def __init__(
        self,
        nx_graph: DiGraph = None,
        frame_attribute: str = "t",
    ):
        self.frame_attribute = frame_attribute
        self._graph_changed = True

        self.nodes: dict[Hashable, dict[Hashable, Any]] = {}
        self.edges: dict[EdgeTuple, dict[Hashable, Any]] = {}
        self.prev_edges: dict[Hashable, list[Hashable]] = {}
        self.next_edges: dict[Hashable, list[Hashable]] = {}

        if nx_graph:
            self.add_from_nx_graph(nx_graph)

        self._update_metadata()

    def add_node(self, node_id: Hashable, data: dict[Hashable, Any]):
        self.nodes[node_id] = data

    def add_edge(self, edge_tuple: EdgeTuple, data: dict[Hashable, Any]):
        self.edges[edge_tuple] = data

    def add_from_nx_graph(self, nx_graph):
        self.nodes = {
            node: nx_graph.nodes[node]
            for node in nx_graph.nodes
            if self.frame_attribute in nx_graph.nodes[node]
        }

        self.prev_edges: dict[Hashable, list[Hashable]] = {
            node: [] for node in self.nodes
        }
        self.next_edges: dict[Hashable, list[Hashable]] = {
            node: [] for node in self.nodes
        }

        for (u, v), data in nx_graph.edges.items():
            # do nothing when you have an nx_edge leaving a hyperedge node
            if self._is_hyperedge_nx_node(nx_graph, u):
                continue
            # add hyperedge when nx_edge leads to hyperedge node
            if self._is_hyperedge_nx_node(nx_graph, v):
                (
                    edge,
                    in_nodes,
                    out_nodes,
                ) = self._hyperedge_nx_node_to_edge_tuple_and_neighbors(nx_graph, v)
                if (
                    edge not in self.edges
                ):  # avoid adding hyperedges having multiple source nodes
                    self.edges[edge] = data
                    for in_node in in_nodes:
                        self.next_edges[in_node].append(edge)
                    for out_node in out_nodes:
                        self.prev_edges[out_node].append(edge)
            else:  # add a regular edge otherwise
                self.edges[(u, v)] = data
                self.prev_edges[v].append((u, v))
                self.next_edges[u].append((u, v))

    def _is_hyperedge_nx_node(self, nx_graph: Any, nx_node: Any) -> bool:
        return self.frame_attribute not in nx_graph.nodes[nx_node]

    def _hyperedge_nx_node_to_edge_tuple_and_neighbors(
        self, nx_graph: DiGraph, hyperedge_node: Any
    ) -> tuple[Hashable, ...]:
        assert self._is_hyperedge_nx_node(nx_graph, hyperedge_node)

        in_nodes = list(nx_graph.predecessors(hyperedge_node))
        out_nodes = list(nx_graph.successors(hyperedge_node))
        nx_nodes = in_nodes + out_nodes

        frameset = set(
            nx_graph.nodes[nx_node][self.frame_attribute] for nx_node in nx_nodes
        )
        frames = list(sorted(frameset))

        edge_tuple = tuple(
            tuple(
                node
                for node in nx_nodes
                if nx_graph.nodes[node][self.frame_attribute] == frame
            )
            for frame in frames
        )

        return edge_tuple, in_nodes, out_nodes

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

        self._graph_changed = False
