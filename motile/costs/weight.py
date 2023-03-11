class Weight:

    def __init__(self, initial_value):
        self._value = initial_value
        self._modify_callbacks = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = new_value
        self._notify_modified(old_value, new_value)

    def register_modify_callback(self, callback):
        self._modify_callbacks.append(callback)

    def _notify_modified(self, old_value, new_value):
        for callback in self._modify_callbacks:
            callback(old_value, new_value)
