from .track_graph import TrackGraph
import networkx as nx


def get_tracks(
    graph: TrackGraph,
    require_selected: bool = False,
    selected_attribute: str = "selected",
) -> list[TrackGraph]:
    '''Return a list of track graphs, each corresponding to one track.

    (i.e., a connected component in the track graph).

    Args:
        graph (:class:`TrackGraph`):

            The track graph to split into tracks.

        require_selected (``bool``):

            If ``True``, consider only edges that have a selected_attribute
            attribute that is set to ``True``. Otherwise, each edge will be
            considered for the connected component analysis.

        selected_attribute (``str``):

            Only used if require_selected=True. Determines the attribute
            name to check if an edge is selected. Default value is
            'selected'.

    Returns:

        A generator object of graphs, one for each track.
    '''

    if require_selected:

        selected_edges = [
            e
            for e in graph.edges
            if (selected_attribute in graph.edges[e]
                and graph.edges[e][selected_attribute])
        ]
        graph = graph.edge_subgraph(selected_edges)

    if len(graph.nodes) == 0:
        return []

    return [
        TrackGraph(
            graph_data=graph.subgraph(g).copy(),
            frame_attribute=graph.frame_attribute,
        )
        for g in nx.weakly_connected_components(graph)
    ]
