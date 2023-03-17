from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, DefaultDict, Hashable, Iterator

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from networkx.classes import DiGraph

    from motile._types import EdgeId, GraphObject, NodeId


class TrackGraph:
    """A :class:`networkx.DiGraph` of objects with positions in time and space,
    and inter-frame edges between them.

    Provides a few convenience methods for time series graphs in addition to
    all the methods inherited from :class:`networkx.DiGraph`.

    Args:

        nx_graph (``DiGraph``, optional):

            A directed networkx graph representing the TrackGraph to be created.
            Hyperedges are represented by networkx nodes that do not have the
            ``frame_attribute`` and are connected to nodes that do have this
            attribute.

        frame_attribute (``string``, optional):

            The name of the node attribute that corresponds to the frame (i.e.,
            the time dimension) of the object. Defaults to ``'t'``.
    """

    def __init__(
        self,
        nx_graph: DiGraph = None,
        frame_attribute: str = "t",
    ):
        self.frame_attribute = frame_attribute
        self._graph_changed = True

        self.nodes: dict[NodeId, GraphObject] = {}
        self.edges: dict[EdgeId, GraphObject] = {}
        self.prev_edges: DefaultDict[NodeId, list[EdgeId]] = DefaultDict(list)
        self.next_edges: DefaultDict[NodeId, list[EdgeId]] = DefaultDict(list)

        if nx_graph:
            self.add_from_nx_graph(nx_graph)

        self._update_metadata()

    def add_node(self, node_id: NodeId, data: GraphObject) -> None:
        """Adds a new node to this TrackGraph.

        Args:
            node_id (Hashable): the node to be added.
            data (GraphObject): all properties associated to the added node.
        """
        self.nodes[node_id] = data

    def add_edge(self, edge_tuple: EdgeId, data: GraphObject) -> None:
        """Adds an edge to this TrackGraph.

        Args:
            edge_tuple (EdgeId): an ``EdgeId`` defining the edge (or hyperedge)
                to be added.
            data (GraphObject): all properties associated to the added edge.
        """
        self.edges[edge_tuple] = data

    def add_from_nx_graph(self, nx_graph: DiGraph) -> None:
        """Adds the TrackGraph represented by the given ``nx_graph`` to the
        existing TrackGraph.

        Hyperedges are represented by nodes in the ``nx_graph`` that do not have the
        ``frame_attribute`` property. All 'regular' nodes connected to such a hyperedge
        node will be added as a hyperedge.

        Args:
            nx_graph (_type_):

                A directed networkx graph representing a TrackGraph to be added.
                Hyperedges are represented by networkx nodes that do not have the
                ``frame_attribute`` and are connected to nodes that do have this
                attribute.
                Duplicate nodes and edges will not be added again but new attributes
                associated to nodes and edges added. If attributes of existing nodes
                or edges do already exist, the values set in the given ``nx_graph``
                will be updating the previously set values.
        """
        # add all regular nodes (all but ones representing hyperedges)
        for node, data in nx_graph.nodes.items():
            if self.frame_attribute in data:
                if node not in self.nodes:
                    self.nodes[node] = data
                else:
                    self.nodes[node] |= data

        # add all edges and hyperedges
        for (u, v), data in nx_graph.edges.items():
            # do nothing when you have an nx_edge leaving a hyperedge node
            # (we will add thi hyperedge when we encounter it via an incoming edge)
            if self._is_hyperedge_nx_node(nx_graph, u):
                continue
            # add hyperedge when nx_edge leads to hyperedge node
            if self._is_hyperedge_nx_node(nx_graph, v):
                (
                    edge,
                    in_nodes,
                    out_nodes,
                ) = self._hyperedge_nx_node_to_edge_tuple_and_neighbors(nx_graph, v)
                # avoid adding duplicates
                if edge not in self.edges:
                    self.edges[edge] = data
                    for in_node in in_nodes:
                        self.next_edges[in_node].append(edge)
                    for out_node in out_nodes:
                        self.prev_edges[out_node].append(edge)
                else:  # but merge in potentially new or updated attributes
                    self.edges[edge] |= data
            else:  # add a regular edge otherwise
                self.edges[(u, v)] = data
                self.prev_edges[v].append((u, v))
                self.next_edges[u].append((u, v))

    def nodes_of(self, edge: int | tuple[int, ...]) -> Iterator[int]:
        """Returns an ``Iterator`` of node id's that are incident to the given edge.

        Args:
            edge (int | tuple[int, ...]): an edge of this TrackGraph.

        Yields:
            Iterator[int]: all nodes incident to the given edge.
        """
        if isinstance(edge, tuple):
            for x in edge:
                yield from self.nodes_of(x)
        else:
            yield edge

    def _is_hyperedge_nx_node(self, nx_graph: DiGraph, nx_node: Any) -> bool:
        """Checks if the given networkx node in the given directed networkx graph
        represents an hyperedge. This boils down to checking if the node does not
        have the ``frame_attribute`` set.

        Args:
            nx_graph (DiGraph): a networkx ``DiGraph``.
            nx_node (Any): a node in the given ``nx_graph``.

        Returns:
            bool: true iff the given ``nx_node`` does not posses the ``frame_attribute``.
        """
        return self.frame_attribute not in nx_graph.nodes[nx_node]

    def _hyperedge_nx_node_to_edge_tuple_and_neighbors(
        self, nx_graph: DiGraph, hyperedge_node: Any
    ) -> tuple[tuple[NodeId, ...], list[NodeId], list[NodeId]]:
        """Creates a hyperedge tuple for hyperedge node in a given networkx ``DiGraph``.

        Args:
            nx_graph (DiGraph): a networkx ``DiGraph``.
            hyperedge_node (Any): a node in the given ``nx_graph`` that represents
                a hyperedge.

        Returns:
            tuple[Hashable, ...]: a tuple representing the hyperedge the given
                ``nx_node`` represented. (It will be a tuple with one entry per
                involved time point, listing all nodes at that time point.)
        """
        assert self._is_hyperedge_nx_node(nx_graph, hyperedge_node)

        in_nodes = list(nx_graph.predecessors(hyperedge_node))
        out_nodes = list(nx_graph.successors(hyperedge_node))
        nx_nodes = in_nodes + out_nodes

        frameset = {
            nx_graph.nodes[nx_node][self.frame_attribute] for nx_node in nx_nodes
        }
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
