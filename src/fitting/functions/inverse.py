"""Inverse and logarithmic fitting functions."""

from typing import Callable, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from ._base import (
    DataLike,
    Numeric,
    estimate_inverse_parameter,
    estimate_ln_parameter,
    generic_fit,
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
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
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
        param_names=['a'],
        equation_template='y={a} ln(x)',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_inverse_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
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
        param_names=['a'],
        equation_template='y={a}/x',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_inverse_square_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
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
        param_names=['a'],
        equation_template='y={a}/x^2',
        initial_guess=initial_guess,
        bounds=bounds,
    )
