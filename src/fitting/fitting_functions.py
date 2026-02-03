"""
Fitting functions and operations for curve fitting.

This module provides:

    1. Mathematical functions for curve fitting (func_lineal, func_sin, etc.)
    2. High-level fitting wrappers (ajlineal, ajsin, etc.) that perform curve fitting
    3. Factory functions to generate custom fitting functions dynamically
"""

# Standard library
from typing import Callable, Tuple, Union

# Third-party packages
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.special import eval_hermite

# Local imports
from fitting.estimators import (
    estimate_binomial_parameters,
    estimate_gaussian_parameters,
    estimate_inverse_parameter,
    estimate_linear_parameters,
    estimate_ln_parameter,
    estimate_phase_shift,
    estimate_polynomial_parameters,
    estimate_single_power_parameter,
    estimate_trigonometric_parameters,
)
from fitting.fitting_utils import generic_fit


# Type alias for numeric inputs that can be scalars or arrays
Numeric = Union[float, NDArray[np.floating]]

# Type alias for data accepted by fit functions (DataFrame is dict-like for column access)
DataLike = Union[dict, pd.DataFrame]


def generate_polynomial_function(parameters: list[bool]) -> Callable:
    """
    Generate a polynomial function dynamically based on which parameters are enabled.
    
    Args:
        parameters: List of booleans indicating which polynomial terms to include.
                   Index i corresponds to the coefficient of t^i.
    
    Returns:
        A function that takes t and the enabled coefficients as arguments.
    """
    # Get indices of enabled parameters
    enabled_indices = [i for i, enabled in enumerate(parameters) if enabled]
    num_params = len(enabled_indices)
    
    if num_params == 0:
        # If no parameters are enabled, return a constant zero function
        def polynomial(t: Numeric) -> Numeric:
            return np.zeros_like(t) if isinstance(t, np.ndarray) else 0.0
        return polynomial
    
    # Generate function with explicit parameters based on number needed
    if num_params == 1:
        def polynomial(t: Numeric, c0: float) -> Numeric:
            """Polynomial with 1 coefficient"""
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
            """Polynomial with 2 coefficients"""
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
            """Polynomial with 3 coefficients"""
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
            """Polynomial with 4 coefficients"""
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
            """Polynomial with 5 coefficients"""
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

# Linear function with y-intercept: y = m*t + n
linear_function_with_n = generate_polynomial_function([True, True])  # t^0 and t^1

# Linear function through origin: y = m*t
linear_function = generate_polynomial_function([False, True])  # only t^1

# Quadratic function: y = a + b*t + c*t^2
quadratic_function_complete = generate_polynomial_function([True, True, True])  # t^0, t^1, and t^2

# Quadratic function through origin: y = a*t^2
quadratic_function = generate_polynomial_function([False, False, True])  # only t^2

# Fourth power function: y = a*t^4
fourth_power = generate_polynomial_function([False, False, False, False, True])  # only t^4


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
    # Map function types to numpy functions
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
            """
            Trigonometric function with phase shift: y = a*func(b*t + c)
            
            Args:
                t: Independent variable (scalar or array)
                a: Amplitude coefficient
                b: Frequency coefficient
                c: Phase shift
            
            Returns:
                Evaluated trigonometric value(s)
            """
            return a * np_func(b * t + c)
    else:
        def trig_func(t: Numeric, a: float, b: float) -> Numeric:
            """
            Trigonometric function: y = a*func(b*t)
            
            Args:
                t: Independent variable (scalar or array)
                a: Amplitude coefficient
                b: Frequency coefficient
            
            Returns:
                Evaluated trigonometric value(s)
            """
            return a * np_func(b * t)
    
    return trig_func


# Sine function: y = a*sin(b*t)
sin_function = generate_trigonometric_function('sin', with_phase=False)

# Sine function with phase shift: y = a*sin(b*t + c)
sin_function_with_c = generate_trigonometric_function('sin', with_phase=True)

# Cosine function: y = a*cos(b*t)
cos_function = generate_trigonometric_function('cos', with_phase=False)

# Cosine function with phase shift: y = a*cos(b*t + c)
cos_function_with_c = generate_trigonometric_function('cos', with_phase=True)

# Hyperbolic sine function: y = a*sinh(b*t)
sinh_function = generate_trigonometric_function('sinh', with_phase=False)

# Hyperbolic cosine function: y = a*cosh(b*t)
cosh_function = generate_trigonometric_function('cosh', with_phase=False)


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
        """
        Inverse power function: y = a/t^power
        
        Args:
            t: Independent variable (scalar or array)
            a: Coefficient
        
        Returns:
            Evaluated inverse power value(s)
        """
        return a / (t**power)
    
    return inverse_func


# Inverse function: y = a/t
inverse_function = generate_inverse_function(1)

# Inverse square function: y = a/t^2
inverse_square_function = generate_inverse_function(2)


# ----------------------------------------------------------------------------
# Gaussian, exponential, binomial (logistic), tangent, square pulse, Hermite
# ----------------------------------------------------------------------------


def gaussian_function(t: Numeric, A: float, mu: float, sigma: float) -> Numeric:
    """Gaussian (normal) function: y = A * exp(-(t-mu)^2 / (2*sigma^2))"""
    return A * np.exp(-((t - mu) ** 2) / (2.0 * sigma**2))


def exponential_function(t: Numeric, a: float, b: float) -> Numeric:
    """Exponential function: y = a * exp(b*t)"""
    return a * np.exp(b * t)


def binomial_function(t: Numeric, a: float, b: float, c: float) -> Numeric:
    """Logistic (S-shaped, binomial-type) function: y = a / (1 + exp(-b*(t-c)))"""
    return a / (1.0 + np.exp(-b * (t - c)))


def tan_function(t: Numeric, a: float, b: float) -> Numeric:
    """Tangent function: y = a * tan(b*t)"""
    return a * np.tan(b * t)


def tan_function_with_c(t: Numeric, a: float, b: float, c: float) -> Numeric:
    """Tangent function with phase: y = a * tan(b*t + c)"""
    return a * np.tan(b * t + c)


def square_pulse_function(t: Numeric, A: float, t0: float, w: float) -> Numeric:
    """
    Smooth square pulse (approximation): y = A * (f(t - (t0-w/2)) - f(t - (t0+w/2)))/2
    with f(s) = tanh(k*s), k=50, so the pulse is centered at t0 with width w.
    """
    k = 50.0
    return A * 0.5 * (np.tanh(k * (t - (t0 - w / 2.0))) - np.tanh(k * (t - (t0 + w / 2.0))))


def hermite_polynomial_3(t: Numeric, c0: float, c1: float, c2: float, c3: float) -> Numeric:
    """
    Sum of physicist's Hermite polynomials up to degree 3:
    y = c0*H_0(t) + c1*H_1(t) + c2*H_2(t) + c3*H_3(t)
    """
    out = c0 * eval_hermite(0, t) + c1 * eval_hermite(1, t)
    out = out + c2 * eval_hermite(2, t) + c3 * eval_hermite(3, t)
    return out


def hermite_polynomial_4(
    t: Numeric, c0: float, c1: float, c2: float, c3: float, c4: float
) -> Numeric:
    """
    Sum of physicist's Hermite polynomials up to degree 4:
    y = c0*H_0(t) + ... + c4*H_4(t)
    """
    out = hermite_polynomial_3(t, c0, c1, c2, c3) + c4 * eval_hermite(4, t)
    return out


# ============================================================================
# Fitting wrapper functions
# ============================================================================


def fit_linear_function_with_n(
    data: DataLike, x_name: str, y_name: str
) -> Tuple[str, NDArray, str]:
    """Linear fit: y = mx + n
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    n_0, m_0 = estimate_linear_parameters(x, y)
    return generic_fit(
        data, x_name, y_name,
        fit_func=linear_function_with_n,
        param_names=['n', 'm'],
        equation_template='y={m}x+{n}',
        initial_guess=[n_0, m_0]
    )


def fit_linear_function(
    data: DataLike, x_name: str, y_name: str
) -> Tuple[str, NDArray, str]:
    """Linear fit through origin: y = mx
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    m_0 = estimate_single_power_parameter(x, y, 1)
    return generic_fit(
        data, x_name, y_name,
        fit_func=linear_function,
        param_names=['m'],
        equation_template='y={m}x',
        initial_guess=[m_0]
    )


def fit_quadratic_function_complete(
    data: DataLike, x_name: str, y_name: str
) -> Tuple[str, NDArray, str]:
    """Quadratic fit: y = ax^2 + bx + c
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    initial_guess = estimate_polynomial_parameters(x, y, 2)
    return generic_fit(
        data, x_name, y_name,
        fit_func=quadratic_function_complete,
        param_names=['a', 'b', 'c'],
        equation_template='y={c}x^2+{b}x+{a}',
        initial_guess=initial_guess
    )


def fit_quadratic_function(
    data: DataLike, x_name: str, y_name: str
) -> Tuple[str, NDArray, str]:
    """Quadratic fit through origin: y = ax^2
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_single_power_parameter(x, y, 2)
    return generic_fit(
        data, x_name, y_name,
        fit_func=quadratic_function,
        param_names=['a'],
        equation_template='y={a}x^2',
        initial_guess=[a_0]
    )


def fit_fourth_power(
    data: DataLike, x_name: str, y_name: str
) -> Tuple[str, NDArray, str]:
    """Quartic fit through origin: y = ax^4
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_single_power_parameter(x, y, 4)
    return generic_fit(
        data, x_name, y_name,
        fit_func=fourth_power,
        param_names=['a'],
        equation_template='y={a}x^4',
        initial_guess=[a_0]
    )

    
def fit_sin_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Sine fit: y = a sin(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    # Estimate initial parameters for better convergence
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=sin_function,
        param_names=['a', 'b'],
        equation_template='y={a} sin({b}x)',
        initial_guess=[amplitude, frequency]
    )


def fit_sin_function_with_c(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Sine fit with phase: y = a sin(bx + c)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    # Estimate initial parameters for better convergence
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    phase = estimate_phase_shift(x, y, amplitude, frequency)
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=sin_function_with_c,
        param_names=['a', 'b', 'c'],
        equation_template='y={a} sin({b}x+{c})',
        initial_guess=[amplitude, frequency, phase]
    )


def fit_cos_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Cosine fit: y = a cos(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    # Estimate initial parameters for better convergence
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=cos_function,
        param_names=['a', 'b'],
        equation_template='y={a} cos({b}x)',
        initial_guess=[amplitude, frequency]
    )


def fit_cos_function_with_c(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Cosine fit with phase: y = a cos(bx + c)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    # Estimate initial parameters for better convergence
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    phase = estimate_phase_shift(x, y, amplitude, frequency)
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=cos_function_with_c,
        param_names=['a', 'b', 'c'],
        equation_template='y={a} cos({b}x+{c})',
        initial_guess=[amplitude, frequency, phase]
    )


def fit_sinh_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Hyperbolic sine fit: y = a sinh(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    y_range = np.max(y) - np.min(y)
    amplitude = y_range / 2.0 if y_range > 0 else 1.0
    x_range = float(np.ptp(x))
    frequency = 1.0 / x_range if x_range > 1e-30 else 1.0
    # Limit b to avoid overflow: sinh(b*x) grows fast; keep b*x_max < ~700
    b_max = 700.0 / (np.max(np.abs(x)) + 1e-30)
    bounds = ([-np.inf, 1e-9], [np.inf, min(b_max, 1e3)])
    return generic_fit(
        data, x_name, y_name,
        fit_func=sinh_function,
        param_names=['a', 'b'],
        equation_template='y={a} sinh({b}x)',
        initial_guess=[amplitude, frequency],
        bounds=bounds
    )


def fit_cosh_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Hyperbolic cosine fit: y = a cosh(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    y_min = np.min(y)
    y_max = np.max(y)
    amplitude = (y_max - y_min) / 2.0 if (y_max - y_min) > 0 else 1.0
    x_range = float(np.ptp(x))
    frequency = 1.0 / x_range if x_range > 1e-30 else 1.0
    b_max = 700.0 / (np.max(np.abs(x)) + 1e-30)
    bounds = ([-np.inf, 1e-9], [np.inf, min(b_max, 1e3)])
    return generic_fit(
        data, x_name, y_name,
        fit_func=cosh_function,
        param_names=['a', 'b'],
        equation_template='y={a} cosh({b}x)',
        initial_guess=[amplitude, frequency],
        bounds=bounds
    )


def fit_ln_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Logarithmic fit: y = a ln(x)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_ln_parameter(x, y)
    return generic_fit(
        data, x_name, y_name,
        fit_func=ln_function,
        param_names=['a'],
        equation_template='y={a} ln(x)',
        initial_guess=[a_0]
    )


def fit_inverse_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Inverse fit: y = a/x
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_inverse_parameter(x, y, 1)
    return generic_fit(
        data, x_name, y_name,
        fit_func=inverse_function,
        param_names=['a'],
        equation_template='y={a}/x',
        initial_guess=[a_0]
    )


def fit_inverse_square_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Inverse quadratic fit: y = a/x^2
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    a_0 = estimate_inverse_parameter(x, y, 2)
    return generic_fit(
        data, x_name, y_name,
        fit_func=inverse_square_function,
        param_names=['a'],
        equation_template='y={a}/x^2',
        initial_guess=[a_0]
    )


def fit_gaussian_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Gaussian fit: y = A * exp(-(x-mu)^2 / (2*sigma^2))
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    A_0, mu_0, sigma_0 = estimate_gaussian_parameters(x, y)
    # Bounds: A > 0 (peak height), sigma > 0 (width)
    bounds = ([0.0, -np.inf, 1e-9], [np.inf, np.inf, np.inf])
    return generic_fit(
        data, x_name, y_name,
        fit_func=gaussian_function,
        param_names=['A', 'mu', 'sigma'],
        equation_template='y={A} exp(-(x-{mu})^2/(2*{sigma}^2))',
        initial_guess=[A_0, mu_0, sigma_0],
        bounds=bounds
    )


def fit_exponential_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Exponential fit: y = a * exp(b*x)
    
    Uses linear regression on log(y) for initial guess when y > 0, and bounds
    on b to avoid exp(b*x) overflow. Returns (text, y_fitted, equation).
    """
    x = np.asarray(data[x_name], dtype=float)
    y = np.asarray(data[y_name], dtype=float)
    x_range = float(np.ptp(x))
    if x_range < 1e-12:
        x_range = 1.0
    # Limit |b| so that exp(b * x_range) does not overflow (~exp(700))
    b_max = 700.0 / x_range
    bounds = ([-np.inf, -b_max], [np.inf, b_max])

    # Robust initial guess: log(y) = log(a) + b*x => linear regression when y > 0
    y_min = float(np.min(y))
    if np.all(y > 1e-15):
        log_y = np.log(y)
        # np.polyfit(x, log_y, 1) => [b, log(a)] so a = exp(log(a))
        slope, intercept = np.polyfit(x, log_y, 1)
        b_0 = float(slope)
        a_0 = float(np.exp(intercept))
        # Clamp b_0 to bounds to avoid bad starting point
        b_0 = np.clip(b_0, -b_max + 0.01, b_max - 0.01)
    else:
        a_0 = float(y[0]) if np.abs(y[0]) > 1e-12 else 1.0
        b_0 = 0.0 if np.abs(a_0) < 1e-12 else np.clip(
            np.log(np.abs(y[-1]) / np.abs(y[0]) + 1e-12) / (x[-1] - x[0] + 1e-12),
            -b_max + 0.01, b_max - 0.01
        )

    return generic_fit(
        data, x_name, y_name,
        fit_func=exponential_function,
        param_names=['a', 'b'],
        equation_template='y={a} exp({b}x)',
        initial_guess=[a_0, b_0],
        bounds=bounds
    )


def fit_binomial_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Logistic (binomial-type) fit: y = a / (1 + exp(-b*(x-c)))
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    a_0, b_0, c_0 = estimate_binomial_parameters(x, y)
    # Bounds: a > 0 (saturation range), b > 0 (steepness)
    bounds = ([1e-9, 1e-9, -np.inf], [np.inf, np.inf, np.inf])
    return generic_fit(
        data, x_name, y_name,
        fit_func=binomial_function,
        param_names=['a', 'b', 'c'],
        equation_template='y={a}/(1+exp(-{b}(x-{c})))',
        initial_guess=[a_0, b_0, c_0],
        bounds=bounds
    )


def fit_tan_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Tangent fit: y = a * tan(b*x)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    return generic_fit(
        data, x_name, y_name,
        fit_func=tan_function,
        param_names=['a', 'b'],
        equation_template='y={a} tan({b}x)',
        initial_guess=[amplitude, frequency]
    )


def fit_tan_function_with_c(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Tangent fit with phase: y = a * tan(b*x + c)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    amplitude, frequency = estimate_trigonometric_parameters(x, y)
    phase = estimate_phase_shift(x, y, amplitude, frequency)
    return generic_fit(
        data, x_name, y_name,
        fit_func=tan_function_with_c,
        param_names=['a', 'b', 'c'],
        equation_template='y={a} tan({b}x+{c})',
        initial_guess=[amplitude, frequency, phase]
    )


def fit_square_pulse_function(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Smooth square pulse fit: amplitude A, center t0, width w.
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    A_0 = float(np.max(y) - np.min(y)) or 1.0
    t0_0 = float(x[np.argmax(y)])
    x_range = float(np.ptp(x))
    w_0 = x_range / 5.0 if x_range > 0 else 1.0
    # Bounds: A > 0, w > 0; t0 within data range with margin
    x_min, x_max = float(np.min(x)), float(np.max(x))
    bounds = ([1e-9, x_min - x_range, 1e-9], [np.inf, x_max + x_range, x_range * 2])
    return generic_fit(
        data, x_name, y_name,
        fit_func=square_pulse_function,
        param_names=['A', 't0', 'w'],
        equation_template='y=pulso(A={A}, t0={t0}, w={w})',
        initial_guess=[A_0, t0_0, w_0],
        bounds=bounds
    )


def fit_hermite_polynomial_3(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Hermite polynomial fit (degree 0..3): y = c0*H_0(x) + c1*H_1(x) + c2*H_2(x) + c3*H_3(x)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    # H_0(x)=1; start with mean as constant term and zeros for higher orders
    y_mean = float(np.mean(y))
    initial_guess = [y_mean, 0.0, 0.0, 0.0]
    return generic_fit(
        data, x_name, y_name,
        fit_func=hermite_polynomial_3,
        param_names=['c0', 'c1', 'c2', 'c3'],
        equation_template='y={c0}*H_0(x)+{c1}*H_1(x)+{c2}*H_2(x)+{c3}*H_3(x)',
        initial_guess=initial_guess
    )


def fit_hermite_polynomial_4(data: DataLike, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
    """Hermite polynomial fit (degree 0..4): y = c0*H_0(x) + ... + c4*H_4(x)
    
    Returns:
        Tuple of (text, y_fitted, equation)
    """
    x = data[x_name]
    y = data[y_name]
    y_mean = float(np.mean(y))
    initial_guess = [y_mean, 0.0, 0.0, 0.0, 0.0]
    return generic_fit(
        data, x_name, y_name,
        fit_func=hermite_polynomial_4,
        param_names=['c0', 'c1', 'c2', 'c3', 'c4'],
        equation_template='y={c0}*H_0(x)+{c1}*H_1(x)+{c2}*H_2(x)+{c3}*H_3(x)+{c4}*H_4(x)',
        initial_guess=initial_guess
    )
