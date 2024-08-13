from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, DefaultDict, Hashable, Iterator, cast

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import networkx
    from typing_extensions import TypeGuard

    from motile._types import (
        Attributes,
        Edge,
        GenericEdge,
        HyperEdge,
        Node,
        Nodes,
    )


class TrackGraph:
    """A graph of nodes in time & space, with edges connecting them across time.

    This wraps a :class:`networkx.DiGraph` object.

    Both ``nodes`` and ``edges`` are represented by a dictionary of properties.

    Provides a few convenience methods for time series graphs in addition to
    all the methods inherited from :class:`networkx.DiGraph`.

    Args:
        nx_graph:

            A directed networkx graph representing the TrackGraph to be created.
            Hyperedges are represented by networkx nodes that do not have the
            ``frame_attribute`` and are connected to nodes that do have this
            attribute.

        frame_attribute:

            The name of the node attribute that corresponds to the frame (i.e.,
            the time dimension) of the object. Defaults to ``'t'``.
    """

    def __init__(
        self,
        nx_graph: networkx.DiGraph | None = None,
        frame_attribute: str = "t",
    ):
        self.frame_attribute = frame_attribute
        self._graph_changed = True

        self.nodes: dict[Node, Attributes] = {}
        self.edges: dict[GenericEdge, Attributes] = {}
        self.prev_edges: defaultdict[Node, list[GenericEdge]] = DefaultDict(list)
        self.next_edges: defaultdict[Node, list[GenericEdge]] = DefaultDict(list)

        if nx_graph:
            self.add_from_nx_graph(nx_graph)

        self._update_metadata()

    def add_node(self, node_id: Node, data: Attributes) -> None:
        """Adds a new node to this TrackGraph.

        Args:
            node_id: the node to be added.
            data: all properties associated to the added node.
        """
        assert self.frame_attribute in data, (
            "Nodes in the track graph need to have (at least) a frame "
            f"attribute {self.frame_attribute}"
        )
        self.nodes[node_id] = data
        self._graph_changed = True

    def add_edge(self, edge_id: GenericEdge, data: Attributes) -> None:
        """Adds an edge to this TrackGraph.

        Args:
            edge_id: an ``GenericEdge`` (tuple of Nodes) defining the edge
                (or hyperedge) to be added.
            data: all properties associated to the added edge.
        """
        self.edges[edge_id] = data

        if self.is_hyperedge(edge_id):
            us, vs = edge_id
            for v in vs:
                self.prev_edges[v].append(edge_id)
            for u in us:
                self.next_edges[v].append(edge_id)
        else:
            # normal (u, v) edge
            u, v = cast("Edge", edge_id)
            self.prev_edges[v].append(edge_id)
            self.next_edges[u].append(edge_id)

        self._graph_changed = True

    def add_from_nx_graph(self, nx_graph: networkx.DiGraph) -> None:
        """Add nodes/edges from ``nx_graph`` to this TrackGraph.

        Hyperedges are represented by nodes in the ``nx_graph`` that do not have the
        ``frame_attribute`` property. All 'regular' nodes connected to such a hyperedge
        node will be added as a hyperedge.

        Args:
            nx_graph:

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
                edge = self._convert_nx_hypernode(nx_graph, v)
                in_nodes, out_nodes = edge
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

    def nodes_of(self, edge: GenericEdge | Nodes | Node) -> Iterator[Node]:
        """Returns an ``Iterator`` of node id's that are incident to the given edge.

        Args:
            edge: an edge of this TrackGraph.

        Yields:
            all nodes incident to the given edge.
        """
        # recursively descent into tuples and yield their elements if they are
        # not tuples
        if isinstance(edge, tuple):
            for x in edge:
                yield from self.nodes_of(x)
        else:
            yield edge

    def is_hyperedge(self, edge: GenericEdge) -> TypeGuard[HyperEdge]:
        """Test if the given edge is a hyperedge in this track graph."""
        assert len(edge) == 2, "(Hyper)edges need to be 2-tuples"
        num_tuples = sum(isinstance(x, tuple) for x in edge)
        if num_tuples == 0:
            return False
        elif num_tuples == 2:
            return True
        raise RuntimeError(
            f"(Hyper)edges have to contain two tuples or two node IDs, not {edge}"
        )

    def _is_hyperedge_nx_node(self, nx_graph: networkx.DiGraph, nx_node: Any) -> bool:
        """Return ``True`` if ``nx_node`` is a hyperedge node in ``nx_graph``.

        Checks if the given networkx node in the given directed networkx graph
        represents an hyperedge. This boils down to checking if the node does not
        have the ``frame_attribute`` set.

        Args:
            nx_graph: a networkx ``DiGraph``.
            nx_node: a node in the given ``nx_graph``.

        Returns:
            bool: true iff the given ``nx_node`` does not posses the
            ``frame_attribute``.
        """
        return self.frame_attribute not in nx_graph.nodes[nx_node]

    def _convert_nx_hypernode(
        self, nx_graph: networkx.DiGraph, hyperedge_node: Any
    ) -> HyperEdge:
        """Creates a hyperedge tuple for hyperedge node in a given networkx ``DiGraph``.

        Args:
            nx_graph: a networkx ``DiGraph``.
            hyperedge_node: a node in the given ``nx_graph`` that represents
                a hyperedge.

        Returns:
            a tuple representing the hyperedge the given ``nx_node`` represented. (It
            will be a tuple with one entry per involved time point, listing all nodes at
            that time point.)
        """
        assert self._is_hyperedge_nx_node(nx_graph, hyperedge_node)

        in_nodes = tuple(nx_graph.predecessors(hyperedge_node))
        out_nodes = tuple(nx_graph.successors(hyperedge_node))

        return (in_nodes, out_nodes)

    def get_frames(self) -> tuple[int | None, int | None]:
        """Return tuple with first and last (exclusive) frame this graph has nodes for.

        Returns ``(t_begin, t_end)`` where ``t_end`` is exclusive.
        """
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
