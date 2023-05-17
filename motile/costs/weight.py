from typing import Any, Callable, List

Callback = Callable[[float, float], Any]


class Weight:
    """A single Weight with observer/callback pattern on update.

    See also :class:`motile.costs.weights.Weights`.

    Args:
        initial_value:
            The initial value of the weight.
    """

    def __init__(self, initial_value: float) -> None:
        self._value = initial_value
        self._modify_callbacks: List[Callback] = []

    @property
    def value(self) -> float:
        """Return the value of this weight."""
        return self._value

    @value.setter
    def value(self, new_value: float) -> None:
        """Set the value of this weight."""
        old_value = self._value
        self._value = new_value
        self._notify_modified(old_value, new_value)

    def register_modify_callback(self, callback: Callback) -> None:
        """Register a ``callback`` to be called when the weight is modified.

        Args:
            callback:
                A function that takes two arguments: the old value and the new value.
        """
        self._modify_callbacks.append(callback)

    def _notify_modified(self, old_value: float, new_value: float) -> None:
        for callback in self._modify_callbacks:
            callback(old_value, new_value)
