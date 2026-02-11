"""Gaussian, exponential, binomial, square pulse, and Hermite fitting functions."""

from typing import List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.special import eval_hermite

# Steepness of tanh edges in smooth square pulse (larger = sharper edges)
_SQUARE_PULSE_STEEPNESS = 50.0

from fitting.functions._base import (
    DataLike,
    Numeric,
    estimate_binomial_parameters,
    estimate_exponential_parameters,
    estimate_gaussian_parameters,
    estimate_square_pulse_parameters,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
    merge_bounds,
    merge_initial_guess,
)


def _gaussian_function(t: Numeric, A: float, mu: float, sigma: float) -> Numeric:
    """Gaussian (normal) function: y = A * exp(-(t-mu)^2 / (2*sigma^2))"""
    return A * np.exp(-((t - mu) ** 2) / (2.0 * sigma**2))


def _exponential_function(t: Numeric, a: float, b: float) -> Numeric:
    """Exponential function: y = a * exp(b*t)"""
    return a * np.exp(b * t)


def _binomial_function(t: Numeric, a: float, b: float, c: float) -> Numeric:
    """Logistic (S-shaped, binomial-type) function: y = a / (1 + exp(-b*(t-c)))"""
    return a / (1.0 + np.exp(-b * (t - c)))


def _square_pulse_function(t: Numeric, A: float, t0: float, w: float) -> Numeric:
    """
    Smooth square pulse (approximation): y = A * (f(t - (t0-w/2)) - f(t - (t0+w/2)))/2
    with f(s) = tanh(k*s).
    """
    k = _SQUARE_PULSE_STEEPNESS
    return A * 0.5 * (np.tanh(k * (t - (t0 - w / 2.0))) - np.tanh(k * (t - (t0 + w / 2.0))))


def _hermite_polynomial_3(t: Numeric, c0: float, c1: float, c2: float, c3: float) -> Numeric:
    """Sum of physicist's Hermite polynomials up to degree 3."""
    return (
        c0 * eval_hermite(0, t) + c1 * eval_hermite(1, t)
        + c2 * eval_hermite(2, t) + c3 * eval_hermite(3, t)
    )


def _hermite_polynomial_4(
    t: Numeric, c0: float, c1: float, c2: float, c3: float, c4: float
) -> Numeric:
    """Sum of physicist's Hermite polynomials up to degree 4."""
    out = _hermite_polynomial_3(t, c0, c1, c2, c3) + c4 * eval_hermite(4, t)
    return out


def fit_gaussian_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a Gaussian (normal) model
    :math:`y = A \\exp(-(x-\\mu)^2 / (2\\sigma^2))`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[A, μ, σ]``.
        bounds_override: Optional bounds for ``[A, μ, σ]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    A_0, mu_0, sigma_0 = estimate_gaussian_parameters(x, y)
    computed_bounds = ([0.0, -np.inf, 1e-9], [np.inf, np.inf, np.inf])
    initial_guess = merge_initial_guess(
        [A_0, mu_0, sigma_0], initial_guess_override
    )
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=_gaussian_function,
        param_names=get_equation_param_names_for_function('fit_gaussian_function'),
        equation_template=get_equation_format_for_function('fit_gaussian_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_exponential_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit an exponential model :math:`y = a \\exp(b x)`.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[a, b]``.
        bounds_override: Optional bounds for ``[a, b]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = np.asarray(data[x_name], dtype=float)
    y = np.asarray(data[y_name], dtype=float)
    x_range = float(np.ptp(x))
    if x_range < 1e-12:
        x_range = 1.0
    b_max = 700.0 / x_range
    computed_bounds = ([-np.inf, -b_max], [np.inf, b_max])
    a_0, b_0 = estimate_exponential_parameters(x, y)
    initial_guess = merge_initial_guess([a_0, b_0], initial_guess_override)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 2)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=_exponential_function,
        param_names=get_equation_param_names_for_function('fit_exponential_function'),
        equation_template=get_equation_format_for_function('fit_exponential_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_binomial_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a logistic (binomial‑type) model
    :math:`y = a / (1 + \\exp(-b (x - c)))`.

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
    a_0, b_0, c_0 = estimate_binomial_parameters(x, y)
    computed_bounds = ([1e-9, 1e-9, -np.inf], [np.inf, np.inf, np.inf])
    initial_guess = merge_initial_guess([a_0, b_0, c_0], initial_guess_override)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=_binomial_function,
        param_names=get_equation_param_names_for_function('fit_binomial_function'),
        equation_template=get_equation_format_for_function('fit_binomial_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_square_pulse_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a smooth square‑pulse model in time.

    The underlying function approximates a finite‑width pulse centered at
    ``t0`` with width ``w`` and amplitude ``A`` using hyperbolic tangents.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[A, t0, w]``.
        bounds_override: Optional bounds for ``[A, t0, w]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    A_0, t0_0, w_0 = estimate_square_pulse_parameters(x, y)
    x_range = float(np.ptp(x))
    x_min, x_max = float(np.min(x)), float(np.max(x))
    computed_bounds = (
        [1e-9, x_min - x_range, 1e-9],
        [np.inf, x_max + x_range, x_range * 2],
    )
    initial_guess = merge_initial_guess([A_0, t0_0, w_0], initial_guess_override)
    bounds = (
        merge_bounds(computed_bounds, bounds_override[0], bounds_override[1], 3)
        if bounds_override is not None
        else computed_bounds
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=_square_pulse_function,
        param_names=get_equation_param_names_for_function('fit_square_pulse_function'),
        equation_template=get_equation_format_for_function('fit_square_pulse_function'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_hermite_polynomial_3(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a Hermite polynomial expansion up to degree 3.

    The model is :math:`y = c_0 H_0(x) + c_1 H_1(x) + c_2 H_2(x) + c_3 H_3(x)`,
    where :math:`H_k` are physicists’ Hermite polynomials.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[c0, c1, c2, c3]``.
        bounds_override: Optional bounds for ``[c0, c1, c2, c3]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    y_mean = float(np.mean(y))
    initial_guess = merge_initial_guess(
        [y_mean, 0.0, 0.0, 0.0], initial_guess_override
    )
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 4)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=_hermite_polynomial_3,
        param_names=get_equation_param_names_for_function('fit_hermite_polynomial_3'),
        equation_template=get_equation_format_for_function('fit_hermite_polynomial_3'),
        initial_guess=initial_guess,
        bounds=bounds,
    )


def fit_hermite_polynomial_4(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit a Hermite polynomial expansion up to degree 4.

    The model extends :func:`fit_hermite_polynomial_3` with an additional
    :math:`c_4 H_4(x)` term.

    Args:
        data: Data source with ``x``, ``y`` and uncertainties.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        initial_guess_override: Optional overrides for ``[c0, c1, c2, c3, c4]``.
        bounds_override: Optional bounds for ``[c0, c1, c2, c3, c4]``.

    Returns:
        Tuple ``(text, y_fitted, equation)`` from :func:`generic_fit`.
    """
    x = data[x_name]
    y = data[y_name]
    y_mean = float(np.mean(y))
    initial_guess = merge_initial_guess(
        [y_mean, 0.0, 0.0, 0.0, 0.0], initial_guess_override
    )
    bounds = (
        merge_bounds(None, bounds_override[0], bounds_override[1], 5)
        if bounds_override is not None
        else None
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=_hermite_polynomial_4,
        param_names=get_equation_param_names_for_function('fit_hermite_polynomial_4'),
        equation_template=get_equation_format_for_function('fit_hermite_polynomial_4'),
        initial_guess=initial_guess,
        bounds=bounds,
    )
