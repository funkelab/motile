import numpy as np


class Features:

    def __init__(self):
        self._values = np.zeros((0, 0), dtype=np.float32)

    def resize(self, num_variables=None, num_features=None):

        if num_variables is None:
            num_variables = self._values.shape[0]
        if num_features is None:
            num_features = self._values.shape[1]

        self._values.resize((num_variables, num_features), refcheck=False)

    def add_feature(self, variable_index, feature_index, value):

        num_variables, num_features = self._values.shape

        if variable_index >= num_variables or feature_index >= num_features:
            self.resize(variable_index + 1, feature_index + 1)

        self._values[variable_index, feature_index] += value

    def to_ndarray(self):
        # _values is already an ndarray, but this might change in the future
        return self._values
