"""Trigonometric and hyperbolic fitting functions."""

from typing import Callable, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from ._base import (
    DataLike,
    Numeric,
    estimate_phase_shift,
    estimate_trigonometric_parameters,
    generic_fit,
    merge_bounds,
    merge_initial_guess,
)


def generate_trigonometric_function(
    func_type: str, with_phase: bool = False
) -> Callable[..., Numeric]:
    """
    Generate a trigonometric function dynamically based on the function type.

    Args:
        func_type: Type of function ('sin', 'cos', 'sinh', 'cosh').
        with_phase: Whether to include a phase shift parameter c.

    Returns:
        A function that takes t and parameters (a, b, [c]) as arguments.
    """
    func_map = {
        'sin': np.sin,
        'cos': np.cos,
        'sinh': np.sinh,
        'cosh': np.cosh
    }
    if func_type not in func_map:
        raise ValueError(f"Unknown function type: {func_type}")
    np_func = func_map[func_type]

    if with_phase:
        def trig_func(t: Numeric, a: float, b: float, c: float) -> Numeric:
            return a * np_func(b * t + c)
    else:
        def trig_func(t: Numeric, a: float, b: float) -> Numeric:
            return a * np_func(b * t)

    return trig_func


sin_function = generate_trigonometric_function('sin', with_phase=False)
sin_function_with_c = generate_trigonometric_function('sin', with_phase=True)
cos_function = generate_trigonometric_function('cos', with_phase=False)
cos_function_with_c = generate_trigonometric_function('cos', with_phase=True)
sinh_function = generate_trigonometric_function('sinh', with_phase=False)
cosh_function = generate_trigonometric_function('cosh', with_phase=False)


def tan_function(t: Numeric, a: float, b: float) -> Numeric:
    """Tangent function: y = a * tan(b*t)"""
    return a * np.tan(b * t)


def tan_function_with_c(t: Numeric, a: float, b: float, c: float) -> Numeric:
    """Tangent function with phase: y = a * tan(b*t + c)"""
    return a * np.tan(b * t + c)


def fit_sin_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=sin_function,
        param_names=['a', 'b'],
        equation_template='y={a} sin({b}x)',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_sin_function_with_c(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    phase = estimate_phase_shift(x, y, amplitude, frequency)
    initial_guess = merge_initial_guess(
        [amplitude, frequency, phase], initial_guess_override
    )
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=sin_function_with_c,
        param_names=['a', 'b', 'c'],
        equation_template='y={a} sin({b}x+{c})',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_cos_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=cos_function,
        param_names=['a', 'b'],
        equation_template='y={a} cos({b}x)',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_cos_function_with_c(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    phase = estimate_phase_shift(x, y, amplitude, frequency)
    initial_guess = merge_initial_guess(
        [amplitude, frequency, phase], initial_guess_override
    )
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=cos_function_with_c,
        param_names=['a', 'b', 'c'],
        equation_template='y={a} cos({b}x+{c})',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_sinh_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    y_range = np.max(y) - np.min(y)
    amplitude = y_range / 2.0 if y_range > 0 else 1.0
    x_range = float(np.ptp(x))
    frequency = 1.0 / x_range if x_range > 1e-30 else 1.0
    b_max = 700.0 / (np.max(np.abs(x)) + 1e-30)
    computed_bounds = ([-np.inf, 1e-9], [np.inf, min(b_max, 1e3)])
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=sinh_function,
        param_names=['a', 'b'],
        equation_template='y={a} sinh({b}x)',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_cosh_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    y_min = np.min(y)
    y_max = np.max(y)
    amplitude = (y_max - y_min) / 2.0 if (y_max - y_min) > 0 else 1.0
    x_range = float(np.ptp(x))
    frequency = 1.0 / x_range if x_range > 1e-30 else 1.0
    b_max = 700.0 / (np.max(np.abs(x)) + 1e-30)
    computed_bounds = ([-np.inf, 1e-9], [np.inf, min(b_max, 1e3)])
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=cosh_function,
        param_names=['a', 'b'],
        equation_template='y={a} cosh({b}x)',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_tan_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=tan_function,
        param_names=['a', 'b'],
        equation_template='y={a} tan({b}x)',
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_tan_function_with_c(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    phase = estimate_phase_shift(x, y, amplitude, frequency)
    initial_guess = merge_initial_guess(
        [amplitude, frequency, phase], initial_guess_override
    )
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=tan_function_with_c,
        param_names=['a', 'b', 'c'],
        equation_template='y={a} tan({b}x+{c})',
        initial_guess=initial_guess,
        bounds=bounds,
    )
