import logging

logger = logging.getLogger(__name__)


class TrackGraph:
    """A :class:`networkx.DiGraph` of objects with positions in time and space,
    and inter-frame edges between them.

    Provides a few convenience methods for time series graphs in addition to
    all the methods inherited from :class:`networkx.DiGraph`.

    Args:

        graph_data (optional):

            Optional graph data to pass to the :class:`networkx.DiGraph`
            constructor as ``incoming_graph_data``. This can be used to
            populate a track graph with entries from a generic
            ``networkx`` graph.

        frame_attribute (``string``, optional):

            The name of the node attribute that corresponds to the frame (i.e.,
            the time dimension) of the object. Defaults to ``'t'``.
    """

    def __init__(
            self,
            graph=None,
            frame_attribute='t',
            is_bipartite=False):

        self.frame_attribute = frame_attribute
        self.is_bipartite = is_bipartite
        self._graph_changed = True

        self.nx_graph = graph

        self.nodes = {
            node: graph.nodes[node]
            for node in graph.nodes
            if frame_attribute in graph.nodes[node]
        }

        self.prev_edges = {node: [] for node in self.nodes}
        self.next_edges = {node: [] for node in self.nodes}

        if is_bipartite:
            self.edges = {
                self._assignment_node_to_edge_tuple(
                    graph,
                    assignment_node):
                graph.nodes[assignment_node]
                for assignment_node in graph.nodes
                if frame_attribute not in graph.nodes[assignment_node]
            }
        else:
            self.edges = graph.edges
            for (u, v) in graph.edges:
                self.prev_edges[v].append((u, v))
                self.next_edges[u].append((u, v))

        self._update_metadata()

    def _assignment_node_to_edge_tuple(self, graph, assignment_node):

        in_nodes = graph.predecessors(assignment_node)
        out_nodes = graph.successors(assignment_node)
        nodes = in_nodes + out_nodes

        frames = list(node[self.frame_attribute] for node in nodes)
        frames = sorted(frames)

        edge_tuple = tuple(
            tuple(
                node
                for node in nodes
                if node[self.frame_attribute] == frame
            )
            for frame in frames
        )

        for in_node in in_nodes:
            self.next_edges[in_nodes].append(edge_tuple)
        for out_node in out_nodes:
            self.prev_edges[out_nodes].append(edge_tuple)

        return edge_tuple

    def get_frames(self):
        '''Get a tuple ``(t_begin, t_end)`` of the first and last frame
        (exclusive) this track graph has nodes for.'''

        self._update_metadata()

        return (self.t_begin, self.t_end)

    def nodes_by_frame(self, t):
        '''Get all nodes in frame ``t``.'''

        self._update_metadata()

        if t not in self._nodes_by_frame:
            return []
        return self._nodes_by_frame[t]

    def _update_metadata(self):

        if not self._graph_changed:
            return

        self._graph_changed = False

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
                assert t_u < t_v, \
                    f"Edge ({u}, {v}) does not point forwards in time, but " \
                    f"from frame {t_u} to {t_v}"

        self._graph_changed = False
