"""
Initial parameter estimators for curve fitting.

Inputs (x, y) are assumed to be finite and already validated/cleaned by the caller.
This module provides functions to estimate initial parameter values and
ranges for various model types (linear, polynomial, trigonometric,
gaussian, logistic, exponential, etc.) to improve fitting convergence.
"""

# Standard library
from typing import Any, List, Tuple

# Numerical library
import numpy as np

# Local imports
from i18n import t
from utils import get_logger

logger = get_logger(__name__)

# Minimum amplitude to avoid division by zero in phase estimation
_MIN_AMPLITUDE = 1e-10
# Minimum denominator to avoid singularities in least-squares
_EPS_DENOM = 1e-30
# Maximum number of lags for autocorrelation period estimation
_MAX_AUTOCORR_LAG = 200


def estimate_trigonometric_parameters(x: Any, y: Any) -> Tuple[float, float]:
    """
    Estimate initial parameters for trigonometric functions (sin/cos).

    Estimates amplitude (a) and angular frequency (b) for
    y = a * sin(b*x) or y = a * cos(b*x). Uses peak detection first,
    with autocorrelation fallback when peaks are insufficient.

    Args:
        x: Independent variable array
        y: Dependent variable array

    Returns:
        Tuple (amplitude, frequency).
    """
    from scipy.signal import find_peaks

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    y_centered = y - np.mean(y)
    y_range = float(np.ptp(y))
    amplitude = y_range / 2.0
    if np.abs(amplitude) < _MIN_AMPLITUDE:
        amplitude = 1.0

    frequency = 1.0
    x_range = float(np.ptp(x))
    if x_range < _EPS_DENOM:
        # No range in x: cannot estimate period; avoid division by zero below
        logger.debug(
            t('log.estimated_trig_parameters', amplitude=f"{amplitude:.3f}", frequency=f"{frequency:.3f}")
        )
        return amplitude, frequency

    # 1) Try peak-based period
    try:
        min_dist = max(1, len(x) // 10)
        peaks, _ = find_peaks(np.abs(y_centered), distance=min_dist)
        if len(peaks) >= 2:
            peak_distances = np.diff(x[peaks])
            if len(peak_distances) > 0 and np.median(peak_distances) > 0:
                estimated_period = 2.0 * float(np.median(peak_distances))
                if estimated_period > _EPS_DENOM:
                    frequency = 2.0 * np.pi / estimated_period
            else:
                frequency = 2.0 * np.pi / x_range
    except Exception as e:
        logger.warning(t('log.peak_detection_failed', error=str(e)))

    # 2) Fallback: autocorrelation to estimate period
    if frequency <= 0 or frequency > 1e8:
        try:
            n = min(len(y_centered), _MAX_AUTOCORR_LAG)
            acf = np.correlate(y_centered[:n], y_centered[:n], mode='full')
            acf = acf[len(acf) // 2:]
            if len(acf) > 2:
                peaks_acf, _ = find_peaks(acf, distance=max(1, n // 10))
                if len(peaks_acf) >= 2:
                    lag_diff = np.diff(peaks_acf)
                    if len(lag_diff) > 0 and np.median(lag_diff) > 0:
                        dx = float(np.median(np.diff(x))) if len(x) > 1 else x_range / max(1, len(x))
                        period = float(np.median(lag_diff)) * dx
                        if period > _EPS_DENOM:
                            frequency = 2.0 * np.pi / period
            if not (0 < frequency <= 1e8):
                frequency = 2.0 * np.pi / x_range
        except Exception as e:
            logger.warning(t('log.peak_detection_failed', error=str(e)))
            frequency = 2.0 * np.pi / x_range

    frequency = np.clip(float(frequency), 1e-8, 1e8)
    logger.debug(
        t('log.estimated_trig_parameters', amplitude=f"{amplitude:.3f}", frequency=f"{frequency:.3f}")
    )
    return amplitude, frequency


def estimate_phase_shift(x: Any, y: Any, amplitude: float, frequency: float) -> float:
    """
    Estimate initial phase shift for y = a * sin(b*x + c) or y = a * cos(b*x + c).

    Args:
        x: Independent variable array
        y: Dependent variable array
        amplitude: Estimated amplitude (a)
        frequency: Estimated angular frequency (b)

    Returns:
        Estimated phase shift (c).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if np.abs(amplitude) < _MIN_AMPLITUDE:
        return 0.0
    try:
        y_normalized = y / amplitude
        y_normalized = np.clip(y_normalized, -1.0, 1.0)
        first_max_idx = int(np.argmax(y_normalized))
        x_at_max = float(x[first_max_idx])
        # Phase such that at x_at_max the sine is at its max: b*x + c = pi/2
        phase = np.pi / 2.0 - frequency * x_at_max
        phase = float(np.arctan2(np.sin(phase), np.cos(phase)))
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

    Args:
        x: Independent variable array.
        y: Dependent variable array.
        degree: Polynomial degree.

    Returns:
        List of coefficients [c0, c1, ..., c_degree] (constant term first).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) <= degree:
        out = [0.0] * (degree + 1)
        out[0] = float(np.mean(y))
        return out
    coefs = np.polyfit(x, y, degree)
    return list(reversed(coefs))


def estimate_single_power_parameter(x: Any, y: Any, power: int) -> float:
    """
    Estimate coefficient a for y = a * x^power (no constant term).
    Least-squares: a = sum(y * x^power) / sum(x^(2*power)).

    Args:
        x: Independent variable array
        y: Dependent variable array
        power: Exponent (e.g. 2 for quadratic through origin)

    Returns:
        Estimated coefficient a.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xp = x ** power
    denom = np.sum(xp * xp)
    if denom < _EPS_DENOM:
        return 1.0
    return float(np.sum(y * xp) / denom)


def estimate_ln_parameter(x: Any, y: Any) -> float:
    """
    Estimate initial parameter a for y = a * ln(x).
    Least squares with no intercept; positive x only.

    Args:
        x: Independent variable array (positive)
        y: Dependent variable array

    Returns:
        Estimated coefficient a.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ln_x = np.log(x)
    denom = np.sum(ln_x * ln_x)
    if denom < _EPS_DENOM:
        return float(np.mean(y) / (np.mean(ln_x) + _EPS_DENOM))
    return float(np.sum(y * ln_x) / denom)


def estimate_inverse_parameter(x: Any, y: Any, power: int) -> float:
    """
    Estimate coefficient a for y = a / x^power.
    Uses median of (y * x^power) for robustness to outliers.

    Args:
        x: Independent variable array (avoid zeros)
        y: Dependent variable array
        power: Power in denominator (1 or 2)

    Returns:
        Estimated coefficient a.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(np.median(y * (x ** power)))


def estimate_gaussian_parameters(x: Any, y: Any) -> Tuple[float, float, float]:
    """
    Estimate initial (A, mu, sigma) for y = A * exp(-(x-mu)^2 / (2*sigma^2)).
    A from max(y), mu from x at max, sigma from FWHM (half-max crossings).

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
    y_min = float(np.min(y))
    y_range = A_0 - y_min
    if y_range < _EPS_DENOM:
        x_range = float(np.ptp(x))
        return A_0, mu_0, max(x_range / 4.0, 1.0) if x_range > 0 else 1.0

    half_max = y_min + 0.5 * y_range
    above = np.where(y >= half_max)[0]
    if len(above) >= 2:
        # FWHM ≈ 2*sqrt(2*ln(2))*sigma => sigma = FWHM / (2*sqrt(2*ln(2)))
        x_above = x[above]
        width = float(np.max(x_above) - np.min(x_above))
        sigma_0 = width / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    else:
        x_range = float(np.ptp(x))
        sigma_0 = x_range / 4.0 if x_range > 0 else 1.0

    if sigma_0 <= 0:
        sigma_0 = 1.0
    return A_0, mu_0, sigma_0


def estimate_binomial_parameters(x: Any, y: Any) -> Tuple[float, float, float]:
    """
    Estimate (a, b, c) for logistic y = a / (1 + exp(-b*(x-c))).
    a = range, c = midpoint of transition, b from inverse of transition width.

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
    a_0 = (y_max - y_min) if (y_max - y_min) > _EPS_DENOM else 1.0
    mid_level = y_min + 0.5 * (y_max - y_min)
    idx = np.searchsorted(np.sort(y), mid_level)
    if idx <= 0:
        c_0 = float(x[0])
    elif idx >= len(x):
        c_0 = float(x[-1])
    else:
        order = np.argsort(x)
        x_s = x[order]
        y_s = y[order]
        i = np.searchsorted(y_s, mid_level)
        if i <= 0:
            c_0 = float(x_s[0])
        elif i >= len(x_s):
            c_0 = float(x_s[-1])
        else:
            t_val = (mid_level - y_s[i - 1]) / (y_s[i] - y_s[i - 1] + _EPS_DENOM)
            c_0 = float((1.0 - t_val) * x_s[i - 1] + t_val * x_s[i])
    x_range = float(np.ptp(x))
    if x_range < _EPS_DENOM:
        x_range = 1.0
    b_0 = 4.0 / x_range
    return a_0, b_0, c_0


def estimate_exponential_parameters(x: Any, y: Any) -> Tuple[float, float]:
    """
    Estimate (a, b) for y = a * exp(b*x).
    Uses log(y) = log(a) + b*x when y > 0; otherwise fallback from endpoints.

    Args:
        x: Independent variable array
        y: Dependent variable array

    Returns:
        Tuple (a, b).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x_range = float(np.ptp(x))
    if x_range < 1e-12:
        x_range = 1.0
    b_max = 700.0 / x_range

    if np.all(y > 1e-15):
        log_y = np.log(np.maximum(y, 1e-300))
        slope, intercept = np.polyfit(x, log_y, 1)
        b_0 = float(np.clip(slope, -b_max + 0.01, b_max - 0.01))
        a_0 = float(np.exp(intercept))
    else:
        a_0 = float(y[0]) if np.abs(y[0]) > 1e-12 else 1.0
        if np.abs(a_0) < 1e-12:
            a_0 = 1.0
        dx = x[-1] - x[0]
        if np.abs(dx) > 1e-12:
            end_ratio = np.abs(y[-1]) / (np.abs(y[0]) + 1e-300)
            b_0 = float(np.clip(np.log(end_ratio + 1e-12) / dx, -b_max + 0.01, b_max - 0.01))
        else:
            b_0 = 0.0
    return a_0, b_0


def estimate_square_pulse_parameters(x: Any, y: Any) -> Tuple[float, float, float]:
    """
    Estimate (A, t0, w) for a smooth square pulse: amplitude, center time, width.
    A from peak-to-peak, t0 from center of mass of ``y`` (absolute value), w from support of elevated region.

    Args:
        x: Independent variable array (e.g. time)
        y: Dependent variable array

    Returns:
        Tuple (A, t0, w).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    A_0 = float(np.ptp(y)) or 1.0
    idx_max = int(np.argmax(y))
    t0_0 = float(x[idx_max])
    x_range = float(np.ptp(x))
    half = np.min(y) + 0.5 * (np.max(y) - np.min(y))
    above = np.where(y >= half)[0]
    if len(above) >= 2:
        w_0 = float(np.ptp(x[above]))
    else:
        w_0 = x_range / 5.0 if x_range > 0 else 1.0
    if w_0 <= 0:
        w_0 = 1.0
    return A_0, t0_0, w_0
