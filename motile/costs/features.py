from __future__ import annotations

import numpy as np


class Features:
    def __init__(self) -> None:
        self._values = np.zeros((0, 0), dtype=np.float32)

    def resize(
        self, num_variables: int | None = None, num_features: int | None = None
    ) -> None:
        if num_variables is None:
            num_variables = self._values.shape[0]
        if num_features is None:
            num_features = self._values.shape[1]

        if num_variables > self._values.shape[0]:
            self.resize_variables(num_variables, num_features)
        if num_features > self._values.shape[1]:
            self.resize_features(num_variables, num_features)

    def resize_variables(self, num_variables: int, num_features: int) -> None:
        # Increasing size without copying works only in dim 0
        self._values.resize((num_variables, num_features), refcheck=False)

    def resize_features(self, num_variables: int, num_features: int) -> None:
        # Need to copy the array when increasing size of dim 1
        new_values = np.zeros(
            shape=(num_variables, num_features),
            dtype=self._values.dtype,
        )
        new_values[
            :self._values.shape[0],
            :self._values.shape[1]
        ] = self._values
        self._values = new_values

    def add_feature(
        self, variable_index: int, feature_index: int, value: float
    ) -> None:
        num_variables, num_features = self._values.shape

        if variable_index >= num_variables or feature_index >= num_features:
            self.resize(
                max(variable_index + 1, num_variables),
                max(feature_index + 1, num_features))

        self._values[variable_index, feature_index] += value

    def to_ndarray(self) -> np.ndarray:
        # _values is already an ndarray, but this might change in the future
        # Note: consider implementing
        return self._values
