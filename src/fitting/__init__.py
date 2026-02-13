"""
Fitting package for RegressionLab.

Re-exports fitting utilities, custom function evaluator, workflow controller,
and parameter estimators. Used by main_program and streamlit for curve fitting.
"""

# Import modules as attributes for backward compatibility
# These are needed for backward compatibility (e.g., fitting/functions/_base.py)
from .fitting_utils import (
    generic_fit,
    get_fitting_function,
    format_parameter,
    get_equation_param_info,
)
from .custom_function_evaluator import CustomFunctionEvaluator
from .workflow_controller import (
    reload_data_by_type,
    single_fit_with_loop,
    multiple_fit_with_loop,
    apply_all_equations,
    coordinate_data_loading,
    coordinate_data_viewing,
    coordinate_equation_selection,
    coordinate_custom_equation,
)
from .estimators import (
    estimate_trigonometric_parameters,
    estimate_phase_shift,
    estimate_linear_parameters,
    estimate_polynomial_parameters,
    estimate_single_power_parameter,
    estimate_ln_parameter,
    estimate_inverse_parameter,
    estimate_gaussian_parameters,
    estimate_binomial_parameters,
    estimate_exponential_parameters,
    estimate_square_pulse_parameters,
    estimate_hyperbolic_parameters,
    estimate_hyperbolic_bounds,
)

__all__ = [
    'generic_fit',
    'get_fitting_function',
    'format_parameter',
    'get_equation_param_info',
    'CustomFunctionEvaluator',
    'reload_data_by_type',
    'single_fit_with_loop',
    'multiple_fit_with_loop',
    'apply_all_equations',
    'coordinate_data_loading',
    'coordinate_data_viewing',
    'coordinate_equation_selection',
    'coordinate_custom_equation',
    'estimate_trigonometric_parameters',
    'estimate_phase_shift',
    'estimate_linear_parameters',
    'estimate_polynomial_parameters',
    'estimate_single_power_parameter',
    'estimate_ln_parameter',
    'estimate_inverse_parameter',
    'estimate_gaussian_parameters',
    'estimate_binomial_parameters',
    'estimate_exponential_parameters',
    'estimate_square_pulse_parameters',
    'estimate_hyperbolic_parameters',
    'estimate_hyperbolic_bounds',
]
