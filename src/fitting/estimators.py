"""
Initial parameter estimators for curve fitting.

This module provides functions to estimate initial parameter values and
ranges for various model types (linear, polynomial, trigonometric,
gaussian, logistic, etc.) to improve fitting convergence.
"""

# Standard library
from typing import Any, List, Tuple

# Numerical library
import numpy as np

# Local imports
from i18n import t
from utils.logger import get_logger

logger = get_logger(__name__)


def estimate_trigonometric_parameters(x: Any, y: Any) -> Tuple[float, float]:
    """
    Estimate initial parameters for trigonometric functions (sin/cos).

    This function estimates the amplitude (a) and angular frequency (b)
    for functions of the form: y = a * sin(b*x) or y = a * cos(b*x)

    Args:
        x: Independent variable array
        y: Dependent variable array

    Returns:
        Tuple of (amplitude, frequency):
            - amplitude: Estimated amplitude parameter (a)
            - frequency: Estimated angular frequency parameter (b)
    """
    from scipy.signal import find_peaks

    y_range = np.max(y) - np.min(y)
    amplitude = y_range / 2.0

    if np.abs(amplitude) < 1e-10:
        amplitude = 1.0

    try:
        peaks, _ = find_peaks(np.abs(y - np.mean(y)), distance=max(1, len(x) // 10))

        if len(peaks) >= 2:
            peak_distances = np.diff(x[peaks])
            avg_peak_distance = np.mean(peak_distances)
            estimated_period = 2.0 * avg_peak_distance
            frequency = 2.0 * np.pi / estimated_period
        else:
            x_range = np.max(x) - np.min(x)
            estimated_period = x_range
            frequency = 2.0 * np.pi / estimated_period
    except Exception as e:
        logger.warning(t('log.peak_detection_failed', error=str(e)))
        x_range = np.max(x) - np.min(x)
        if x_range > 0:
            frequency = 2.0 * np.pi / x_range
        else:
            frequency = 1.0

    if frequency <= 0 or not np.isfinite(frequency):
        frequency = 1.0

    logger.debug(
        t(
            'log.estimated_trig_parameters',
            amplitude=f"{amplitude:.3f}",
            frequency=f"{frequency:.3f}"
        )
    )
    return amplitude, frequency


def estimate_phase_shift(x: Any, y: Any, amplitude: float, frequency: float) -> float:
    """
    Estimate initial phase shift for trigonometric functions with phase.

    For functions of the form: y = a * sin(b*x + c) or y = a * cos(b*x + c)

    Args:
        x: Independent variable array
        y: Dependent variable array
        amplitude: Estimated amplitude parameter
        frequency: Estimated frequency parameter

    Returns:
        Estimated phase shift (c)
    """
    try:
        y_normalized = y / (amplitude if amplitude != 0 else 1.0)
        first_max_idx = np.argmax(y_normalized)
        x_at_max = x[first_max_idx]
        phase = np.pi / 4.0 - frequency * x_at_max
        phase = np.arctan2(np.sin(phase), np.cos(phase))
    except Exception as e:
        logger.warning(t('log.phase_estimation_failed', error=str(e)))
        phase = 0.0

    logger.debug(t('log.estimated_phase_shift', phase=f"{phase:.3f}"))
    return phase


def estimate_linear_parameters(x: Any, y: Any) -> Tuple[float, float]:
    """
    Estimate initial parameters for linear fit y = m*x + n (intercept n, slope m).

    Args:
        x: Independent variable array
        y: Dependent variable array

    Returns:
        Tuple (n, m): intercept and slope.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 2:
        return float(np.mean(y)), 0.0
    coefs = np.polyfit(x, y, 1)
    return float(coefs[1]), float(coefs[0])


def estimate_polynomial_parameters(x: Any, y: Any, degree: int) -> List[float]:
    """
    Estimate initial parameters for polynomial y = c0 + c1*x + ... + c_degree*x^degree.
    Returns list [c0, c1, ..., c_degree] (constant term first).

    Args:
        x: Independent variable array
        y: Dependent variable array
        degree: Polynomial degree

    Returns:
        List of coefficients from constant to highest order.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) <= degree:
        return [0.0] * (degree + 1)
    coefs = np.polyfit(x, y, degree)
    return list(reversed(coefs))


def estimate_single_power_parameter(x: Any, y: Any, power: int) -> float:
    """
    Estimate coefficient a for y = a * x^power (no constant term).
    Least-squares: a = sum(y * x^power) / sum(x^(2*power)).

    Args:
        x: Independent variable array
        y: Dependent variable array
        power: Exponent (e.g. 2 for quadratic through origin, 4 for fourth power)

    Returns:
        Estimated coefficient a.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xp = x ** power
    denom = np.sum(xp * xp)
    if denom < 1e-30:
        return 1.0
    return float(np.sum(y * xp) / denom)


def estimate_ln_parameter(x: Any, y: Any) -> float:
    """
    Estimate initial parameter a for y = a * ln(x).
    Uses a = sum(y * ln(x)) / sum(ln(x)^2) (least squares with no intercept).

    Args:
        x: Independent variable array (must be positive)
        y: Dependent variable array

    Returns:
        Estimated coefficient a.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = np.where(x <= 0, np.nan, x)
    valid = np.isfinite(x) & np.isfinite(y)
    if not np.any(valid):
        return 1.0
    ln_x = np.log(x[valid])
    y_v = y[valid]
    denom = np.sum(ln_x * ln_x)
    if denom < 1e-30:
        return float(np.mean(y_v) / (np.mean(ln_x) + 1e-30))
    return float(np.sum(y_v * ln_x) / denom)


def estimate_inverse_parameter(x: Any, y: Any, power: int) -> float:
    """
    Estimate coefficient a for y = a / x^power.
    From y*x^power = a, use median of (y * x^power) for robustness.

    Args:
        x: Independent variable array (avoid zeros)
        y: Dependent variable array
        power: Power in denominator (1 or 2)

    Returns:
        Estimated coefficient a.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x_safe = np.where(np.abs(x) < 1e-30, np.nan, x)
    valid = np.isfinite(x_safe) & np.isfinite(y)
    if not np.any(valid):
        return 1.0
    a_vals = y[valid] * (x_safe[valid] ** power)
    return float(np.median(a_vals))


def estimate_gaussian_parameters(x: Any, y: Any) -> Tuple[float, float, float]:
    """
    Estimate initial (A, mu, sigma) for y = A * exp(-(x-mu)^2 / (2*sigma^2)).
    A from max(y), mu from x at max, sigma from FWHM-style.

    Args:
        x: Independent variable array
        y: Dependent variable array

    Returns:
        Tuple (A, mu, sigma).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    idx_max = int(np.argmax(y))
    A_0 = float(y[idx_max])
    mu_0 = float(x[idx_max])
    y_range = np.max(y) - np.min(y)
    if y_range < 1e-30:
        return A_0, mu_0, 1.0
    half = A_0 - 0.5 * (A_0 - np.min(y))
    above = np.where(y >= half)[0]
    if len(above) >= 2:
        x_half = x[above]
        width = np.max(x_half) - np.min(x_half)
        sigma_0 = width / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    else:
        x_range = float(np.ptp(x))
        sigma_0 = x_range / 4.0 if x_range > 0 else 1.0
    if sigma_0 <= 0 or not np.isfinite(sigma_0):
        sigma_0 = 1.0
    return A_0, mu_0, sigma_0


def estimate_binomial_parameters(x: Any, y: Any) -> Tuple[float, float, float]:
    """
    Estimate (a, b, c) for logistic y = a / (1 + exp(-b*(x-c))).
    a = range, c near midpoint of transition, b from inverse width.

    Args:
        x: Independent variable array
        y: Dependent variable array

    Returns:
        Tuple (a, b, c).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    y_min = float(np.min(y))
    y_max = float(np.max(y))
    a_0 = y_max - y_min if (y_max - y_min) > 1e-30 else 1.0
    mid_level = y_min + 0.5 * (y_max - y_min)
    idx = np.searchsorted(y, mid_level)
    if idx <= 0:
        c_0 = float(x[0])
    elif idx >= len(x):
        c_0 = float(x[-1])
    else:
        t_val = (mid_level - y[idx - 1]) / (y[idx] - y[idx - 1] + 1e-30)
        c_0 = float((1 - t_val) * x[idx - 1] + t_val * x[idx])
    x_range = float(np.ptp(x))
    if x_range < 1e-30:
        x_range = 1.0
    b_0 = 4.0 / x_range
    return a_0, b_0, c_0
