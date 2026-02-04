# Extending RegressionLab

This guide explains how to add new fitting functions to RegressionLab. Whether you want to add a specific equation for your research or extend the library with new mathematical models, this guide will walk you through the process.

## Overview

Adding a new fitting function involves three main steps:

1. **Define the mathematical function**: Write the Python function that calculates y from x and parameters
2. **Create the fitting wrapper**: Write a function that performs the curve fitting
3. **Register the function**: Add it to the configuration so it appears in the UI

## Prerequisites

### Required Knowledge

- **Basic Python**: Functions, variables, imports
- **NumPy basics**: Arrays, mathematical operations
- **Basic mathematics**: Understanding the equation you want to add

### Files You'll Modify

```
src/
├── config/
│   └── constants.py                   # Add equation type, EQUATION_FUNCTION_MAP, EQUATION_FORMULAS
└── fitting/
    ├── functions/                     # Add mathematical and fit_* in appropriate module
    │   ├── polynomials.py
    │   ├── trigonometric.py
    │   ├── inverse.py
    │   └── special.py
    └── fitting_utils.py               # (optional) factory / get_fitting_function
```

## Step-by-Step Guide

### Step 1: Define the Mathematical Function

Open the appropriate module under `src/fitting/functions/` (e.g. `special.py` for exponential/Gaussian, `polynomials.py` for polynomial models) and add your mathematical function.

#### Example: Adding an Exponential Function

```python
def exponential_function(t: Numeric, a: float, b: float) -> Numeric:
    """Exponential function: y = a * exp(b * t)"""
    return a * np.exp(b * t)
```

**Key Points**:
- **Type hints**: Use `Numeric` type for variables that can be scalar or array
- **Docstring**: Explain what the function does, its parameters, and return value
- **NumPy functions**: Use `np.exp()`, `np.sin()`, etc. for array compatibility
- **Parameter order**: After `t`, list all fitting parameters

#### More Examples

**Power Law**:
```python
def power_function(t: Numeric, a: float, b: float) -> Numeric:
    """Power function: y = a * t^b"""
    return a * (t ** b)
```

**Gaussian**:
```python
def gaussian_function(t: Numeric, a: float, mu: float, sigma: float) -> Numeric:
    """Gaussian function: y = a * exp(-(t-mu)²/(2*sigma²))"""
    return a * np.exp(-(t - mu)**2 / (2 * sigma**2))
```

**Logistic**:
```python
def logistic_function(t: Numeric, L: float, k: float, t0: float) -> Numeric:
    """Logistic function: y = L / (1 + exp(-k*(t-t0)))"""
    return L / (1 + np.exp(-k * (t - t0)))
```

**Hyperbola**:
```python
def hyperbola_function(t: Numeric, a: float, b: float) -> Numeric:
    """Hyperbola: y = a / (b + t)"""
    return a / (b + t)
```

### Step 2: Create the Fitting Wrapper

In the same module under `fitting/functions/`, create a wrapper function that performs the fitting.

#### Basic Template

```python
def fit_exponential(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Exponential fit: y = a·exp(b·x)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from fitting.fitting_utils import generic_fit
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=exponential_function,
        param_names=['a', 'b'],
        equation_template='y={a}·exp({b}·x)'
    )
```

**Key Points**:
- **Function signature**: `data` is a `dict`, not a DataFrame
- **Parameter names**: List of strings matching the function parameters
- **Equation template**: String with placeholders like `{a}`, `{b}`, etc.
- **Return value**: `generic_fit` handles everything and returns the tuple
- Add the fitting wrapper in the same module as the mathematical function (under `fitting/functions/`).

#### Advanced: With Initial Parameter Guess

For complex functions, providing initial guesses improves convergence:

```python
def fit_gaussian(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Gaussian fit: y = a·exp(-(x-mu)²/(2·sigma²))
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from fitting.fitting_utils import generic_fit
    
    # Estimate initial parameters
    x = data[x_name]
    y = data[y_name]
    a0 = np.max(y)  # Amplitude: max y value
    mu0 = x[np.argmax(y)]  # Mean: x at max y
    sigma0 = (np.max(x) - np.min(x)) / 4  # Spread: quarter of x range
    initial_guess = [a0, mu0, sigma0]
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=gaussian_function,
        param_names=['a', 'mu', 'sigma'],
        equation_template='y={a}·exp(-(x-{mu})²/(2·{sigma}²))',
        initial_guess=initial_guess
    )
```

### Step 3: Register the Function

#### Add to Configuration

Open `src/config/constants.py` and add your equation to `AVAILABLE_EQUATION_TYPES` and to the `EQUATION_FUNCTION_MAP` dictionary:

```python
EQUATION_FUNCTION_MAP = {
    'linear_function_with_n': 'fit_linear_function_with_n',
    'linear_function': 'fit_linear_function',
    'quadratic_function_complete': 'fit_quadratic_function_complete',
    # ... existing mappings ...
    'exponential_function': 'fit_exponential',  # Add your new mapping here
}
```

The `get_fitting_function()` in `fitting_utils.py` uses this map (imported from `config`) to load functions, so you don't need to modify it directly.

#### Add Translations

Add translations for your equation name in both language files:

**English** (`src/locales/en.json`):
```json
{
  "equations": {
    "exponential_function": "Exponential Function"
  }
}
```

**Spanish** (`src/locales/es.json`):
```json
{
  "equations": {
    "exponential_function": "Función Exponencial"
  }
}
```


#### Add Formula for UI (Optional)

For both Tkinter and Streamlit, add the formula to `src/config/constants.py` in `EQUATION_FORMULAS`:

```python
EQUATION_FORMULAS = {
    'linear_function_with_n': 'y=mx+n',
    'linear_function': 'y=mx',
    # ... existing formulas ...
    'exponential_function': 'y=a·exp(b·x)',  # Add your formula
}
```

### Step 4: Test Your Function

#### Create Test Data

Create a test file in `input/` folder:

```python
# generate_exponential_test.py
import pandas as pd
import numpy as np

# Generate synthetic exponential data
x = np.linspace(0, 3, 30)
y = 2.5 * np.exp(0.8 * x) + np.random.normal(0, 0.5, 30)  # Add noise

# Create DataFrame
data = pd.DataFrame({
    'x': x,
    'y': y,
    'ux': [0.05] * len(x),  # Uncertainties
    'uy': [0.5] * len(x)
})

# Save to CSV
data.to_csv('input/exponential_test.csv', index=False)
print("Test data created: input/exponential_test.csv")
```

Run the script:
```bash
python generate_exponential_test.py
```

#### Test in Tkinter

1. Run RegressionLab
2. Select "Normal Fitting"
3. Choose "Exponential Function" from equation dropdown
4. Load `exponential_test.csv`
5. Select x and y variables
6. View results and check:
   - Parameters are reasonable (a ≈ 2.5, b ≈ 0.8)
   - R² is high (> 0.95)
   - Plot looks good

#### Test in Streamlit

1. Run `streamlit run src/streamlit_app/app.py`
2. Upload `exponential_test.csv`
3. Select "Exponential Function"
4. Verify results

## Advanced Topics

### Parameter Bounds

Constrain parameters to valid ranges. Note: `generic_fit` doesn't support bounds directly, so you'll need to use `curve_fit` directly:

```python
def fit_positive_exponential(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Exponential fit with positive parameters only: y = a·exp(b·x), a>0, b>0
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from scipy.optimize import curve_fit
    from fitting.fitting_utils import format_parameter
    
    x = data[x_name]
    y = data[y_name]
    uy = data[f'u{y_name}']
    
    # Set parameter bounds: a > 0, b > 0
    bounds = ([0, 0], [np.inf, np.inf])
    
    # Perform fit with bounds
    params, cov = curve_fit(
        exponential_function,
        x, y,
        sigma=uy,
        bounds=bounds,
        absolute_sigma=True
    )
    
    # Calculate fitted values and R²
    y_fitted = exponential_function(x, *params)
    ss_res = np.sum((y - y_fitted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    # Format parameters
    uncertainties = np.sqrt(np.diag(cov))
    a, b = params
    a_formatted, a_unc = format_parameter(a, uncertainties[0])
    b_formatted, b_unc = format_parameter(b, uncertainties[1])
    
    param_text = f"a={a_formatted}, σ(a)={a_unc}\nb={b_formatted}, σ(b)={b_unc}\nR²={r_squared:.6f}"
    equation = f"y={a_formatted}·exp({b_formatted}·x)"
    
    return param_text, y_fitted, equation, r_squared
```

### Fixed Parameters

Fit with some parameters fixed:

```python
def fit_exponential_fixed_b(data: dict, x_name: str, y_name: str, b_fixed: float = 1.0) -> Tuple[str, NDArray, str, float]:
    """Exponential fit with fixed b parameter: y = a·exp(b_fixed·x)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from fitting.fitting_utils import generic_fit
    
    # Define function with b fixed
    def exponential_fixed_b_function(t: Numeric, a: float) -> Numeric:
        """Exponential function with fixed b: y = a·exp(b_fixed·t)"""
        return a * np.exp(b_fixed * t)
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=exponential_fixed_b_function,
        param_names=['a'],
        equation_template=f'y={{a}}·exp({b_fixed}·x)'
    )
```

### Multi-Dimensional Functions

For functions of multiple variables (e.g., z = f(x, y)), you'll need to use `curve_fit` directly since `generic_fit` is designed for single-variable functions:

```python
def plane_3d_function(data: NDArray, a: float, b: float, c: float) -> Numeric:
    """3D plane: z = a*x + b*y + c"""
    x = data[:, 0]  # First column
    y = data[:, 1]  # Second column
    return a * x + b * y + c

def fit_plane_3d(data: dict, x_name: str, y_name: str, z_name: str) -> Tuple[str, NDArray, str, float]:
    """3D plane fit: z = a·x + b·y + c
    
    Returns:
        Tuple of (text, z_fitted, equation, r_squared)
    """
    from scipy.optimize import curve_fit
    from fitting.fitting_utils import format_parameter
    
    # Prepare data
    x = data[x_name]
    y = data[y_name]
    z = data[z_name]
    xy = np.column_stack([x, y])  # Combine x and y
    uz = data[f'u{z_name}']
    
    # Fit
    params, cov = curve_fit(plane_3d_function, xy, z, sigma=uz, absolute_sigma=True)
    
    # Calculate fitted values
    z_fitted = plane_3d_function(xy, *params)
    ss_res = np.sum((z - z_fitted) ** 2)
    ss_tot = np.sum((z - np.mean(z)) ** 2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    # Format parameters
    uncertainties = np.sqrt(np.diag(cov))
    a, b, c = params
    a_formatted, a_unc = format_parameter(a, uncertainties[0])
    b_formatted, b_unc = format_parameter(b, uncertainties[1])
    c_formatted, c_unc = format_parameter(c, uncertainties[2])
    
    param_text = (
        f"a={a_formatted}, σ(a)={a_unc}\n"
        f"b={b_formatted}, σ(b)={b_unc}\n"
        f"c={c_formatted}, σ(c)={c_unc}\n"
        f"R²={r_squared:.6f}"
    )
    equation = f"z={a_formatted}·x+{b_formatted}·y+{c_formatted}"
    
    return param_text, z_fitted, equation, r_squared
```

### Piecewise Functions

Functions with different behaviors in different regions:

```python
def piecewise_linear_function(t: Numeric, a: float, b: float, t_break: float,
                              c: float, d: float) -> Numeric:
    """Piecewise linear function: y = a*t + b if t < t_break, else y = c*t + d"""
    y = np.where(
        t < t_break,
        a * t + b,  # First segment
        c * t + d   # Second segment
    )
    return y
```

## Code Style Guidelines

### Follow Existing Conventions

1. **Naming**:
   - Mathematical functions: `<name>_function` (e.g., `exponential_function`)
   - Fitting functions: `fit_<name>` (e.g., `fit_exponential`)
   - Use snake_case for function names

2. **Type Hints**:
   ```python
   from numpy.typing import NDArray
   from typing import Tuple
   
   def my_function(t: Numeric, a: float) -> Numeric:
       """Function description: y = ..."""
       ...
   
   def my_fit(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
       ...
   ```

3. **Docstrings**:
   ```python
   def example_function(t: Numeric, a: float, b: float) -> Numeric:
       """Example function: y = a * exp(b * t)"""
       return a * np.exp(b * t)
   ```
   
   For fitting wrapper functions:
   ```python
   def fit_example(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
       """Example fit: y = a·exp(b·x)
       
       Returns:
           Tuple of (text, y_fitted, equation, r_squared)
       """
       ...
   ```

4. **Error Handling**:
   ```python
   def fit_example(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
       """Example fit: y = a·x + b
       
       Returns:
           Tuple of (text, y_fitted, equation, r_squared)
       """
       # generic_fit handles errors internally, but you can wrap it if needed
       from fitting.fitting_utils import generic_fit
       from utils.exceptions import FittingError
       
       try:
           return generic_fit(
               data, x_name, y_name,
               fit_func=example_function,
               param_names=['a', 'b'],
               equation_template='y={a}·x+{b}'
           )
       except FittingError:
           # Re-raise fitting errors
           raise
       except Exception as e:
           # Unexpected error
           from utils.logger import get_logger
           logger = get_logger(__name__)
           logger.error(f"Unexpected error in fitting: {e}", exc_info=True)
           raise FittingError(f"Unexpected error: {str(e)}")
   ```

### Testing

Create a test file in `tests/` directory:

```python
# tests/test_exponential_function.py
import numpy as np
import pytest
from fitting.fitting_functions import exponential_function, fit_exponential

def test_exponential_function():
    """Test exponential function calculation."""
    t = np.array([0, 1, 2])
    a, b = 2.0, 0.5
    
    expected = np.array([2.0, 2.0 * np.exp(0.5), 2.0 * np.exp(1.0)])
    result = exponential_function(t, a, b)
    
    np.testing.assert_array_almost_equal(result, expected)

def test_fit_exponential():
    """Test exponential fitting."""
    # Generate perfect exponential data
    x = np.linspace(0, 2, 20)
    y = 2.5 * np.exp(0.8 * x)
    
    # Create data dictionary (as expected by fitting functions)
    data = {
        'x': x,
        'y': y,
        'ux': np.zeros_like(x),
        'uy': np.zeros_like(y)
    }
    
    param_text, y_fitted, equation, r_squared = fit_exponential(data, 'x', 'y')
    
    # Check R² is very high for perfect data
    assert r_squared > 0.999
    
    # Check fitted values are close
    np.testing.assert_array_almost_equal(y_fitted, y, decimal=6)
```

Run tests:
```bash
pytest tests/test_exponential_function.py -v
```

## Common Patterns

### Pattern 1: Simple Function

For straightforward equations without special requirements:

```python
# 1. Define function
def power_function(t: Numeric, a: float, n: float) -> Numeric:
    """Power function: y = a * t^n"""
    return a * (t ** n)

# 2. Create fitting wrapper
def fit_power(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Power fit: y = a·x^n
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from fitting.fitting_utils import generic_fit
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=power_function,
        param_names=['a', 'n'],
        equation_template='y={a}·x^{n}'
    )

# 3. Register in config/constants.py: AVAILABLE_EQUATION_TYPES, EQUATION_FUNCTION_MAP, (optional) EQUATION_FORMULAS
# 4. Add translations in locales/
```

### Pattern 2: Function with Estimation

For complex functions needing initial guesses:

```python
# Provide smart initial guesses
def damped_sine_function(t: Numeric, a: float, b: float, c: float) -> Numeric:
    """Damped sine function: y = a·exp(-c·t)·sin(b·t)"""
    return a * np.exp(-c * t) * np.sin(b * t)

def fit_damped_sine(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Damped sine fit: y = a·exp(-c·x)·sin(b·x)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from fitting.fitting_utils import generic_fit, estimate_trigonometric_parameters
    
    x = data[x_name]
    y = data[y_name]
    
    # Estimate initial parameters
    a0, b0 = estimate_trigonometric_parameters(x, y)
    c0 = 0.1  # Small damping factor
    initial_guess = [a0, b0, c0]
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=damped_sine_function,
        param_names=['a', 'b', 'c'],
        equation_template='y={a}·exp(-{c}·x)·sin({b}·x)',
        initial_guess=initial_guess
    )
```

### Pattern 3: Specialized Function

For functions with constraints or special handling, use `curve_fit` directly:

```python
# Use custom fitting logic
def bounded_growth_function(t: Numeric, L: float, k: float) -> Numeric:
    """Bounded growth function: y = L / (1 + exp(-k*t))"""
    return L / (1 + np.exp(-k * t))

def fit_bounded_growth(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Bounded growth fit with constraints: y = L / (1 + exp(-k*x))
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from scipy.optimize import curve_fit
    from fitting.fitting_utils import format_parameter
    
    x = data[x_name]
    y = data[y_name]
    uy = data[f'u{y_name}']
    
    # Constrain growth rate to positive and limit below max(y)
    bounds = ([0, 0], [np.max(y) * 1.5, np.inf])
    
    params, cov = curve_fit(
        bounded_growth_function, x, y, 
        sigma=uy, 
        bounds=bounds,
        absolute_sigma=True
    )
    
    # Calculate fitted values and R²
    y_fitted = bounded_growth_function(x, *params)
    ss_res = np.sum((y - y_fitted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    
    # Format parameters (similar to generic_fit)
    uncertainties = np.sqrt(np.diag(cov))
    # ... format and return
```

## Example: Complete Implementation

Here's a complete example adding a Stretched Exponential function:

**1. Add to `fitting/functions/` (e.g. `special.py`):**

```python
def stretched_exponential_function(t: Numeric, a: float, tau: float, beta: float) -> Numeric:
    """Stretched exponential (Kohlrausch) function: y = a * exp(-(t/tau)^beta)"""
    return a * np.exp(-(t / tau) ** beta)

def fit_stretched_exponential(data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str, float]:
    """Stretched exponential fit: y = a·exp(-(x/tau)^beta)
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared)
    """
    from fitting.fitting_utils import generic_fit
    
    # Extract data for initial parameter estimation
    x = data[x_name]
    y = data[y_name]
    
    # Estimate initial parameters
    a0 = y[0]  # Initial amplitude
    tau0 = x[len(x)//2]  # Half-time as estimate
    beta0 = 1.0  # Start with pure exponential
    initial_guess = [a0, tau0, beta0]
    
    return generic_fit(
        data, x_name, y_name,
        fit_func=stretched_exponential_function,
        param_names=['a', 'tau', 'beta'],
        equation_template='y={a}·exp(-(x/{tau})^{beta})',
        initial_guess=initial_guess
    )
```

**2. Add to `config/constants.py`:**

```python
AVAILABLE_EQUATION_TYPES = [
    # ... existing types ...
    'stretched_exponential_function',
]

EQUATION_FUNCTION_MAP = {
    # ... existing mappings ...
    'stretched_exponential_function': 'fit_stretched_exponential',
}

# Optional: for UI formula display
EQUATION_FORMULAS = {
    # ...
    'stretched_exponential_function': 'y=a·exp(-(x/τ)^β)',
}
```

**3. Add to `locales/en.json`:**

```json
{
  "equations": {
    "stretched_exponential_function": "Stretched Exponential (Kohlrausch)"
  }
}
```

**4. Add to `locales/es.json`:**

```json
{
  "equations": {
    "stretched_exponential_function": "Exponencial Estirada (Kohlrausch)"
  }
}
```

**5. (Optional)** If you didn’t add the formula in step 2, add it to `EQUATION_FORMULAS` in `config/constants.py`.

**6. Test:**

```python
# Create test data
import numpy as np
import pandas as pd

t = np.linspace(0, 10, 100)
y = 5.0 * np.exp(-(t/2.5)**0.7) + np.random.normal(0, 0.1, 100)

data = pd.DataFrame({'t': t, 'y': y, 'ut': 0.1, 'uy': 0.1})
data.to_csv('input/stretched_exp_test.csv', index=False)
```

Then test in both interfaces!

## Next Steps

- **Study existing functions**: Look at the modules under `fitting/functions/` for more examples
- **Test thoroughly**: Create synthetic data with known parameters
- **Document well**: Write clear docstrings and comments
- **Contribute**: Submit your functions as pull requests to help others!

For more advanced customization, see [Customizing the Fitting Core](customization.md).

---

*Have questions? Open an issue on GitHub or check the [API Documentation](api/index.md).*
