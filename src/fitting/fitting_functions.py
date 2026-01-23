"""
Fitting functions and operations for curve fitting.

This module provides:
1. Mathematical functions commonly used for curve fitting (func_lineal, func_sin, etc.)
2. High-level fitting wrapper functions (ajlineal, ajsin, etc.) that perform the actual curve fitting
3. Factory functions to generate custom fitting functions dynamically
"""

import numpy as np
from numpy.typing import NDArray
from typing import Union, Tuple

from fitting.fitting_utils import generic_fit, estimate_trigonometric_parameters, estimate_phase_shift


# Type alias for numeric inputs that can be scalars or arrays
Numeric = Union[float, NDArray[np.floating]]


def generate_polynomial_function(parameters: list[bool]):
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
        def polynomial(t: Numeric, c0: float, c1: float, c2: float, c3: float, c4: float) -> Numeric:
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


def generate_trigonometric_function(func_type: str, with_phase: bool = False):
    """
    Generate a trigonometric function dynamically based on the function type.
    
    Args:
        func_type: Type of function ('sin', 'cos', 'sinh', 'cosh')
        with_phase: Whether to include a phase shift parameter c
    
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

def generate_inverse_function(power: int):
    """
    Generate an inverse power function dynamically based on the power.
    
    Args:
        power: The power of t in the denominator (e.g., 1 for 1/t, 2 for 1/t^2)
    
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


# ============================================================================
# Fitting wrapper functions
# ============================================================================


def fit_linear_function_with_n(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Linear fit: y = mx + n
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=linear_function_with_n,
        param_names=['m', 'n'],
        equation_template='y={m}x+{n}'
    )


def fit_linear_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Linear fit through origin: y = mx
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=linear_function,
        param_names=['m'],
        equation_template='y={m}x'
    )


def fit_quadratic_function_complete(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Quadratic fit: y = ax^2 + bx + c
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=quadratic_function_complete,
        param_names=['a', 'b', 'c'],
        equation_template='y={c}x^2+{b}x+{a}'
    )


def fit_quadratic_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Quadratic fit through origin: y = ax^2
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=quadratic_function,
        param_names=['a'],
        equation_template='y={a}x^2'
    )


def fit_fourth_power(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Quartic fit through origin: y = ax^4
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=fourth_power,
        param_names=['a'],
        equation_template='y={a}x^4'
    )

    
def fit_sin_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Sine fit: y = a sin(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
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


def fit_sin_function_with_c(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Sine fit with phase: y = a sin(bx + c)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
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


def fit_cos_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Cosine fit: y = a cos(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
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


def fit_cos_function_with_c(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Cosine fit with phase: y = a cos(bx + c)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
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


def fit_sinh_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Hyperbolic sine fit: y = a sinh(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    # Estimate initial parameters for better convergence
    x = data[x_name]
    y = data[y_name]
    
    # For sinh, estimate amplitude from range
    y_range = np.max(y) - np.min(y)
    amplitude = y_range / 2.0 if y_range > 0 else 1.0
    
    # For hyperbolic functions, b should be small (starts slow, grows fast)
    x_range = np.max(x) - np.min(x)
    frequency = 1.0 / x_range if x_range > 0 else 1.0
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=sinh_function,
        param_names=['a', 'b'],
        equation_template='y={a} sinh({b}x)',
        initial_guess=[amplitude, frequency]
    )


def fit_cosh_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Hyperbolic cosine fit: y = a cosh(bx)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    # Estimate initial parameters for better convergence
    x = data[x_name]
    y = data[y_name]
    
    # For cosh, minimum value gives us info about amplitude
    y_min = np.min(y)
    y_max = np.max(y)
    amplitude = (y_max - y_min) / 2.0 if (y_max - y_min) > 0 else 1.0
    
    # For hyperbolic functions, b should be small
    x_range = np.max(x) - np.min(x)
    frequency = 1.0 / x_range if x_range > 0 else 1.0
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=cosh_function,
        param_names=['a', 'b'],
        equation_template='y={a} cosh({b}x)',
        initial_guess=[amplitude, frequency]
    )


def fit_ln_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Logarithmic fit: y = a ln(x)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=ln_function,
        param_names=['a'],
        equation_template='y={a} ln(x)'
    )


def fit_inverse_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Inverse fit: y = a/x
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=inverse_function,
        param_names=['a'],
        equation_template='y={a}/x'
    )


def fit_inverse_square_function(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Inverse quadratic fit: y = a/x^2
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=inverse_square_function,
        param_names=['a'],
        equation_template='y={a}/x^2'
    )
