from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, DefaultDict, Hashable

import networkx

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Mapping

    from motile._types import (
        Attributes,
        Edge,
        Node,
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
        self.edges: dict[Edge, Attributes] = {}
        self.prev_edges: defaultdict[Node, list[Edge]] = DefaultDict(list)
        self.next_edges: defaultdict[Node, list[Edge]] = DefaultDict(list)

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

    def add_edge(self, edge_id: Edge, data: Attributes) -> None:
        """Adds an edge to this TrackGraph.

        Args:
            edge_id: a tuple ``(u, v)`` defining the edge to be added.
            data: all properties associated to the added edge.
        """
        self.edges[edge_id] = data
        u, v = edge_id
        self.prev_edges[v].append(edge_id)
        self.next_edges[u].append(edge_id)
        self._graph_changed = True

    def add_from_nx_graph(self, nx_graph: networkx.DiGraph) -> None:
        """Add nodes/edges from ``nx_graph`` to this TrackGraph.

        Args:
            nx_graph (networkx.DiGraph):

                A directed networkx graph representing a TrackGraph to be added.

                Duplicate nodes and edges will not be added again but new attributes
                associated to nodes and edges added. If attributes of existing nodes
                or edges do already exist, the values set in the given ``nx_graph``
                will be updating the previously set values.
        """
        nodes_count = 0
        # add all regular nodes
        for node, data in nx_graph.nodes.items():
            if self.frame_attribute in data:
                if node not in self.nodes:
                    self.nodes[node] = data
                else:
                    self.nodes[node] |= data
                nodes_count += 1

        # graph without nodes, it's very likely this was not intentional
        if nodes_count == 0:
            raise KeyError(
                f"No nodes with `frame_attribute` '{self.frame_attribute}' found in "
                "the `nx_graph`.\nIt's likely the wrong `frame_attribute` was set."
            )

        # add all edges
        for (u, v), data in nx_graph.edges.items():
            edge: Edge = (u, v)
            if edge not in self.edges:
                self.edges[edge] = data
                self.prev_edges[v].append(edge)
                self.next_edges[u].append(edge)

    def to_nx_graph(self) -> networkx.DiGraph:
        """Convert this TrackGraph into a networkx DiGraph.

        Returns:
            networkx.DiGraph: Directed networkx graph with same nodes, edges, and
                attributes.
        """
        nx_graph = networkx.DiGraph()
        nodes_list = list(self.nodes.items())
        nx_graph.add_nodes_from(nodes_list)
        edges_list: list[tuple[Any, Any, Mapping]] = []
        for (u, v), data in self.edges.items():
            edges_list.append((u, v, data))
        nx_graph.add_edges_from(edges_list)
        return nx_graph

    def get_frames(self) -> tuple[int, int]:
        """Return tuple with first and last (exclusive) frame this graph has nodes for.

        Returns ``(t_begin, t_end)`` where ``t_end`` is exclusive.
        Returns ``(0, 0)`` for empty graph.
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
            self.t_begin = 0
            self.t_end = 0
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

    def __str__(self) -> str:
        return f"TrackGraph({len(self.nodes)} nodes, {len(self.edges)} edges)"
