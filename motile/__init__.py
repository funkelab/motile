from importlib.metadata import PackageNotFoundError, version

from .solver import Solver
from .track_graph import TrackGraph

try:
    __version__ = version("motile")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

__all__ = ["Solver", "TrackGraph"]
