try:
    import structsvm as ssvm
except ImportError as e:
    raise ImportError(
        "This functionality requires the structsvm package. "
        "Please install structsvm."
    ) from e

import numpy as np

from .variables import NodeSelected


def fit_weights(
        solver,
        gt_attribute,
        regularizer_weight=0.1,
        eps=1e-6,
        max_iterations=None):

    features = solver.features.to_ndarray()

    mask = np.zeros((solver.num_variables,), dtype=np.float32)
    ground_truth = np.zeros((solver.num_variables,), dtype=np.float32)
    for node, index in solver.get_variables(NodeSelected).items():
        if gt_attribute in solver.graph.nodes[node]:
            mask[index] = 1.0
            ground_truth[index] = solver.graph.nodes[node][gt_attribute]

    loss = ssvm.SoftMarginLoss(
        solver.constraints,
        features.T,  # TODO: fix in ssvm
        ground_truth,
        ssvm.HammingCosts(ground_truth, mask))
    bundle_method = ssvm.BundleMethod(
        loss.value_and_gradient,
        dims=features.shape[1],
        regularizer_weight=regularizer_weight,
        eps=eps)

    return bundle_method.optimize(max_iterations)
