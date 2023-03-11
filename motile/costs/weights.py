import numpy as np


class Weights:

    def __init__(self):
        self._weights = []
        self._weights_by_name = {}
        self._weight_indices = {}
        self._modify_callbacks = []

    def add_weight(self, weight, name):
        self._weight_indices[weight] = len(self._weights)
        self._weights.append(weight)
        self._weights_by_name[name] = weight

        for callback in self._modify_callbacks:
            weight.register_modify_callback(callback)

        self._notify_modified(None, weight.value)

    def register_modify_callback(self, callback):
        self._modify_callbacks.append(callback)
        for weight in self._weights:
            weight.register_modify_callback(callback)

    def to_ndarray(self):
        return np.array([w.value for w in self._weights], dtype=np.float32)

    def from_ndarray(self, values):
        for weight, value in zip(self._weights, values):
            weight.value = value

    def index_of(self, weight):
        return self._weight_indices[weight]

    def __getitem__(self, name):
        return self._weights_by_name[name].value

    def __setitem__(self, name, value):
        self._weights_by_name[name].value = value

    def _notify_modified(self, old_value, new_value):
        for callback in self._modify_callbacks:
            callback(old_value, new_value)

    def __repr__(self):

        r = ''
        for name, weight in self._weights_by_name.items():
            r += f'{name} = {weight.value}\n'
        return r
