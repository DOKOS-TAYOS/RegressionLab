"""Trigonometric and hyperbolic fitting functions."""

from typing import Callable, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

from fitting.functions._base import (
    DataLike,
    Numeric,
    estimate_hyperbolic_bounds,
    estimate_hyperbolic_parameters,
    estimate_phase_shift,
    estimate_trigonometric_parameters,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
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
    """
    Fit a sine model without phase, :math:`y = a \\sin(b x)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b]``.
        bounds_override: Optional bounds for ``[a, b]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
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
        param_names=get_equation_param_names_for_function('fit_sin_function'),
        equation_template=get_equation_format_for_function('fit_sin_function'),
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
    """
    Fit a sine model with phase, :math:`y = a \\sin(b x + c)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b, c]``.
        bounds_override: Optional bounds for ``[a, b, c]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
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
        param_names=get_equation_param_names_for_function('fit_sin_function_with_c'),
        equation_template=get_equation_format_for_function('fit_sin_function_with_c'),
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
    """
    Fit a cosine model without phase, :math:`y = a \\cos(b x)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b]``.
        bounds_override: Optional bounds for ``[a, b]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
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
        param_names=get_equation_param_names_for_function('fit_cos_function'),
        equation_template=get_equation_format_for_function('fit_cos_function'),
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
    """
    Fit a cosine model with phase, :math:`y = a \\cos(b x + c)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b, c]``.
        bounds_override: Optional bounds for ``[a, b, c]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
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
        param_names=get_equation_param_names_for_function('fit_cos_function_with_c'),
        equation_template=get_equation_format_for_function('fit_cos_function_with_c'),
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
    """
    Fit a hyperbolic sine model, :math:`y = a \\sinh(b x)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b]``.
        bounds_override: Optional bounds for ``[a, b]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_hyperbolic_parameters(x, y)
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    computed_bounds = estimate_hyperbolic_bounds(x)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=sinh_function,
        param_names=get_equation_param_names_for_function('fit_sinh_function'),
        equation_template=get_equation_format_for_function('fit_sinh_function'),
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
    """
    Fit a hyperbolic cosine model, :math:`y = a \\cosh(b x)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b]``.
        bounds_override: Optional bounds for ``[a, b]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_hyperbolic_parameters(x, y)
    initial_guess = merge_initial_guess([amplitude, frequency], initial_guess_override)
    computed_bounds = estimate_hyperbolic_bounds(x)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=cosh_function,
        param_names=get_equation_param_names_for_function('fit_cosh_function'),
        equation_template=get_equation_format_for_function('fit_cosh_function'),
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
    """
    Fit a tangent model without phase, :math:`y = a \\tan(b x)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b]``.
        bounds_override: Optional bounds for ``[a, b]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
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
        param_names=get_equation_param_names_for_function('fit_tan_function'),
        equation_template=get_equation_format_for_function('fit_tan_function'),
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
    """
    Fit a tangent model with phase, :math:`y = a \\tan(b x + c)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b, c]``.
        bounds_override: Optional bounds for ``[a, b, c]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
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
        param_names=get_equation_param_names_for_function('fit_tan_function_with_c'),
        equation_template=get_equation_format_for_function('fit_tan_function_with_c'),
        initial_guess=initial_guess,
        bounds=bounds,
    )
