"""Polynomial and linear fitting functions."""

from typing import Callable, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from ._base import (
    DataLike,
    Numeric,
    estimate_linear_parameters,
    estimate_polynomial_parameters,
    estimate_single_power_parameter,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
    merge_bounds,
    merge_initial_guess,
)


def generate_polynomial_function(parameters: list[bool]) -> Callable:
    """
    Generate a polynomial function dynamically based on which parameters are enabled.

    Args:
        parameters: List of booleans indicating which polynomial terms to include.
                   Index i corresponds to the coefficient of t^i.

    Returns:
        A function that takes t and the enabled coefficients as arguments.
    """
    enabled_indices = [i for i, enabled in enumerate(parameters) if enabled]
    num_params = len(enabled_indices)

    if num_params == 0:
        def polynomial(t: Numeric) -> Numeric:
            return np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
        return polynomial

    if num_params == 1:
        def polynomial(t: Numeric, c0: float) -> Numeric:
            coeffs = (c0,)
            result = np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
            for coeff, power in zip(coeffs, enabled_indices):
                if power == 0:
                    result = result + coeff
                else:
                    result = result + coeff * t**power
            return result
    elif num_params == 2:
        def polynomial(t: Numeric, c0: float, c1: float) -> Numeric:
            coeffs = (c0, c1)
            result = np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
            for coeff, power in zip(coeffs, enabled_indices):
                if power == 0:
                    result = result + coeff
                else:
                    result = result + coeff * t**power
            return result
    elif num_params == 3:
        def polynomial(t: Numeric, c0: float, c1: float, c2: float) -> Numeric:
            coeffs = (c0, c1, c2)
            result = np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
            for coeff, power in zip(coeffs, enabled_indices):
                if power == 0:
                    result = result + coeff
                else:
                    result = result + coeff * t**power
            return result
    elif num_params == 4:
        def polynomial(t: Numeric, c0: float, c1: float, c2: float, c3: float) -> Numeric:
            coeffs = (c0, c1, c2, c3)
            result = np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
            for coeff, power in zip(coeffs, enabled_indices):
                if power == 0:
                    result = result + coeff
                else:
                    result = result + coeff * t**power
            return result
    elif num_params == 5:
        def polynomial(
            t: Numeric, c0: float, c1: float, c2: float, c3: float, c4: float
        ) -> Numeric:
            coeffs = (c0, c1, c2, c3, c4)
            result = np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
            for coeff, power in zip(coeffs, enabled_indices):
                if power == 0:
                    result = result + coeff
                else:
                    result = result + coeff * t**power
            return result
    else:
        raise ValueError(f"Unsupported number of parameters: {num_params}")

    return polynomial


linear_function_with_n = generate_polynomial_function([True, True])
linear_function = generate_polynomial_function([False, True])
quadratic_function_complete = generate_polynomial_function([True, True, True])
quadratic_function = generate_polynomial_function([False, False, True])
fourth_power = generate_polynomial_function([False, False, False, False, True])


def fit_linear_function_with_n(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a linear model with intercept, :math:`y = m x + n`.

    Args:
        data: Data source (dictionary or DataFrame) containing ``x``, ``y`` and
            their uncertainties (``ux``, ``uy``).
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional list overriding the automatically
            estimated ``[n, m]``; ``None`` entries keep the estimate.
        bounds_override: Optional pair ``(lower, upper)`` with bounds for
            ``[n, m]``; ``None`` entries keep the estimator bounds.

    Returns:
        Tuple ``(text, y_fitted, equation)`` as produced by
        :func:`fitting.fitting_utils.generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    n_0, m_0 = estimate_linear_parameters(x, y)
    initial_guess = merge_initial_guess([n_0, m_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=linear_function_with_n,
        param_names=get_equation_param_names_for_function('fit_linear_function_with_n'),
        equation_template=get_equation_format_for_function('fit_linear_function_with_n'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_linear_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a linear model through the origin, :math:`y = m x`.

    Args:
        data: Data source with columns for ``x``, ``y`` and their uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional list overriding the estimated slope
            ``[m]``; ``None`` keeps the estimate.
        bounds_override: Optional pair ``(lower, upper)`` with bounds for ``[m]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    m_0 = estimate_single_power_parameter(x, y, 1)
    initial_guess = merge_initial_guess([m_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 1)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=linear_function,
        param_names=get_equation_param_names_for_function('fit_linear_function'),
        equation_template=get_equation_format_for_function('fit_linear_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_quadratic_function_complete(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a full quadratic model :math:`y = c x^2 + b x + a`.

    Args:
        data: Data source with ``x``, ``y`` and their uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b, c]``.
        bounds_override: Optional bounds for ``[a, b, c]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    initial_guess = merge_initial_guess(
        estimate_polynomial_parameters(x, y, 2), initial_guess_override
    )
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=quadratic_function_complete,
        param_names=get_equation_param_names_for_function('fit_quadratic_function_complete'),
        equation_template=get_equation_format_for_function('fit_quadratic_function_complete'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_quadratic_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a pure quadratic model through the origin, :math:`y = a x^2`.

    Args:
        data: Data source with ``x``, ``y`` and their uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional override for ``[a]``.
        bounds_override: Optional bounds for ``[a]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_single_power_parameter(x, y, 2)
    initial_guess = merge_initial_guess([a_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 1)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=quadratic_function,
        param_names=get_equation_param_names_for_function('fit_quadratic_function'),
        equation_template=get_equation_format_for_function('fit_quadratic_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_fourth_power(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a fourth‑power model through the origin, :math:`y = a x^4`.

    Args:
        data: Data source with ``x``, ``y`` and their uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional override for ``[a]``.
        bounds_override: Optional bounds for ``[a]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_single_power_parameter(x, y, 4)
    initial_guess = merge_initial_guess([a_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 1)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=fourth_power,
        param_names=get_equation_param_names_for_function('fit_fourth_power'),
        equation_template=get_equation_format_for_function('fit_fourth_power'),
        initial_guess=initial_guess,
        bounds=bounds,
    )
