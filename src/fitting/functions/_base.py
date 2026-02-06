"""Shared types and imports for fitting functions."""

from typing import Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from fitting import fitting_utils, estimators

generic_fit = fitting_utils.generic_fit
merge_bounds = fitting_utils.merge_bounds
merge_initial_guess = fitting_utils.merge_initial_guess

(
    estimate_binomial_parameters,
    estimate_gaussian_parameters,
    estimate_exponential_parameters,
    estimate_inverse_parameter,
    estimate_linear_parameters,
    estimate_ln_parameter,
    estimate_phase_shift,
    estimate_polynomial_parameters,
    estimate_single_power_parameter,
    estimate_square_pulse_parameters,
    estimate_trigonometric_parameters,
) = (
    estimators.estimate_binomial_parameters,
    estimators.estimate_gaussian_parameters,
    estimators.estimate_exponential_parameters,
    estimators.estimate_inverse_parameter,
    estimators.estimate_linear_parameters,
    estimators.estimate_ln_parameter,
    estimators.estimate_phase_shift,
    estimators.estimate_polynomial_parameters,
    estimators.estimate_single_power_parameter,
    estimators.estimate_square_pulse_parameters,
    estimators.estimate_trigonometric_parameters,
)

Numeric = Union[float, NDArray[np.floating]]
DataLike = Union[dict, pd.DataFrame]

__all__ = [
    'Numeric',
    'DataLike',
    'generic_fit',
    'merge_bounds',
    'merge_initial_guess',
    'estimate_binomial_parameters',
    'estimate_gaussian_parameters',
    'estimate_exponential_parameters',
    'estimate_inverse_parameter',
    'estimate_linear_parameters',
    'estimate_ln_parameter',
    'estimate_phase_shift',
    'estimate_polynomial_parameters',
    'estimate_single_power_parameter',
    'estimate_square_pulse_parameters',
    'estimate_trigonometric_parameters',
]
