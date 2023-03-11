import numpy as np
import ilpy
import structsvm as ssvm

from .constraints import Pin


def fit_weights(
        solver,
        gt_attribute,
        regularizer_weight=0.1,
        eps=1e-6,
        max_iterations=None):

    features = solver.features.to_ndarray()

    # make a copy of the original constraints
    constraints = solver.constraints
    solver.constraints = ilpy.LinearConstraints()
    solver.constraints.add_all(constraints)

    # pin GT nodes/edges to find solution vector
    pin_constraints = Pin(attribute=gt_attribute)
    solver.add_constraints(pin_constraints)
    solution = solver.solve()
    ground_truth = np.array([x for x in solution])

    # restore original constraints
    solver.constraints = constraints

    constraints = solver.constraints

    loss = ssvm.SoftMarginLoss(
        constraints,
        features.T,  # TODO: fix in ssvm
        ground_truth)
    bundle_method = ssvm.BundleMethod(
        loss.value_and_gradient,
        dims=features.shape[1],
        regularizer_weight=regularizer_weight,
        eps=eps)

    return bundle_method.optimize(max_iterations)
