from typing import Any, Callable, List

Callback = Callable[[float, float], Any]


class Weight:
    
    def __init__(self, initial_value: float) -> None:
        self._value = initial_value
        self._modify_callbacks: List[Callback] = []

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float) -> None:
        old_value = self._value
        self._value = new_value
        self._notify_modified(old_value, new_value)

    def register_modify_callback(self, callback: Callback) -> None:
        self._modify_callbacks.append(callback)

    def _notify_modified(self, old_value: float, new_value: float) -> None:
        for callback in self._modify_callbacks:
            callback(old_value, new_value)
