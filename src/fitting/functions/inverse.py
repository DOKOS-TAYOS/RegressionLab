"""Inverse and logarithmic fitting functions."""

from typing import Callable, Optional

import numpy as np
from numpy.typing import NDArray

from ._base import (
    DataLike,
    Numeric,
    estimate_inverse_parameter,
    estimate_ln_parameter,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
    merge_bounds,
    merge_initial_guess,
)


def ln_function(t: Numeric, a: float) -> Numeric:
    """Natural logarithm function: y = a*ln(t)"""
    return a * np.log(t)


def generate_inverse_function(power: int) -> Callable[..., Numeric]:
    """
    Generate an inverse power function dynamically based on the power.

    Args:
        power: The power of t in the denominator (e.g., 1 for 1/t, 2 for 1/t^2).

    Returns:
        A function that takes t and coefficient a as arguments.
    """
    def inverse_func(t: Numeric, a: float) -> Numeric:
        return a / (t**power)
    return inverse_func


inverse_function = generate_inverse_function(1)
inverse_square_function = generate_inverse_function(2)


def fit_ln_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[list[Optional[float]]] = None,
    bounds_override: Optional[tuple[list[Optional[float]], list[Optional[float]]]] = None,
) -> tuple[str, NDArray, str]:
    """
    Fit a logarithmic model :math:`y = a \\ln(x)`.

    Args:
        data: Data source with positive ``x`` values, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional override for the coefficient ``[a]``.
        bounds_override: Optional bounds for ``[a]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_ln_parameter(x, y)
    initial_guess = merge_initial_guess([a_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 1)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=ln_function,
        param_names=get_equation_param_names_for_function('fit_ln_function'),
        equation_template=get_equation_format_for_function('fit_ln_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_inverse_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[list[Optional[float]]] = None,
    bounds_override: Optional[tuple[list[Optional[float]], list[Optional[float]]]] = None,
) -> tuple[str, NDArray, str]:
    """
    Fit an inverse model :math:`y = a / x`.

    Args:
        data: Data source with non‑zero ``x`` values, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional override for ``[a]``.
        bounds_override: Optional bounds for ``[a]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_inverse_parameter(x, y, 1)
    initial_guess = merge_initial_guess([a_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 1)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=inverse_function,
        param_names=get_equation_param_names_for_function('fit_inverse_function'),
        equation_template=get_equation_format_for_function('fit_inverse_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_inverse_square_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[list[Optional[float]]] = None,
    bounds_override: Optional[tuple[list[Optional[float]], list[Optional[float]]]] = None,
) -> tuple[str, NDArray, str]:
    """
    Fit an inverse‑square model :math:`y = a / x^2`.

    Args:
        data: Data source with non‑zero ``x`` values, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional override for ``[a]``.
        bounds_override: Optional bounds for ``[a]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_inverse_parameter(x, y, 2)
    initial_guess = merge_initial_guess([a_0], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 1)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=inverse_square_function,
        param_names=get_equation_param_names_for_function('fit_inverse_square_function'),
        equation_template=get_equation_format_for_function('fit_inverse_square_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )
