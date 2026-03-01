"""Shared types and imports for fitting functions."""

from typing import Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray

# Re-export fitting utilities
from fitting.fitting_utils import (
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
    merge_bounds,
    merge_initial_guess,
)

# Re-export estimators
from fitting.estimators import (
    estimate_binomial_parameters,
    estimate_exponential_parameters,
    estimate_gaussian_parameters,
    estimate_hyperbolic_bounds,
    estimate_hyperbolic_parameters,
    estimate_inverse_parameter,
    estimate_linear_parameters,
    estimate_ln_parameter,
    estimate_phase_shift,
    estimate_polynomial_parameters,
    estimate_single_power_parameter,
    estimate_square_pulse_parameters,
    estimate_trigonometric_parameters,
)

Numeric = Union[float, NDArray[np.floating]]
DataLike = Union[dict, pd.DataFrame]

__all__ = [
    'Numeric',
    'DataLike',
    'generic_fit',
    'get_equation_format_for_function',
    'get_equation_param_names_for_function',
    'merge_bounds',
    'merge_initial_guess',
    'estimate_binomial_parameters',
    'estimate_exponential_parameters',
    'estimate_gaussian_parameters',
    'estimate_hyperbolic_bounds',
    'estimate_hyperbolic_parameters',
    'estimate_inverse_parameter',
    'estimate_linear_parameters',
    'estimate_ln_parameter',
    'estimate_phase_shift',
    'estimate_polynomial_parameters',
    'estimate_single_power_parameter',
    'estimate_square_pulse_parameters',
    'estimate_trigonometric_parameters',
]
