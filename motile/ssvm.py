from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import structsvm as ssvm

from .variables import EdgeSelected, NodeSelected

if TYPE_CHECKING:
    from motile.solver import Solver


def fit_weights(
    solver: Solver,
    gt_attribute: str,
    regularizer_weight: float,
    max_iterations: int | None,
    eps: float,
) -> np.ndarray:
    """Return the optimal weights for the given solver.

    This uses `structsvm.BundleMethod` to fit the weights.

    Args:
        solver (Solver):
            The solver to fit the weights for.
        gt_attribute (str):
            Node/edge attribute that marks the ground truth for fitting.
            `gt_attribute` is expected to be set to `1` for objects labeled as
            ground truth, `0` for objects explicitly labeled as not part of the
            ground truth, and `None` or not set for unlabeled objects.
        regularizer_weight (float):
            The weight of the quadratic regularizer.
        max_iterations (int):
            Maximum number of gradient steps in the structured SVM.
        eps (float):
            Convergence threshold.

    Returns:
        np.ndarray:
            The optimal weights for the given solver.
    """
    features = solver.features.to_ndarray()

    mask = np.zeros((solver.num_variables,), dtype=np.float32)
    ground_truth = np.zeros((solver.num_variables,), dtype=np.float32)

    for node, index in solver.get_variables(NodeSelected).items():
        gt = solver.graph.nodes[node].get(gt_attribute, None)
        if gt is not None:
            mask[index] = 1.0
            ground_truth[index] = gt

    for edge, index in solver.get_variables(EdgeSelected).items():
        gt = solver.graph.edges[edge].get(gt_attribute, None)
        if gt is not None:
            mask[index] = 1.0
            ground_truth[index] = gt

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
