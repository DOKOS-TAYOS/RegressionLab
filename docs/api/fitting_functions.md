# fitting.fitting_functions

Mathematical functions and curve fitting implementations for RegressionLab.

## Overview

The `fitting.fitting_functions` package re-exports all mathematical and fitting functions from `fitting.functions`. The implementations live in submodules under `src/fitting/functions/`:

- **`fitting/functions/polynomials.py`** – Linear, quadratic, fourth power
- **`fitting/functions/trigonometric.py`** – Sin, cos, sinh, cosh, tan (with/without phase)
- **`fitting/functions/inverse.py`** – ln, inverse, inverse square
- **`fitting/functions/special.py`** – Gaussian, exponential, binomial, square pulse, Hermite

Imports remain unchanged: `from fitting.fitting_functions import linear_function, fit_linear_function_with_n`, etc.

The package provides two types of functions:

1. **Mathematical functions** (`*_function`): Pure mathematical functions that calculate y from x and parameters
2. **Fitting functions** (`fit_*`): Wrapper functions that perform curve fitting and return results

All fitting functions use `generic_fit()` from `fitting_utils`, which wraps `scipy.optimize.curve_fit` to provide weighted fitting, uncertainty estimation, and R² calculation.

## Mathematical Functions

Mathematical functions are pure functions that evaluate the mathematical formula given input values and parameters. They are used internally by the fitting functions.

### Linear Functions

#### `linear_function(t: Numeric, m: float) -> Numeric`

Linear function passing through origin: y = mx

**Parameters:**
- `t`: Independent variable (scalar or array)
- `m`: Slope parameter

**Returns:**
- Calculated y values (same type as input t)

**Example:**
```python
from fitting.fitting_functions import linear_function
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = linear_function(x, 2.5)  # y = 2.5 * x
# Result: [2.5, 5.0, 7.5, 10.0, 12.5]
```

#### `linear_function_with_n(t: Numeric, m: float, n: float) -> Numeric`

Linear function with intercept: y = mx + n

**Parameters:**
- `t`: Independent variable (scalar or array)
- `m`: Slope parameter
- `n`: Y-intercept parameter

**Returns:**
- Calculated y values (same type as input t)

**Example:**
```python
from fitting.fitting_functions import linear_function_with_n

x = np.array([0, 1, 2, 3])
y = linear_function_with_n(x, 2.0, 1.5)  # y = 2.0*x + 1.5
# Result: [1.5, 3.5, 5.5, 7.5]
```

### Polynomial Functions

#### `quadratic_function(t: Numeric, a: float) -> Numeric`

Quadratic function: y = ax²

**Parameters:**
- `t`: Independent variable
- `a`: Quadratic coefficient

**Returns:**
- Calculated y values

#### `quadratic_function_complete(t: Numeric, a: float, b: float, c: float) -> Numeric`

Complete quadratic function: `y = c x² + b x + a`

**Parameters:**
- `t`: Independent variable
- `a`: Constant term
- `b`: Linear coefficient
- `c`: Quadratic coefficient

**Returns:**
- Calculated y values

#### `fourth_power(t: Numeric, a: float) -> Numeric`

Fourth power function: y = ax⁴

**Parameters:**
- `t`: Independent variable
- `a`: Coefficient

**Returns:**
- Calculated y values

### Trigonometric Functions

#### `sin_function(t: Numeric, a: float, b: float) -> Numeric`

Sine function: y = a·sin(bx)

**Parameters:**
- `t`: Independent variable
- `a`: Amplitude
- `b`: Angular frequency

**Returns:**
- Calculated y values

#### `sin_function_with_c(t: Numeric, a: float, b: float, c: float) -> Numeric`

Sine function with phase shift: y = a·sin(bx + c)

**Parameters:**
- `t`: Independent variable
- `a`: Amplitude
- `b`: Angular frequency
- `c`: Phase shift

**Returns:**
- Calculated y values

#### `cos_function(t: Numeric, a: float, b: float) -> Numeric`

Cosine function: y = a·cos(bx)

**Parameters:**
- `t`: Independent variable
- `a`: Amplitude
- `b`: Angular frequency

**Returns:**
- Calculated y values

#### `cos_function_with_c(t: Numeric, a: float, b: float, c: float) -> Numeric`

Cosine function with phase shift: y = a·cos(bx + c)

**Parameters:**
- `t`: Independent variable
- `a`: Amplitude
- `b`: Angular frequency
- `c`: Phase shift

**Returns:**
- Calculated y values

### Hyperbolic Functions

#### `sinh_function(t: Numeric, a: float, b: float) -> Numeric`

Hyperbolic sine function: y = a·sinh(bx)

**Parameters:**
- `t`: Independent variable
- `a`: Amplitude
- `b`: Scaling factor

**Returns:**
- Calculated y values

#### `cosh_function(t: Numeric, a: float, b: float) -> Numeric`

Hyperbolic cosine function: y = a·cosh(bx)

**Parameters:**
- `t`: Independent variable
- `a`: Amplitude
- `b`: Scaling factor

**Returns:**
- Calculated y values

### Logarithmic and Inverse Functions

#### `ln_function(t: Numeric, a: float) -> Numeric`

Natural logarithm function: y = a·ln(x)

**Parameters:**
- `t`: Independent variable (must be positive)
- `a`: Coefficient

**Returns:**
- Calculated y values

**Note:** Input values must be positive (x > 0)

#### `inverse_function(t: Numeric, a: float) -> Numeric`

Inverse function: y = a/x

**Parameters:**
- `t`: Independent variable (must be non-zero)
- `a`: Coefficient

**Returns:**
- Calculated y values

**Note:** Input values must be non-zero

#### `inverse_square_function(t: Numeric, a: float) -> Numeric`

Inverse square function: y = a/x²

**Parameters:**
- `t`: Independent variable (must be non-zero)
- `a`: Coefficient

**Returns:**
- Calculated y values

**Note:** Input values must be non-zero

## Fitting Functions

Fitting functions perform curve fitting using the corresponding mathematical functions. All fitting functions follow the same signature and return format.

### Common Signature

```python
def fit_*(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """
    Fit equation to data.
    
    Args:
        data: Data source (dictionary or DataFrame) with x, y and their uncertainties
        x_name: Name of independent variable column
        y_name: Name of dependent variable column
        initial_guess_override: Optional list overriding automatically estimated
            parameters; None entries keep the estimate
        bounds_override: Optional pair (lower, upper) with bounds for parameters;
            None entries keep the estimator bounds
        
    Returns:
        Tuple containing:
            - text: Formatted string of parameters with uncertainties, R², and statistics
            - y_fitted: Fitted y values as ndarray
            - equation: Formatted equation string with parameter values
            
    Raises:
        FittingError: If curve fitting fails to converge
    """
```

### Available Fitting Functions

#### `fit_linear_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit linear function passing through origin: `y = m x`

**Example:**
```python
from fitting.fitting_functions import fit_linear_function

data = {
    'x': np.array([1, 2, 3, 4, 5]),
    'y': np.array([2.1, 4.2, 6.0, 8.1, 10.0]),
    'ux': np.ones(5) * 0.1,
    'uy': np.ones(5) * 0.2
}

text, y_fitted, equation, *_ = fit_linear_function(data, 'x', 'y')
```

#### `fit_linear_function_with_n(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit linear function with intercept: `y = m x + n`

**Example:**
```python
from fitting.fitting_functions import fit_linear_function_with_n

text, y_fitted, equation, *_ = fit_linear_function_with_n(data, 'x', 'y')
```

#### `fit_quadratic_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit quadratic function: `y = a x²`

#### `fit_quadratic_function_complete(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit complete quadratic function: `y = c x² + b x + a`

**Parameters:**
- `a`: Constant term
- `b`: Linear coefficient  
- `c`: Quadratic coefficient

**Note:** The parameter order in `initial_guess_override` and `bounds_override` is `[a, b, c]` corresponding to the formula `y = c x² + b x + a`.

#### `fit_fourth_power(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit fourth power function: `y = a x⁴`

#### `fit_sin_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit sine function: `y = a sin(b x)`

**Note:** Uses automatic parameter estimation for better convergence.

#### `fit_sin_function_with_c(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit sine function with phase shift: `y = a sin(b x + c)`

**Note:** Uses automatic parameter estimation for amplitude, frequency, and phase.

#### `fit_cos_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit cosine function: `y = a cos(b x)`

#### `fit_cos_function_with_c(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit cosine function with phase shift: `y = a cos(b x + c)`

#### `fit_tan_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit tangent function: `y = a tan(b x)`

**Note:** Uses automatic parameter estimation for better convergence.

#### `fit_tan_function_with_c(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit tangent function with phase shift: `y = a tan(b x + c)`

**Note:** Uses automatic parameter estimation for amplitude, frequency, and phase.

#### `fit_sinh_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit hyperbolic sine function: `y = a sinh(b x)`

#### `fit_cosh_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit hyperbolic cosine function: `y = a cosh(b x)`

#### `fit_ln_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit natural logarithm function: `y = a ln(x)`

**Note:** Requires x values to be positive.

#### `fit_inverse_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit inverse function: `y = a / x`

**Note:** Requires x values to be non-zero.

#### `fit_inverse_square_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit inverse square function: `y = a / x²`

**Note:** Requires x values to be non-zero.

### Special Functions

#### `fit_gaussian_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit Gaussian (normal) function: `y = A exp(-(x-μ)² / (2σ²))`

**Parameters:**
- `A`: Amplitude (peak value)
- `μ` (mu): Center position
- `σ` (sigma): Standard deviation (width)

**Note:** Uses automatic parameter estimation and applies bounds to ensure A > 0 and σ > 0.

#### `fit_exponential_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit exponential function: `y = a exp(b x)`

**Parameters:**
- `a`: Amplitude/prefactor
- `b`: Exponential rate constant

**Note:** Uses automatic parameter estimation and applies bounds to prevent overflow.

#### `fit_binomial_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit logistic (S-shaped, binomial-type) function: `y = a / (1 + exp(-b (x - c)))`

**Parameters:**
- `a`: Maximum value/asymptote
- `b`: Growth rate
- `c`: Inflection point (midpoint of transition)

**Note:** Uses automatic parameter estimation and applies bounds to ensure a > 0 and b > 0.

#### `fit_square_pulse_function(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit smooth square pulse function (approximated using hyperbolic tangents).

**Parameters:**
- `A`: Amplitude
- `t0`: Center time/position
- `w`: Width of the pulse

**Note:** Uses automatic parameter estimation with bounds based on data range.

#### `fit_hermite_polynomial_3(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit Hermite polynomial expansion up to degree 3: `y = c₀ H₀(x) + c₁ H₁(x) + c₂ H₂(x) + c₃ H₃(x)`

Where `H_k` are physicists' Hermite polynomials.

**Parameters:**
- `c0`, `c1`, `c2`, `c3`: Coefficients for each polynomial term

#### `fit_hermite_polynomial_4(data: DataLike, x_name: str, y_name: str, initial_guess_override: Optional[List[Optional[float]]] = None, bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None) -> Tuple[str, NDArray, str]`

Fit Hermite polynomial expansion up to degree 4: extends `fit_hermite_polynomial_3` with an additional `c₄ H₄(x)` term.

**Parameters:**
- `c0`, `c1`, `c2`, `c3`, `c4`: Coefficients for each polynomial term

## Data Format

All fitting functions expect a `DataLike` object (dictionary or pandas DataFrame) with the following structure:

```python
# Dictionary format
data = {
    'x': np.array([...]),      # Independent variable (required)
    'y': np.array([...]),      # Dependent variable (required)
    'ux': np.array([...]),     # X uncertainties (optional)
    'uy': np.array([...])      # Y uncertainties (optional, used for weighted fitting)
}

# DataFrame format
data = pd.DataFrame({
    'x': [...],
    'y': [...],
    'ux': [...],
    'uy': [...]
})
```

**Requirements:**
- All arrays must have the same length
- Values must be numeric (no NaN or infinite values)
- For `ln_function`: x values must be positive
- For inverse functions: x values must be non-zero

## Usage Examples

### Basic Linear Fitting

```python
import numpy as np
import pandas as pd
from fitting.fitting_functions import fit_linear_function_with_n

# Generate synthetic data
x = np.linspace(0, 10, 50)
y_true = 2.5 * x + 1.3
y_noisy = y_true + np.random.normal(0, 0.5, 50)

# Create data dictionary
data = {
    'x': x,
    'y': y_noisy,
    'ux': np.ones(50) * 0.1,
    'uy': np.ones(50) * 0.5
}

# Perform fitting
text, y_fitted, equation, *_ = fit_linear_function_with_n(data, 'x', 'y')

print(f"Parameters:\n{text}")
print(f"Equation: {equation}")
# R² is included in the text output
```

### Trigonometric Fitting

```python
from fitting.fitting_functions import fit_sin_function_with_c

# Generate sinusoidal data
x = np.linspace(0, 4*np.pi, 100)
y = 2.0 * np.sin(1.5 * x + 0.5) + np.random.normal(0, 0.1, 100)

data = {
    'x': x,
    'y': y,
    'ux': np.ones(100) * 0.01,
    'uy': np.ones(100) * 0.1
}

text, y_fitted, equation, *_ = fit_sin_function_with_c(data, 'x', 'y')
```

### Using Mathematical Functions Directly

```python
from fitting.fitting_functions import linear_function_with_n
import numpy as np

# Calculate y values for known parameters
x = np.array([1, 2, 3, 4, 5])
m, n = 2.0, 1.5
y = linear_function_with_n(x, m, n)

# Use with scipy.optimize.curve_fit directly
from scipy.optimize import curve_fit

x_data = np.array([1, 2, 3, 4, 5])
y_data = np.array([3.5, 5.5, 7.5, 9.5, 11.5])

popt, pcov = curve_fit(linear_function_with_n, x_data, y_data)
```

## Adding New Functions

See [Extending RegressionLab](../extending.md) for a detailed guide on adding new fitting functions.

### Quick Steps

1. **Define mathematical function** (`*_function`):
   ```python
   def my_function(t: Numeric, a: float, b: float) -> Numeric:
       """My custom function: y = a*exp(-b*t)"""
       return a * np.exp(-b * t)
   ```

2. **Create fitting wrapper** (`fit_*`):
   ```python
   def fit_my_function(
       data: DataLike,
       x_name: str,
       y_name: str,
       initial_guess_override: Optional[List[Optional[float]]] = None,
       bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
   ) -> Tuple[str, NDArray, str]:
       """Fit my custom function to data."""
       return generic_fit(
           data, x_name, y_name,
           fit_func=my_function,
           param_names=['a', 'b'],
           equation_template='y={a}*exp(-{b}*x)'
       )
   ```

3. **Register in `config/constants.py`** (add to `AVAILABLE_EQUATION_TYPES` and `EQUATION_FUNCTION_MAP`):
   ```python
   AVAILABLE_EQUATION_TYPES = [
       # ... existing equations ...
       'my_function',
   ]
   EQUATION_FUNCTION_MAP = {
       # ...
       'my_function': 'fit_my_function',
   }
   ```

4. **Add translations** in `locales/en.json` and `locales/es.json`

5. **Test thoroughly** with various datasets

## Error Handling

### Common Errors

1. **Fitting Convergence Failure**:
   ```python
   from utils.exceptions import FittingError
   
   try:
       text, y_fitted, equation, *_ = fit_ln_function(data, 'x', 'y')
   except FittingError as e:
       print(f"Fitting failed: {e}")
       # Try different equation or check data quality
   ```

2. **Invalid Data**:
   ```python
   # For ln_function: x must be positive
   data = {'x': np.array([-1, 0, 1, 2]), 'y': np.array([1, 2, 3, 4])}
   # Will fail or produce invalid results
   ```

3. **Insufficient Data Points**:
   - Most functions require at least 3-5 data points
   - More complex functions (e.g., `quadratic_function_complete`) need more points

## Best Practices

1. **Check Data Quality**: Validate data before fitting
   ```python
   from utils.validators import validate_fitting_data
   
   validate_fitting_data(data, 'x', 'y')
   text, y_fitted, equation, *_ = fit_linear_function_with_n(data, 'x', 'y')
   ```

2. **Use Appropriate Function**: Choose the function that matches your data pattern
   - Linear data → `fit_linear_function` or `fit_linear_function_with_n`
   - Periodic data → `fit_sin_function` or `fit_cos_function`
   - Exponential decay → Consider custom function

3. **Check R² Value**: R² is included in the text output and indicates fit quality
   - R² > 0.95: Excellent fit
   - R² > 0.85: Good fit
   - R² < 0.70: Poor fit, consider different equation

4. **Handle Uncertainties**: Always provide uncertainty arrays when available for weighted fitting

5. **Visualize Results**: Plot data and fitted curve to verify fit quality

## Technical Details

### Implementation

All fitting functions use `generic_fit()` from `fitting_utils`, which:
- Wraps `scipy.optimize.curve_fit` for optimization
- Handles weighted fitting based on uncertainties
- Calculates covariance matrix for parameter uncertainties
- Computes R² coefficient of determination (included in text output)
- Calculates additional statistics (RMSE, chi-squared, reduced chi-squared, degrees of freedom, confidence intervals)
- Formats output for display

### Numerical Considerations

- **Initial Parameter Guesses**: Trigonometric (sin/cos/tan) use `estimate_trigonometric_parameters()` and `estimate_phase_shift()` from `fitting.estimators`. Hyperbolic (sinh/cosh) use `estimate_hyperbolic_parameters()` and `estimate_hyperbolic_bounds()` from the same module for initial values and bounds
- **Parameter Bounds**: Can be applied to constrain parameters (not currently used in default implementation)
- **Robust Fitting**: For outlier-heavy data, consider using robust loss functions
- **Convergence**: Nonlinear functions may require good initial guesses or multiple attempts

### Performance

- **Vectorized Operations**: All mathematical functions use NumPy vectorization
- **Memory Efficiency**: Functions handle both scalar and array inputs efficiently
- **Fitting Speed**: Linear functions are fastest; trigonometric functions may be slower due to parameter estimation

---

*For implementation details, see the source code: `src/fitting/functions/` (e.g. `polynomials.py`, `trigonometric.py`, `inverse.py`, `special.py`). The public API is re-exported by `src/fitting/fitting_functions/`.*
