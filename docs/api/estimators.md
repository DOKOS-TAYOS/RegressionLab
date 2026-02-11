# fitting.estimators

Initial parameter estimation functions for curve fitting.

## Overview

The `fitting.estimators` module provides functions to estimate initial parameter values for various mathematical models. These estimates are used as starting points for curve fitting algorithms to improve convergence and reduce the likelihood of finding local minima instead of the global optimum.

All estimation functions assume that input arrays `x` and `y` are finite and have been validated/cleaned by the caller. The functions are exported from the `fitting` package, so they can be imported as:

```python
from fitting import estimate_linear_parameters, estimate_gaussian_parameters
```

## Available Estimators

### Linear Functions

#### `estimate_linear_parameters(x: Any, y: Any) -> Tuple[float, float]`

Estimate initial parameters for linear fit `y = m*x + n`.

Uses `numpy.polyfit` to compute the intercept (n) and slope (m) from the data.

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array

**Returns:**
- Tuple `(n, m)`: intercept and slope

**Example:**
```python
from fitting import estimate_linear_parameters
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = np.array([2.5, 5.1, 7.4, 10.2, 12.6])
n, m = estimate_linear_parameters(x, y)
print(f"Intercept: {n:.3f}, Slope: {m:.3f}")
```

### Polynomial Functions

#### `estimate_polynomial_parameters(x: Any, y: Any, degree: int) -> List[float]`

Estimate initial parameters for polynomial `y = c0 + c1*x + ... + c_degree*x^degree`.

Uses `numpy.polyfit` to compute coefficients. Returns coefficients in order from constant term to highest degree.

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array
- `degree`: Polynomial degree

**Returns:**
- List of coefficients `[c0, c1, ..., c_degree]` (constant term first)

**Example:**
```python
from fitting import estimate_polynomial_parameters

x = np.array([1, 2, 3, 4, 5])
y = np.array([1, 4, 9, 16, 25])  # Quadratic
coefs = estimate_polynomial_parameters(x, y, degree=2)
print(f"Coefficients: {coefs}")
```

#### `estimate_single_power_parameter(x: Any, y: Any, power: int) -> float`

Estimate coefficient `a` for `y = a * x^power` (no constant term).

Uses least-squares: `a = sum(y * x^power) / sum(x^(2*power))`.

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array
- `power`: Exponent (e.g., 2 for quadratic through origin)

**Returns:**
- Estimated coefficient `a`

**Example:**
```python
from fitting import estimate_single_power_parameter

x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 8, 18, 32, 50])  # y = 2*x^2
a = estimate_single_power_parameter(x, y, power=2)
print(f"Coefficient: {a:.3f}")
```

### Trigonometric Functions

#### `estimate_trigonometric_parameters(x: Any, y: Any) -> Tuple[float, float]`

Estimate initial parameters for trigonometric functions `y = a * sin(b*x)` or `y = a * cos(b*x)`.

Uses peak detection first, with autocorrelation fallback when peaks are insufficient. Estimates amplitude (a) and angular frequency (b).

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array

**Returns:**
- Tuple `(amplitude, frequency)`

**Example:**
```python
from fitting import estimate_trigonometric_parameters
import numpy as np

x = np.linspace(0, 4*np.pi, 100)
y = 3.0 * np.sin(2.0 * x)  # Amplitude=3, Frequency=2
amplitude, frequency = estimate_trigonometric_parameters(x, y)
print(f"Amplitude: {amplitude:.3f}, Frequency: {frequency:.3f}")
```

#### `estimate_phase_shift(x: Any, y: Any, amplitude: float, frequency: float) -> float`

Estimate initial phase shift for `y = a * sin(b*x + c)` or `y = a * cos(b*x + c)`.

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array
- `amplitude`: Estimated amplitude (a)
- `frequency`: Estimated angular frequency (b)

**Returns:**
- Estimated phase shift (c)

**Example:**
```python
from fitting import estimate_trigonometric_parameters, estimate_phase_shift

amplitude, frequency = estimate_trigonometric_parameters(x, y)
phase = estimate_phase_shift(x, y, amplitude, frequency)
print(f"Phase shift: {phase:.3f}")
```

### Hyperbolic Functions

#### `estimate_hyperbolic_parameters(x: Any, y: Any) -> Tuple[float, float]`

Estimate initial parameters for hyperbolic functions `y = a * sinh(b*x)` or `y = a * cosh(b*x)`.

- Amplitude (a) from half the y range
- Frequency (b) from the inverse of the x range

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array

**Returns:**
- Tuple `(amplitude, frequency)`

**Example:**
```python
from fitting import estimate_hyperbolic_parameters
import numpy as np

x = np.linspace(0, 2, 50)
y = 2.0 * np.sinh(1.5 * x)
amplitude, frequency = estimate_hyperbolic_parameters(x, y)
print(f"Amplitude: {amplitude:.3f}, Frequency: {frequency:.3f}")
```

#### `estimate_hyperbolic_bounds(x: Any) -> Tuple[Tuple[float, float], Tuple[float, float]]`

Return parameter bounds for hyperbolic fits to avoid overflow in `exp`.

For `y = a * sinh(b*x)` or `y = a * cosh(b*x)`: `a` can be any real; `b` is bounded so that `b * max(|x|)` does not cause overflow.

**Parameters:**
- `x`: Independent variable array

**Returns:**
- Pair `(lower_bounds, upper_bounds)`, each of length 2 for `(a, b)`

**Example:**
```python
from fitting import estimate_hyperbolic_parameters, estimate_hyperbolic_bounds

amplitude, frequency = estimate_hyperbolic_parameters(x, y)
(lower, upper) = estimate_hyperbolic_bounds(x)
# Use with merge_bounds when calling generic_fit
```

### Logarithmic Functions

#### `estimate_ln_parameter(x: Any, y: Any) -> float`

Estimate initial parameter `a` for `y = a * ln(x)`.

Uses least squares with no intercept. Requires positive x values.

**Parameters:**
- `x`: Independent variable array (must be positive)
- `y`: Dependent variable array

**Returns:**
- Estimated coefficient `a`

**Example:**
```python
from fitting import estimate_ln_parameter

x = np.array([1, 2, 3, 4, 5])
y = 2.5 * np.log(x)
a = estimate_ln_parameter(x, y)
print(f"Coefficient: {a:.3f}")
```

### Inverse Functions

#### `estimate_inverse_parameter(x: Any, y: Any, power: int) -> float`

Estimate coefficient `a` for `y = a / x^power`.

Uses median of `(y * x^power)` for robustness to outliers.

**Parameters:**
- `x`: Independent variable array (avoid zeros)
- `y`: Dependent variable array
- `power`: Power in denominator (1 or 2)

**Returns:**
- Estimated coefficient `a`

**Example:**
```python
from fitting import estimate_inverse_parameter

x = np.array([1, 2, 3, 4, 5])
y = 10.0 / x  # y = 10/x
a = estimate_inverse_parameter(x, y, power=1)
print(f"Coefficient: {a:.3f}")
```

### Gaussian Functions

#### `estimate_gaussian_parameters(x: Any, y: Any) -> Tuple[float, float, float]`

Estimate initial `(A, mu, sigma)` for `y = A * exp(-(x-mu)^2 / (2*sigma^2))`.

- `A` from `max(y)`
- `mu` from `x` at maximum
- `sigma` from FWHM (full width at half maximum) using half-max crossings

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array

**Returns:**
- Tuple `(A, mu, sigma)`

**Example:**
```python
from fitting import estimate_gaussian_parameters
import numpy as np

x = np.linspace(-5, 5, 100)
y = 5.0 * np.exp(-(x - 1.0)**2 / (2 * 1.5**2))  # A=5, mu=1, sigma=1.5
A, mu, sigma = estimate_gaussian_parameters(x, y)
print(f"A: {A:.3f}, mu: {mu:.3f}, sigma: {sigma:.3f}")
```

### Exponential Functions

#### `estimate_exponential_parameters(x: Any, y: Any) -> Tuple[float, float]`

Estimate `(a, b)` for `y = a * exp(b*x)`.

Uses `log(y) = log(a) + b*x` when `y > 0`; otherwise fallback from endpoints.

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array

**Returns:**
- Tuple `(a, b)`

**Example:**
```python
from fitting import estimate_exponential_parameters

x = np.array([0, 1, 2, 3, 4])
y = 2.0 * np.exp(0.5 * x)  # a=2, b=0.5
a, b = estimate_exponential_parameters(x, y)
print(f"a: {a:.3f}, b: {b:.3f}")
```

### Logistic/Binomial Functions

#### `estimate_binomial_parameters(x: Any, y: Any) -> Tuple[float, float, float]`

Estimate `(a, b, c)` for logistic `y = a / (1 + exp(-b*(x-c)))`.

- `a` = range (y_max - y_min)
- `c` = midpoint of transition
- `b` from inverse of transition width

**Parameters:**
- `x`: Independent variable array
- `y`: Dependent variable array

**Returns:**
- Tuple `(a, b, c)`

**Example:**
```python
from fitting import estimate_binomial_parameters

x = np.linspace(-5, 5, 100)
y = 10.0 / (1 + np.exp(-2.0 * (x - 1.0)))  # Logistic curve
a, b, c = estimate_binomial_parameters(x, y)
print(f"a: {a:.3f}, b: {b:.3f}, c: {c:.3f}")
```

### Square Pulse Functions

#### `estimate_square_pulse_parameters(x: Any, y: Any) -> Tuple[float, float, float]`

Estimate `(A, t0, w)` for a smooth square pulse: amplitude, center time, width.

- `A` from peak-to-peak
- `t0` from center of mass of `y` (absolute value)
- `w` from support of elevated region

**Parameters:**
- `x`: Independent variable array (e.g., time)
- `y`: Dependent variable array

**Returns:**
- Tuple `(A, t0, w)`

**Example:**
```python
from fitting import estimate_square_pulse_parameters

x = np.linspace(0, 10, 100)
# Square pulse centered at t=5 with width=2
y = np.where((x >= 4) & (x <= 6), 5.0, 0.0)
A, t0, w = estimate_square_pulse_parameters(x, y)
print(f"A: {A:.3f}, t0: {t0:.3f}, w: {w:.3f}")
```

## Usage Patterns

### Using Estimators with Fitting Functions

Estimators are typically used internally by fitting functions to provide initial guesses, but you can also use them directly:

```python
from fitting import estimate_gaussian_parameters, get_fitting_function
import numpy as np

# Generate sample data
x = np.linspace(-5, 5, 100)
y = 5.0 * np.exp(-(x - 1.0)**2 / (2 * 1.5**2)) + np.random.normal(0, 0.1, 100)

# Estimate initial parameters
A_0, mu_0, sigma_0 = estimate_gaussian_parameters(x, y)
print(f"Initial guess: A={A_0:.3f}, mu={mu_0:.3f}, sigma={sigma_0:.3f}")

# Use with fitting function (if it accepts initial_guess parameter)
# Note: Most fitting functions use estimators internally
```

### Error Handling

All estimator functions handle edge cases gracefully:

- **Insufficient data**: Returns sensible defaults (e.g., mean value, zero)
- **Zero/negative values**: Handles edge cases for logarithmic and inverse functions
- **Numerical issues**: Clips values to prevent overflow/underflow
- **Peak detection failures**: Falls back to alternative estimation methods

### Performance Considerations

- Estimators are designed to be fast and robust
- They use vectorized NumPy operations
- Some functions (like trigonometric) use peak detection which can be slower for large datasets
- For very large datasets, consider subsampling before estimation

## Integration with Fitting Workflow

The estimators are automatically used by fitting functions in `fitting.fitting_functions` when initial guesses are needed. You typically don't need to call them directly unless you're:

1. **Debugging**: Checking if initial guesses are reasonable
2. **Custom fitting**: Creating your own fitting routines
3. **Visualization**: Plotting initial guesses before fitting

## Best Practices

1. **Validate inputs**: Ensure `x` and `y` are finite and have sufficient data points
2. **Check domain**: For logarithmic functions, ensure `x > 0`
3. **Handle outliers**: Some estimators use median for robustness
4. **Use appropriate estimators**: Match the estimator to your model type

---

*For more information about fitting functions, see [fitting_functions](fitting_functions.md) and [fitting_utils](fitting_utils.md).*
