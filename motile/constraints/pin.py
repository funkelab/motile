from __future__ import annotations

from .expression import ExpressionConstraint


class Pin(ExpressionConstraint):
    """Enforces the selection of nodes/edges based on truthiness of a given attribute.

    Every node or edge that has the given attribute will be selected if the
    attribute value is ``True`` (and not selected if the attribute value is
    ``False``). The solver will only determine the selection of nodes and edges
    that do not have this attribute.

    This constraint is useful to complete partial tracking solutions, e.g.,
    when users have already manually selected (or unselected) certain nodes or
    edges.

    Args:
        attribute:
            The name of the node/edge attribute to use.
    """

    def __init__(self, attribute: str) -> None:
        super().__init__(f"{attribute} == True", eval_nodes=True, eval_edges=True)
