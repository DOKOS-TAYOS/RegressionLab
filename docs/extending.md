# Extending RegressionLab

This guide explains how to add new fitting functions to RegressionLab. Whether you want to add a specific equation for your research or extend the library with new mathematical models, this guide will walk you through the process.

## Overview

Adding a new fitting function involves four main steps:

1. **Implement the model and fit function**: In the right module under `src/fitting/functions/`, add the mathematical function and a fitting wrapper that uses `generic_fit` (or `curve_fit` directly for advanced cases).
2. **Export the fit function**: Add the new `fit_*` to the exports in `src/fitting/functions/__init__.py` so the app can resolve it by name.
3. **Register in configuration**: Add an entry in `src/config/equations.yaml` (with `function`, `formula`, `format`, `param_names`) and add translations in `src/locales/`.
4. **Test**: Run the app (Tkinter or Streamlit) and optionally add tests.

The app resolves fit functions by name: it reads the `function` key from `equations.yaml` (e.g. `fit_exponential_function`) and does `getattr(fitting_functions, function_name)`. The `fitting_functions` package re-exports everything from `fitting.functions`, so any new `fit_*` must be implemented in one of the modules under `fitting/functions/` and re-exported from `fitting/functions/__init__.py`.

## Prerequisites

### Required Knowledge

- **Basic Python**: Functions, variables, imports
- **NumPy basics**: Arrays, mathematical operations
- **Basic mathematics**: Understanding the equation you want to add

### Files You'll Modify

```
src/
├── config/
│   └── equations.yaml                # Add entry: function, formula, format, param_names
├── fitting/
│   └── functions/
│       ├── __init__.py               # Export new fit_* (add to imports and __all__)
│       ├── _base.py                  # Re-exports fitting utils and estimators
│       ├── polynomials.py
│       ├── trigonometric.py
│       ├── inverse.py
│       └── special.py
├── fitting/
│   └── estimators.py                 # (optional) add estimator for initial guess/bounds
└── locales/
    ├── en.json                       # Add translation for equation ID
    ├── es.json
    └── de.json
```

## Step-by-Step Guide

### Step 1: Implement the Model and Fit Function

Open the appropriate module under `src/fitting/functions/` (e.g. `special.py` for exponential/Gaussian, `polynomials.py` for polynomial models). Add the mathematical model (e.g. `_my_function`) and the fitting wrapper (`fit_my_function`). The model can be a private function (e.g. `_gaussian_function`) if it is only used inside that module.

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

In the same module under `fitting/functions/`, create a fitting wrapper. The wrapper must have this signature and return type:

- **Signature**: `(data, x_name, y_name, initial_guess_override=None, bounds_override=None)`
- **Return**: Your wrapper can return `(text, y_fitted, equation)` or the full 4-tuple from `generic_fit`: `(text, y_fitted, equation, fit_info)`. R² is included in `text`. Callers (e.g. Streamlit) use the first three values.

Use `get_equation_param_names_for_function('fit_<name>')` and `get_equation_format_for_function('fit_<name>')` so parameter names and the equation format live only in `equations.yaml`. That way you define them once in config. These lookups are O(1) via pre-built reverse dicts (`_FUNCTION_TO_EQUATION` in `constants.py`).

#### Basic Template

```python
from fitting.functions._base import (
    DataLike,
    Numeric,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
)

def fit_my_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """Fit my model: y = a·exp(b·x).
    
    Returns:
        Tuple (text, y_fitted, equation) from generic_fit.
    """
    return generic_fit(
        data, x_name, y_name,
        fit_func=my_model_function,
        param_names=get_equation_param_names_for_function('fit_my_function'),
        equation_template=get_equation_format_for_function('fit_my_function'),
    )
```

**Key Points**:
- **Signature**: Include `initial_guess_override` and `bounds_override` so the workflow can pass user overrides; they can be `None` if you do not use them.
- **Config-driven params**: Prefer `get_equation_param_names_for_function` and `get_equation_format_for_function` so the equation is defined once in `equations.yaml`.
- **Return**: `generic_fit` returns `(text, y_fitted, equation, fit_info)` (four values). Your wrapper can `return generic_fit(...)`; callers that only need text, y_fitted, and equation use the first three elements.

#### With Initial Guess and Bounds

For complex functions, use estimators (from `_base` or `estimators`) and merge helpers:

```python
from fitting.functions._base import (
    DataLike,
    Numeric,
    estimate_gaussian_parameters,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
    merge_bounds,
    merge_initial_guess,
)

def fit_gaussian_function(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """Gaussian fit: y = A·exp(-(x-μ)²/(2σ²))."""
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
```

### Step 3: Export the Fit Function

The app resolves the fit function by name with `getattr(fitting_functions, function_name)`. The `fitting_functions` package re-exports from `fitting.functions`, so you must export your new `fit_*` from `src/fitting/functions/__init__.py`.

1. Add your fit function to the appropriate `from .<module> import ...` (e.g. `from .special import ..., fit_my_function`).
2. Add the same name to the `__all__` list in that file.

If you omit this step, the app will raise `AttributeError` when the user selects your equation.

### Step 4: Register in Configuration

#### Add to equations.yaml

Open `src/config/equations.yaml` and add a new entry. The key is the equation ID (e.g. `exponential_function`). The order of entries defines the order in the UI.

```yaml
# Add at the desired position (order matters for AVAILABLE_EQUATION_TYPES)
exponential_function:
  function: fit_exponential_function
  formula: "y = a exp(bx)"
  format: "y={a} exp({b}x)"
  param_names: [a, b]
```

- **`function`**: Exact name of your fitting function (e.g. `fit_exponential_function`). Must match the name exported from `fitting.functions`.
- **`formula`**: Display string for the UI (Tkinter and Streamlit).
- **`format`**: Template with `{param}` placeholders used to build the fitted equation string (e.g. `y={a} exp({b}x)`). Required by `generic_fit` when using `get_equation_format_for_function`.
- **`param_names`**: List of parameter names in the order expected by your mathematical function (same order as in the model signature after the independent variable).

The application loads this file at startup; `AVAILABLE_EQUATION_TYPES` and `EQUATIONS` in `config.constants` are built from it, so you do not need to edit `constants.py`.

#### Add Translations

Add translations for the equation ID in the `equations` section of each locale file:

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

**German** (`src/locales/de.json`):
```json
{
  "equations": {
    "exponential_function": "Exponentialfunktion"
  }
}
```

### Step 5: Test Your Function

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

`generic_fit` accepts a `bounds` argument. Pass `(lower_bounds, upper_bounds)` when building your fit (see "With Initial Guess and Bounds" above). For full control (e.g. custom formatting), use `curve_fit` directly and then build the same return tuple `(text, y_fitted, equation[, fit_info])` that `generic_fit` returns, including R² in the text.

### Fixed Parameters

Fit with some parameters fixed: define a reduced model that takes only the free parameters and pass the corresponding `param_names` and `equation_template` (or register a separate equation in `equations.yaml` with its own `format` and `param_names`).

### Multi-Dimensional Functions

For functions of multiple variables (e.g., z = f(x, y)), you'll need to use `curve_fit` directly since `generic_fit` is designed for single-variable functions:

```python
def plane_3d_function(data: NDArray, a: float, b: float, c: float) -> Numeric:
    """3D plane: z = a*x + b*y + c"""
    x = data[:, 0]  # First column
    y = data[:, 1]  # Second column
    return a * x + b * y + c

def fit_plane_3d(data: dict, x_name: str, y_name: str, z_name: str) -> Tuple[str, NDArray, str]:
    """3D plane fit: z = a·x + b·y + c
    
    Returns:
        Tuple of (text, z_fitted, equation)
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
    return param_text, z_fitted, equation
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
   from typing import List, Optional, Tuple
   
   def my_function(t: Numeric, a: float) -> Numeric:
       """Function description: y = ..."""
       ...
   
   def my_fit(
       data: DataLike, x_name: str, y_name: str,
       initial_guess_override: Optional[List[Optional[float]]] = None,
       bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
   ) -> Tuple[str, NDArray, str]:
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
   def fit_example(...) -> Tuple[str, NDArray, str]:
       """Example fit: y = a·exp(b·x)
       
       Returns:
           Tuple (text, y_fitted, equation) from generic_fit.
       """
       ...
   ```

4. **Error Handling**: `generic_fit` raises `FittingError` on failure. You can wrap your fit in try/except to log or re-raise; the workflow controller already handles errors from the fit function.

### Testing

Create a test file in `tests/` directory:

```python
# tests/test_exponential_function.py
import numpy as np
import pytest
from fitting.functions import fit_exponential_function
from fitting.functions.special import _exponential_function as exponential_function

def test_exponential_function():
    """Test exponential model calculation."""
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
    
    param_text, y_fitted, equation = fit_exponential_function(data, 'x', 'y')
    
    # Check R² is in the text and fitted values are close
    assert 'R²' in param_text
    
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
# 1. Define model (in the right module under fitting/functions/)
def power_function(t: Numeric, a: float, n: float) -> Numeric:
    """Power function: y = a * t^n"""
    return a * (t ** n)

# 2. Create fitting wrapper (same module)
def fit_power(
    data: DataLike, x_name: str, y_name: str,
    initial_guess_override=None, bounds_override=None,
) -> Tuple[str, NDArray, str]:
    """Power fit: y = a·x^n. Returns (text, y_fitted, equation)."""
    from fitting.functions._base import (
        generic_fit,
        get_equation_format_for_function,
        get_equation_param_names_for_function,
    )
    return generic_fit(
        data, x_name, y_name,
        fit_func=power_function,
        param_names=get_equation_param_names_for_function('fit_power'),
        equation_template=get_equation_format_for_function('fit_power'),
    )

# 3. Export fit_power in fitting/functions/__init__.py
# 4. Register in config/equations.yaml (function, formula, format, param_names)
# 5. Add translations in src/locales/ (en, es, de)
```

### Pattern 2: Function with Estimation

For complex functions needing initial guesses, use estimators from `_base` (or add one in `estimators.py` and re-export from `_base`) and `merge_initial_guess` / `merge_bounds`:

```python
from fitting.functions._base import (
    estimate_trigonometric_parameters,
    generic_fit,
    get_equation_format_for_function,
    get_equation_param_names_for_function,
    merge_initial_guess,
)

def damped_sine_function(t: Numeric, a: float, b: float, c: float) -> Numeric:
    """Damped sine: y = a·exp(-c·t)·sin(b·t)"""
    return a * np.exp(-c * t) * np.sin(b * t)

def fit_damped_sine(
    data: DataLike, x_name: str, y_name: str,
    initial_guess_override=None, bounds_override=None,
) -> Tuple[str, NDArray, str]:
    """Damped sine fit. Returns (text, y_fitted, equation)."""
    x, y = data[x_name], data[y_name]
    a0, b0 = estimate_trigonometric_parameters(x, y)
    c0 = 0.1
    initial_guess = merge_initial_guess([a0, b0, c0], initial_guess_override)
    return generic_fit(
        data, x_name, y_name,
        fit_func=damped_sine_function,
        param_names=get_equation_param_names_for_function('fit_damped_sine'),
        equation_template=get_equation_format_for_function('fit_damped_sine'),
        initial_guess=initial_guess,
    )
```

### Pattern 3: Specialized Function

For functions with constraints or special handling, use `curve_fit` directly and build the same return tuple `(text, y_fitted, equation[, fit_info])` that `generic_fit` returns (include R² in the text). See existing implementations in `fitting/functions/special.py` for examples with bounds and custom estimators.

## Example: Complete Implementation

Here's a complete example adding a Stretched Exponential function.

**1. Add to `fitting/functions/special.py`:**

```python
def _stretched_exponential_function(t: Numeric, a: float, tau: float, beta: float) -> Numeric:
    """Stretched exponential (Kohlrausch): y = a * exp(-(t/tau)^beta)"""
    return a * np.exp(-(t / tau) ** beta)

def fit_stretched_exponential(
    data: DataLike,
    x_name: str,
    y_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Tuple[str, NDArray, str]:
    """Stretched exponential fit. Returns (text, y_fitted, equation)."""
    x = data[x_name]
    y = data[y_name]
    a0 = float(y[0])
    tau0 = float(x[len(x) // 2])
    beta0 = 1.0
    initial_guess = merge_initial_guess([a0, tau0, beta0], initial_guess_override)
    return generic_fit(
        data, x_name, y_name,
        fit_func=_stretched_exponential_function,
        param_names=get_equation_param_names_for_function('fit_stretched_exponential'),
        equation_template=get_equation_format_for_function('fit_stretched_exponential'),
        initial_guess=initial_guess,
    )
```

**2. Export in `fitting/functions/__init__.py`:**  
Add `fit_stretched_exponential` to the `from .special import ...` list and to `__all__`.

**3. Add to `config/equations.yaml`:**

```yaml
stretched_exponential_function:
  function: fit_stretched_exponential
  formula: "y = a·exp(-(x/τ)^β)"
  format: "y={a} exp(-(x/{tau})^{beta})"
  param_names: [a, tau, beta]
```

**4. Add translations** in `src/locales/en.json`, `es.json`, and `de.json` under the `equations` key:

```json
"stretched_exponential_function": "Stretched Exponential (Kohlrausch)"
```

**5. Test:** Create test data (e.g. in `input/stretched_exp_test.csv`) and run the app (Tkinter or Streamlit) to verify the new equation appears and fits correctly.

## Next Steps

- **Study existing functions**: Look at the modules under `fitting/functions/` for more examples
- **Test thoroughly**: Create synthetic data with known parameters
- **Document well**: Write clear docstrings and comments
- **Contribute**: Submit your functions as pull requests to help others!

For more advanced customization, see [Customizing the Fitting Core](customization.md).

---

*Have questions? Open an issue on GitHub or check the [API Documentation](api/index).*
