# fitting.fitting_utils

Utility functions for curve fitting operations.

## Overview

This module provides the core fitting utilities used by all fitting functions in RegressionLab. It abstracts the underlying optimization library (SciPy by default) and provides helper functions for parameter estimation.

## Core Functions

### Fitting Operations

#### `generic_fit(data: Any, x_name: str, y_name: str, fit_func: Callable, param_names: List[str], equation_template: Optional[str], initial_guess: Optional[List[float]] = None, bounds: Optional[Tuple[Sequence[float], Sequence[float]]] = None, equation_formula: Optional[str] = None) -> Tuple[str, NDArray, str, Optional[dict]]`

The main fitting function used by all equation-specific fitters.

Generic curve fitting using `scipy.optimize.curve_fit`. This function handles weighted fitting based on uncertainties, calculates parameter uncertainties, computes R² and additional statistics (RMSE, chi-squared, reduced chi-squared, degrees of freedom, confidence intervals).

Before calling `curve_fit`, `x`, `y`, and their uncertainty arrays are converted to NumPy arrays with `dtype=float` to ensure consistent behavior (e.g., when `data` is a pandas DataFrame). The optimizer uses `maxfev=10000` to allow more iterations and improve convergence for polynomial and nonlinear models.

**Parameters:**
- `data`: Data dictionary or DataFrame containing x, y and their uncertainties
- `x_name`: Name of the x variable, or list of variable names for multidimensional fitting (e.g. `['x_0', 'x_1']`)
- `y_name`: Name of the y variable
- `fit_func`: Function to fit (e.g., `linear_function_with_n`, `sin_function`, etc.)
- `param_names`: List of parameter names (e.g., `['m', 'n']` or `['a', 'b', 'c']`)
- `equation_template`: Template for equation display (e.g., `"y={m}x+{n}"`)
- `initial_guess`: Optional initial parameter values for fitting (improves convergence)
- `bounds`: Optional `(lower_bounds, upper_bounds)` tuple for parameters; avoids overflow in exponentials
- `equation_formula`: Optional original formula string (e.g., `"y = mx + n"`); used for custom fits; predefined fits use EQUATIONS config lookup

**Returns:**
- Tuple containing:
  - `text`: Formatted text with parameters, uncertainties, R², and statistics
  - `y_fitted`: Array with fitted y values
  - `equation`: Formatted equation with parameter values (prefixed with original formula if available)
  - `fit_info`: Optional dict with `fit_func`, `params`, `cov`, `x_names` (for advanced use)

**Raises:**
- `FittingError`: If `curve_fit` fails to converge or data is invalid

**Example:**
```python
from fitting.fitting_utils import generic_fit
from fitting.fitting_functions import linear_function_with_n
import numpy as np

# Create data dictionary
data = {
    'x': np.array([1, 2, 3, 4, 5]),
    'y': np.array([2.5, 5.1, 7.4, 10.2, 12.6]),
    'ux': np.ones(5) * 0.1,
    'uy': np.ones(5) * 0.5
}

text, y_fitted, equation, fit_info = generic_fit(
    data, 'x', 'y',
    fit_func=linear_function_with_n,
    param_names=['m', 'n'],
    equation_template='y={m}x+{n}'
)
print(f"Parameters:\n{text}")
print(f"Equation: {equation}")
# R² is included in the text output
```

#### `get_fitting_function(equation_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Optional[Callable]`

Factory function that returns the appropriate fitting function for a given equation name.

**Parameters:**
- `equation_name`: Name from `config.EQUATIONS` (e.g., 'linear_function_with_n')
- `initial_guess_override`: Optional list of initial values (None = use estimator)
- `bounds_override`: Optional `(lower_list, upper_list)` (None in slot = use estimator)

**Returns:**
- Fitting function that takes `(data, x_name, y_name)` and returns `(text, y_fitted, equation, fit_info)`, or `None` if not found

**Example:**
```python
from fitting.fitting_utils import get_fitting_function

# Get fitting function by name
fit_func = get_fitting_function('linear_function_with_n')

# Use it to fit data (first three values are text, y_fitted, equation)
text, y_fitted, equation, *_ = fit_func(data, 'x', 'y')

# With parameter overrides
fit_func_with_overrides = get_fitting_function(
    'linear_function_with_n',
    initial_guess_override=[1.0, 2.0],  # Override [n, m]
    bounds_override=([0.0, 0.0], [10.0, 10.0])  # Bounds for [n, m]
)
text, y_fitted, equation, *_ = fit_func_with_overrides(data, 'x', 'y')
```

## Helper Functions

### Parameter Formatting

#### `format_parameter(value: float, sigma: float) -> Tuple[float, str]`

Format a parameter value and its uncertainty using scientific notation.

**Parameters:**
- `value`: Parameter value
- `sigma`: Uncertainty in the parameter

**Returns:**
- Tuple of `(rounded_value, sigma_str)` where `sigma_str` is in scientific notation

#### `get_equation_param_info(equation_name: str) -> Optional[Tuple[List[str], str]]`

Get parameter names and display formula for a given equation type.

**Parameters:**
- `equation_name`: Identifier of the equation (e.g., `'linear_function_with_n'` or `'gaussian_function'`)

**Returns:**
- Tuple `(param_names, formula_str)` where `param_names` is a list of parameter names in order and `formula_str` is a human-readable equation, or `None` if the equation is unknown

**Example:**
```python
from fitting.fitting_utils import get_equation_param_info

names, formula = get_equation_param_info("linear_function_with_n")
# names: ['n', 'm']
# formula: 'y = mx + n'
```

#### `get_equation_format_for_function(function_name: str) -> Optional[str]`

Return the format template (with placeholders) for the given fit function name.

**Parameters:**
- `function_name`: Name of the fitting function (e.g., `'fit_linear_function_with_n'`)

**Returns:**
- Format string (e.g., `'y={m}x+{n}'`) or `None` if not found

#### `get_equation_param_names_for_function(function_name: str) -> List[str]`

Return the parameter names for the given fit function from equations config.

**Parameters:**
- `function_name`: Name of the fitting function (e.g., `'fit_linear_function_with_n'`)

**Returns:**
- List of parameter names in the order expected by the fit function

**Raises:**
- `FittingError`: If no equation config is found or param_names is missing

#### `merge_initial_guess(computed: List[float], override: Optional[List[Optional[float]]]) -> List[float]`

Merge automatically computed initial guesses with user overrides.

**Parameters:**
- `computed`: List of automatically estimated parameter values
- `override`: Optional list of user-provided overrides (same length as `computed`); `None` entries mean "keep computed"

**Returns:**
- New list with the effective initial guess for each parameter

#### `merge_bounds(computed_bounds: Optional[Tuple[Sequence[float], Sequence[float]]], override_lower: Optional[List[Optional[float]]], override_upper: Optional[List[Optional[float]]], n_params: int) -> Optional[Tuple[Tuple[float, ...], Tuple[float, ...]]]`

Merge automatically computed parameter bounds with user overrides.

**Parameters:**
- `computed_bounds`: Optional pair of sequences with base lower and upper bounds, or `None`
- `override_lower`: Optional list of lower bound overrides
- `override_upper`: Optional list of upper bound overrides
- `n_params`: Total number of parameters in the model

**Returns:**
- Tuple `(lower_bounds, upper_bounds)` as tuples of floats, or `computed_bounds` unchanged if no overrides are provided

### Parameter Estimation

Parameter estimation functions are available from the `fitting.estimators` module (also exported from `fitting` package). These functions provide initial guesses for fitting algorithms.

See [fitting.estimators](estimators.md) for complete documentation of all available estimation functions, including:

- `estimate_trigonometric_parameters(x, y)` - Estimates amplitude and frequency for sin/cos
- `estimate_phase_shift(x, y, amplitude, frequency)` - Estimates phase shift
- `estimate_hyperbolic_parameters(x, y)` - Estimates amplitude and frequency for sinh/cosh
- `estimate_hyperbolic_bounds(x)` - Returns bounds for hyperbolic fits to avoid overflow
- `estimate_linear_parameters(x, y)` - Estimates slope and intercept for linear functions
- `estimate_polynomial_parameters(x, y, degree)` - Estimates coefficients for polynomial functions
- `estimate_gaussian_parameters(x, y)` - Estimates amplitude, center, and width for Gaussian functions
- `estimate_exponential_parameters(x, y)` - Estimates parameters for exponential functions
- And more...

**Example:**
```python
from fitting import estimate_trigonometric_parameters

# Estimate initial parameters
amplitude, frequency = estimate_trigonometric_parameters(x_data, y_data)
```

## Statistical Functions

### Statistics Calculation

The function calculates several statistics that are included in the text output:

**R² (Coefficient of Determination):**
```python
r_squared = 1 - (SS_res / SS_tot)

where:
    SS_res = Σ(y - y_fitted)²  # Residual sum of squares
    SS_tot = Σ(y - ȳ)²         # Total sum of squares
```

**RMSE (Root Mean Square Error):**
```python
rmse = sqrt(mean((y - y_fitted)²))
```

**Chi-squared Statistics:**
```python
chi_squared = Σ((y - y_fitted) / uy)²
reduced_chi_squared = chi_squared / dof
```

**Confidence Intervals:**
95% confidence intervals for each parameter using t-distribution.

**Interpretation:**
- R² = 1.0: Perfect fit
- R² > 0.95: Excellent fit
- R² > 0.85: Good fit
- R² > 0.70: Acceptable fit
- R² < 0.70: Poor fit

### Weighted Fitting

When uncertainties are provided in the data dictionary:

```python
# Data dictionary includes uncertainties
data = {
    'x': x_array,
    'y': y_array,
    'ux': x_uncertainties,  # Optional
    'uy': y_uncertainties   # Used as weights
}

# generic_fit automatically extracts and uses uy as sigma
# SciPy curve_fit uses these as sigma
popt, pcov = curve_fit(fit_func, x, y, sigma=uy, absolute_sigma=True)
```

This gives more weight to data points with smaller uncertainties, which is statistically correct for experimental data.

## Advanced Usage

### Custom Initial Guesses

For complex functions, providing good initial guesses improves convergence:

```python
# Example: Gaussian function
def fit_gaussian_with_guess(data, x_name, y_name):
    x = data[x_name]
    y = data[y_name]
    
    # Estimate initial parameters
    a0 = np.max(y)                    # Amplitude
    mu0 = x[np.argmax(y)]             # Center
    sigma0 = (np.max(x) - np.min(x)) / 4  # Width
    
    initial_guess = [a0, mu0, sigma0]
    
    text, y_fitted, equation, *_ = generic_fit(
        data, x_name, y_name,
        fit_func=gaussian_function,
        param_names=['a', 'mu', 'sigma'],
        equation_template='y={a}*exp(-((x-{mu})/{sigma})^2)',
        initial_guess=initial_guess
    )
    ...
```

### Replacing the Backend

To use a different optimization library, modify `generic_fit()`:

```python
def generic_fit_custom(data, x_name, y_name, fit_func, param_names, equation_template, initial_guess=None):
    """Custom fitting using alternative library."""
    # Import your preferred library
    from alternative_lib import fit_function
    
    # Extract data
    x = data[x_name]
    y = data[y_name]
    uy = data.get(f'u{y_name}', None)
    
    # Perform fit
    result = fit_function(fit_func, x, y, weights=uy, initial=initial_guess)
    
    # Extract results
    params = result.parameters
    y_fitted = fit_func(x, *params)
    r_squared = calculate_r_squared(y, y_fitted)
    
    # Format output (similar to original generic_fit)
    text = format_parameters(param_names, params, result.uncertainties)
    equation = equation_template.format(**dict(zip(param_names, params)))
    
    return text, y_fitted, equation
```

See [Customizing the Fitting Core](../customization.md) for details.

## Error Handling

The fitting utilities raise specific exceptions:

```python
from utils.exceptions import FittingError
from fitting.fitting_utils import generic_fit
from fitting.fitting_functions import linear_function_with_n

try:
    text, y_fitted, equation, *_ = generic_fit(
        data, 'x', 'y',
        fit_func=linear_function_with_n,
        param_names=['m', 'n'],
        equation_template='y={m}x+{n}'
    )
except FittingError as e:
    print(f"Fitting failed: {e}")
    # Handle error (try different equation, initial guess, etc.)
```

Common causes of fitting failures:
- Insufficient data points
- Poor initial guess
- Wrong equation for data
- Numerical issues (infinity, NaN values)

---

*For more details, see source code: `src/fitting/fitting_utils.py`*
