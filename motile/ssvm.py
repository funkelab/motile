from __future__ import annotations

try:
    import structsvm as ssvm
except ImportError as e:
    raise ImportError(
        "This functionality requires the structsvm package. "
        "Please install structsvm."
    ) from e

from typing import TYPE_CHECKING

import numpy as np

from .variables import EdgeSelected, NodeSelected

if TYPE_CHECKING:
    from motile.solver import Solver


def fit_weights(
    solver: Solver,
    gt_attribute: str,
    regularizer_weight: float = 0.1,
    eps: float = 1e-6,
    max_iterations: int | None = None,
) -> np.ndarray:
    features = solver.features.to_ndarray()

    mask = np.zeros((solver.num_variables,), dtype=np.float32)
    ground_truth = np.zeros((solver.num_variables,), dtype=np.float32)

    for node, index in solver.get_variables(NodeSelected).items():
        if gt_attribute in solver.graph.nodes[node]:
            mask[index] = 1.0
            ground_truth[index] = solver.graph.nodes[node][gt_attribute]

    for edge, index in solver.get_variables(EdgeSelected).items():
        if gt_attribute in solver.graph.edges[edge]:
            mask[index] = 1.0
            ground_truth[index] = solver.graph.edges[edge][gt_attribute]

    loss = ssvm.SoftMarginLoss(
        solver.constraints,
        features.T,  # TODO: fix in ssvm
        ground_truth,
        ssvm.HammingCosts(ground_truth, mask),
    )
    bundle_method = ssvm.BundleMethod(
        loss.value_and_gradient,
        dims=features.shape[1],
        regularizer_weight=regularizer_weight,
        eps=eps,
    )

    return bundle_method.optimize(max_iterations)
