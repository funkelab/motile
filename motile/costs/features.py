from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import ilpy


class Features:
    """Simple container for features with resizeable dimensions.

    A :class:`~motile.Solver` has a :class:`Features` instance.
    """

    def __init__(self) -> None:
        self._values = np.zeros((0, 0), dtype=np.float32)

    def resize(
        self, num_variables: int | None = None, num_features: int | None = None
    ) -> None:
        """Resize the feature matrix.

        Args:
            num_variables:
                The number of variables to resize to. If None, the number of
                variables is not changed.
            num_features:
                The number of features to resize to. If None, the number of
                features is not changed.
        """
        if num_variables is None:
            num_variables = self._values.shape[0]
        if num_features is None:
            num_features = self._values.shape[1]

        # Resize features first for efficiency
        if num_features > self._values.shape[1]:
            self._increase_features(num_features)

        if num_variables > self._values.shape[0]:
            self._increase_variables(num_variables)

    def _increase_variables(self, num_variables: int) -> None:
        # Increasing size without copying works only in dim 0
        self._values.resize((num_variables, self._values.shape[1]), refcheck=False)

    def _increase_features(self, num_features: int) -> None:
        # Need to copy the array when increasing size of dim 1
        shape = (self._values.shape[0], num_features - self._values.shape[1])
        new_features = np.zeros(shape, dtype=self._values.dtype)
        self._values = np.hstack((self._values, new_features))

    def add_feature(
        self, variable_index: int | ilpy.Variable, feature_index: int, value: float
    ) -> None:
        """Add a value to a feature.

        Args:
            variable_index:
                The index of the variable to add the value to.
            feature_index:
                The index of the feature to add the value to.
            value:
                The value to add.
        """
        num_variables, num_features = self._values.shape

        variable_index = int(variable_index)
        if variable_index >= num_variables or feature_index >= num_features:
            self.resize(
                max(variable_index + 1, num_variables),
                max(feature_index + 1, num_features),
            )

        self._values[variable_index, feature_index] += value

    def to_ndarray(self) -> np.ndarray:
        """Export the feature matrix as a numpy array.

        Note: you can also use ``np.asarray(features)``.
        """
        # _values is already an ndarray, but this might change in the future
        # Note: consider implementing
        return self._values

    def __array__(self) -> np.ndarray:
        return self.to_ndarray()

    def __repr__(self) -> str:
        r = f"array of shape={self._values.shape}"
        if self._values.size > 0:
            r += f", values =\n{self._values}"
        else:
            r += " [empty]"
        return r
