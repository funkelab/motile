from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Hashable, Iterable, Optional

import numpy as np

if TYPE_CHECKING:
    from .weight import Weight

Callback = Callable[[Optional[float], float], Any]


class Weights:
    """A simple container for weights with observer/callback pattern on update.

    A :class:`motile.Solver` has a :class:`Weights` instance that is used to
    store the weights of the model.  Changes to the weights can be observed with
    ``Solver.weights.register_modify_callback``
    """

    def __init__(self) -> None:
        self._weights: list[Weight] = []
        self._weights_by_name: dict[Hashable, Weight] = {}
        self._weight_indices: dict[Weight, int] = {}
        self._modify_callbacks: list[Callback] = []

    def add_weight(self, weight: Weight, name: Hashable) -> None:
        """Add a weight to the container.

        Args:
            weight:
                The :class:`~motile.costs.Weight` to add.
            name:
                The name of the weight.
        """
        self._weight_indices[weight] = len(self._weights)
        self._weights.append(weight)
        self._weights_by_name[name] = weight

        for callback in self._modify_callbacks:
            weight.register_modify_callback(callback)

        self._notify_modified(None, weight.value)

    def register_modify_callback(self, callback: Callback) -> None:
        """Register ``callback`` to be called when a weight is modified.

        Args:
            callback:
                A function that takes two arguments: the old value (which may be
                ``None``) and the new value.
        """
        self._modify_callbacks.append(callback)
        for weight in self._weights:
            weight.register_modify_callback(callback)

    def to_ndarray(self) -> np.ndarray:
        """Export the weights as a numpy array.

        Note: you can also use ``np.asarray(weights)``.
        """
        return np.array([w.value for w in self._weights], dtype=np.float32)

    def __array__(self) -> np.ndarray:
        return self.to_ndarray()

    def from_ndarray(self, values: Iterable[float]) -> None:
        """Update weights from an iterable of floats."""
        for weight, value in zip(self._weights, values):
            weight.value = value

    def index_of(self, weight: Weight) -> int:
        """Return the index of ``weight`` in this container."""
        return self._weight_indices[weight]

    def __getitem__(self, name: str) -> float:
        """Return the value of the weight with the given name."""
        return self._weights_by_name[name].value

    def __setitem__(self, name: str, value: float) -> None:
        """Set the value of the weight with the given name."""
        self._weights_by_name[name].value = value

    def _notify_modified(self, old_value: float | None, new_value: float) -> None:
        for callback in self._modify_callbacks:
            callback(old_value, new_value)

    def __repr__(self) -> str:
        return "".join(
            f"{name} = {weight.value}\n"
            for name, weight in self._weights_by_name.items()
        )
