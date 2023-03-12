from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Hashable, Iterable

import numpy as np

if TYPE_CHECKING:
    from .weight import Weight

Callback = Callable[[float | None, float], Any]

class Weights:

    def __init__(self) -> None:
        self._weights: list[Weight] = []
        self._weights_by_name: dict[Hashable, Weight] = {}
        self._weight_indices: dict[Weight, int] = {}
        self._modify_callbacks: list[Callback] = []

    def add_weight(self, weight: Weight, name: Hashable) -> None:
        self._weight_indices[weight] = len(self._weights)
        self._weights.append(weight)
        self._weights_by_name[name] = weight

        for callback in self._modify_callbacks:
            weight.register_modify_callback(callback)

        self._notify_modified(None, weight.value)

    def register_modify_callback(self, callback: Callback) -> None:
        self._modify_callbacks.append(callback)
        for weight in self._weights:
            weight.register_modify_callback(callback)

    def to_ndarray(self) -> np.ndarray:
        return np.array([w.value for w in self._weights], dtype=np.float32)

    def from_ndarray(self, values: Iterable[float]) -> None:
        for weight, value in zip(self._weights, values):
            weight.value = value

    def index_of(self, weight: Weight) -> int:
        return self._weight_indices[weight]

    def __getitem__(self, name: str) -> float:
        return self._weights_by_name[name].value

    def __setitem__(self, name: str, value: float) -> None:
        self._weights_by_name[name].value = value

    def _notify_modified(self, old_value: float | None, new_value: float) -> None:
        for callback in self._modify_callbacks:
            callback(old_value, new_value)

    def __repr__(self) -> str:
        return ''.join(
            f'{name} = {weight.value}\n'
            for name, weight in self._weights_by_name.items()
        )
