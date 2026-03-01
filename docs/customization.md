# Customizing the Fitting Core

This guide explains how to replace or modify the curve fitting engine in RegressionLab. By default, RegressionLab uses SciPy's `curve_fit` function, but you may want to use a different optimization library for specific needs.

## Overview

RegressionLab's fitting architecture is modular, making it relatively easy to swap out the optimization backend. This guide covers:

1. **Understanding the current architecture**
2. **Why you might want to change it**
3. **How to replace SciPy with another library**
4. **Alternative optimization libraries**
5. **Performance considerations**

## Current Architecture

### How Fitting Works Now

RegressionLab's fitting pipeline:

```
User Interface (Tkinter/Streamlit)
        ↓
Fitting Wrapper Functions (ajlineal, ajsin, etc.)
        ↓
Generic Fit Utility (generic_fit)
        ↓
SciPy curve_fit
        ↓
Results (parameters, uncertainties, fitted curve)
```

### Key File: `fitting_utils.py`

The core fitting logic is in `src/fitting/fitting_utils.py`:

```python
def generic_fit(func, x, y, uy=None, p0=None):
    """
    Generic fitting function using scipy.optimize.curve_fit.
    
    Args:
        func: Mathematical function to fit
        x: Independent variable data
        y: Dependent variable data
        uy: Uncertainties in y (optional)
        p0: Initial parameter guess (optional)
        
    Returns:
        params: Fitted parameters
        y_fitted: Fitted y values
        r_squared: Coefficient of determination
    """
    from scipy.optimize import curve_fit
    
    # Prepare weights from uncertainties
    sigma = uy if uy is not None else None
    
    # Perform optimization
    popt, pcov = curve_fit(
        func, x, y,
        p0=p0,
        sigma=sigma,
        absolute_sigma=True if sigma is not None else False
    )
    
    # Calculate fitted values
    y_fitted = func(x, *popt)
    
    # Calculate R² and RMSE (residuals computed once and reused)
    residuals_sq = (y - y_fitted) ** 2
    ss_res = np.sum(residuals_sq)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    rmse = float(np.sqrt(np.mean(residuals_sq)))

    return popt, y_fitted, r_squared
```

This function is the **single point of control** for the optimization backend. Equation lookups (`get_equation_format_for_function`, `get_equation_param_names_for_function`) use O(1) reverse dicts built at module load, so there is no performance cost when resolving equations by function name.

## Why Change the Fitting Core?

### Reasons to Use a Different Library

1. **Performance**: Some libraries are faster for specific problem types
2. **Robustness**: Better handling of difficult optimization problems
3. **Features**: Access to different optimization algorithms (global optimization, constraints, etc.)
4. **Licensing**: Some libraries have different licenses
5. **Custom needs**: Specialized algorithms for your domain

### Popular Alternatives

| Library | Pros | Cons |
|---------|------|------|
| **lmfit** | High-level API, parameter constraints, many models | Additional dependency |
| **scipy.optimize.least_squares** | More options than curve_fit, robust loss functions | Lower-level API |
| **scipy.optimize.minimize** | General optimization, many algorithms | Not specialized for curve fitting |
| **PyGMO** | Global optimization, parallel evaluation | Complex, heavy dependency |
| **NLopt** | Fast, many algorithms, constraints | C library binding, harder to install |
| **TensorFlow/PyTorch** | GPU acceleration, automatic differentiation | Overkill for simple fits, steep learning curve |

## How to Replace the Fitting Core

### Method 1: Modify `generic_fit` Function

This is the recommended approach as it requires minimal changes to the codebase.

#### Example: Using lmfit

**Step 1: Install lmfit**

```bash
pip install lmfit
```

Add to `requirements.txt`:
```
lmfit>=1.2.0
```

**Step 2: Create Alternative Generic Fit**

Create a new function in `fitting_utils.py`:

```python
def generic_fit_lmfit(func, x, y, uy=None, p0=None):
    """
    Generic fitting using lmfit library.
    
    lmfit provides more control over parameter bounds, constraints,
    and fitting statistics compared to scipy.curve_fit.
    
    Args:
        func: Mathematical function to fit
        x: Independent variable data
        y: Dependent variable data
        uy: Uncertainties in y (optional, used as weights)
        p0: Initial parameter guess (optional)
        
    Returns:
        params: Fitted parameters (as ndarray)
        y_fitted: Fitted y values
        r_squared: Coefficient of determination
    """
    from lmfit import Model
    import inspect
    
    # Create lmfit Model from function
    model = Model(func, independent_vars=['x'])
    
    # Get parameter names from function signature
    sig = inspect.signature(func)
    param_names = [p for p in sig.parameters.keys() if p != 'x' and p != 't']
    
    # Create parameters object
    params = model.make_params()
    
    # Set initial values if provided
    if p0 is not None:
        for name, value in zip(param_names, p0):
            params[name].value = value
    
    # Perform fit
    if uy is not None:
        # Weighted fit
        result = model.fit(y, params, x=x, weights=1.0/uy)
    else:
        # Unweighted fit
        result = model.fit(y, params, x=x)
    
    # Extract results
    popt = np.array([result.params[name].value for name in param_names])
    y_fitted = result.best_fit
    r_squared = 1 - result.residual.var() / np.var(y)
    
    return popt, y_fitted, r_squared
```

**Step 3: Switch to New Implementation**

Option A - Replace original:
```python
# In fitting_utils.py, rename functions:
def generic_fit_scipy(func, x, y, uy=None, p0=None):
    # ... original scipy implementation ...
    pass

# Make generic_fit use lmfit
generic_fit = generic_fit_lmfit
```

Option B - Use configuration flag:
```python
# In config/constants.py or config/env.py
USE_LMFIT = True  # Set to False to use SciPy

# In fitting_utils.py
def generic_fit(func, x, y, uy=None, p0=None):
    from config import USE_LMFIT
    
    if USE_LMFIT:
        return generic_fit_lmfit(func, x, y, uy, p0)
    else:
        return generic_fit_scipy(func, x, y, uy, p0)
```

#### Example: Using scipy.optimize.least_squares

For more control and robust loss functions:

```python
def generic_fit_least_squares(func, x, y, uy=None, p0=None, loss='linear'):
    """
    Generic fitting using scipy.optimize.least_squares.
    
    Provides more robust loss functions and better convergence for
    difficult problems.
    
    Args:
        func: Mathematical function to fit
        x: Independent variable data
        y: Dependent variable data
        uy: Uncertainties in y (used as weights)
        p0: Initial parameter guess (required!)
        loss: Loss function ('linear', 'soft_l1', 'huber', 'cauchy', 'arctan')
        
    Returns:
        params: Fitted parameters
        y_fitted: Fitted y values
        r_squared: Coefficient of determination
    """
    from scipy.optimize import least_squares
    import inspect
    
    # Validate inputs
    if p0 is None:
        raise ValueError("least_squares requires initial parameter guess (p0)")
    
    # Get number of parameters
    sig = inspect.signature(func)
    n_params = len(sig.parameters) - 1  # Subtract independent variable
    
    # Define residual function
    def residuals(params):
        y_model = func(x, *params)
        if uy is not None:
            # Weighted residuals
            return (y - y_model) / uy
        else:
            return y - y_model
    
    # Perform optimization
    result = least_squares(
        residuals,
        p0,
        loss=loss,  # Robust loss function
        f_scale=1.0,  # Scale parameter for loss
        max_nfev=10000  # Maximum function evaluations
    )
    
    # Extract results
    popt = result.x
    y_fitted = func(x, *popt)
    
    # Calculate R²
    ss_res = np.sum((y - y_fitted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return popt, y_fitted, r_squared
```

**Robust Loss Functions**:
- `'linear'`: Standard least squares (default, same as curve_fit)
- `'soft_l1'`: Robust to outliers, smooth transition
- `'huber'`: Robust to outliers, less aggressive
- `'cauchy'`: Very robust to outliers, but can converge slowly
- `'arctan'`: Similar to Cauchy

### Method 2: Create Custom Fitting Wrapper

For specialized needs, create domain-specific fitting functions:

```python
def generic_fit_global(func, x, y, uy=None, bounds=None):
    """
    Global optimization for multimodal functions.
    
    Uses differential evolution to find global minimum,
    useful when curve_fit gets stuck in local minima.
    
    Args:
        func: Mathematical function to fit
        x: Independent variable data
        y: Dependent variable data
        uy: Uncertainties (optional)
        bounds: Parameter bounds as list of (min, max) tuples (required!)
        
    Returns:
        params: Fitted parameters
        y_fitted: Fitted y values
        r_squared: R² value
    """
    from scipy.optimize import differential_evolution
    
    if bounds is None:
        raise ValueError("Global optimization requires parameter bounds")
    
    # Define objective function (minimize sum of squared residuals)
    def objective(params):
        y_model = func(x, *params)
        if uy is not None:
            residuals = (y - y_model) / uy
        else:
            residuals = y - y_model
        return np.sum(residuals ** 2)
    
    # Run global optimization
    result = differential_evolution(
        objective,
        bounds,
        seed=42,  # Reproducibility
        maxiter=1000,
        atol=1e-7,
        tol=0.01
    )
    
    # Extract results
    popt = result.x
    y_fitted = func(x, *popt)
    
    # Calculate R²
    ss_res = np.sum((y - y_fitted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return popt, y_fitted, r_squared
```

### Method 3: Bayesian Fitting with MCMC

For uncertainty quantification with complex models:

```python
def generic_fit_mcmc(func, x, y, uy=None, p0=None):
    """
    Bayesian fitting using MCMC (requires emcee library).
    
    Provides full posterior distributions for parameters,
    not just point estimates.
    
    Args:
        func: Mathematical function to fit
        x: Independent variable data
        y: Dependent variable data
        uy: Uncertainties in y (required!)
        p0: Initial parameter guess
        
    Returns:
        params: Median parameter values
        y_fitted: Fitted y values
        r_squared: R² value
    """
    try:
        import emcee
    except ImportError:
        raise ImportError("MCMC fitting requires emcee: pip install emcee")
    
    if uy is None:
        uy = np.ones_like(y) * 0.1 * np.std(y)
    
    n_params = len(p0)
    
    # Define log-likelihood
    def log_likelihood(params):
        y_model = func(x, *params)
        return -0.5 * np.sum(((y - y_model) / uy) ** 2)
    
    # Define log-prior (uniform priors)
    def log_prior(params):
        # Simple bounds check
        if np.all(np.isfinite(params)):
            return 0.0
        return -np.inf
    
    # Define log-probability
    def log_probability(params):
        lp = log_prior(params)
        if not np.isfinite(lp):
            return -np.inf
        return lp + log_likelihood(params)
    
    # Initialize walkers
    n_walkers = max(32, 2 * n_params)
    pos = p0 + 1e-4 * np.random.randn(n_walkers, n_params)
    
    # Run MCMC
    sampler = emcee.EnsembleSampler(n_walkers, n_params, log_probability)
    sampler.run_mcmc(pos, 5000, progress=False)
    
    # Get results (discard burn-in)
    samples = sampler.get_chain(discard=1000, flat=True)
    popt = np.median(samples, axis=0)
    
    # Calculate fitted values and R²
    y_fitted = func(x, *popt)
    ss_res = np.sum((y - y_fitted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return popt, y_fitted, r_squared
```

## Advanced: Parameter Constraints and Bounds

### Adding Bounds to Existing Functions

Modify individual fitting functions to include bounds:

```python
def ajlineal_con_n_bounded(data, x_name: str, y_name: str):
    """Linear fit with slope constrained to be positive."""
    from scipy.optimize import curve_fit
    
    x = data[x_name].values
    y = data[y_name].values
    uy = data[f'u{y_name}'].values if f'u{y_name}' in data.columns else None
    
    # Constrain: m > 0, n unrestricted
    bounds = ([0, -np.inf], [np.inf, np.inf])
    
    popt, _ = curve_fit(
        func_lineal_con_n,
        x, y,
        sigma=uy,
        bounds=bounds,
        absolute_sigma=True if uy is not None else False
    )
    
    # ... rest of function ...
```

### Creating a Configurable Bounds System

Add bounds to function metadata:

```python
# In config/constants.py
EQUATION_BOUNDS = {
    'exponential_decay': ([0, 0], [np.inf, np.inf]),  # a > 0, b > 0
    'sine_function': ([-np.inf, 0], [np.inf, np.inf]),  # b > 0
    # Add bounds for other equations
}

# In fitting_utils.py
def generic_fit_with_bounds(func, x, y, uy=None, p0=None, equation_name=None):
    """Generic fit with optional bounds from configuration."""
    from scipy.optimize import curve_fit
    from config import EQUATION_BOUNDS
    
    # Get bounds if available
    bounds = EQUATION_BOUNDS.get(equation_name, (-np.inf, np.inf))
    
    sigma = uy if uy is not None else None
    
    popt, _ = curve_fit(
        func, x, y,
        p0=p0,
        sigma=sigma,
        bounds=bounds,
        absolute_sigma=True if sigma is not None else False
    )
    
    y_fitted = func(x, *popt)
    r_squared = 1 - (np.sum((y - y_fitted)**2) / np.sum((y - np.mean(y))**2))
    
    return popt, y_fitted, r_squared
```

## Performance Considerations

### Benchmarking Different Backends

Create a benchmark script:

```python
# benchmark_fitting.py
import time
import numpy as np
import pandas as pd
from fitting.fitting_utils import generic_fit, generic_fit_lmfit

# Generate test data
x = np.linspace(0, 10, 1000)
y = 2.5 * x + 1.3 + np.random.normal(0, 0.5, 1000)

def func_linear(t, m, n):
    return m * t + n

# Benchmark scipy
start = time.time()
for _ in range(100):
    params, y_fit, r2 = generic_fit(func_linear, x, y)
scipy_time = time.time() - start

# Benchmark lmfit
start = time.time()
for _ in range(100):
    params, y_fit, r2 = generic_fit_lmfit(func_linear, x, y)
lmfit_time = time.time() - start

print(f"SciPy:  {scipy_time:.3f} seconds (100 fits)")
print(f"lmfit:  {lmfit_time:.3f} seconds (100 fits)")
print(f"Speedup: {lmfit_time/scipy_time:.2f}x")
```

### Optimization Tips

1. **Vectorize operations**: Use NumPy arrays, not loops
2. **Good initial guesses**: Reduces iterations
3. **Appropriate tolerances**: Don't over-optimize
4. **Warm starts**: Reuse previous fits as initial guesses

Example with warm starts:

```python
def batch_fit_with_warm_start(files, equation_type):
    """Fit multiple files using previous result as initial guess."""
    p0 = None  # Start with no guess
    
    results = []
    for file in files:
        data = load_data(file)
        x, y = data['x'].values, data['y'].values
        
        params, y_fit, r2 = generic_fit(func, x, y, p0=p0)
        
        # Use current result as next initial guess
        p0 = params
        
        results.append((params, r2))
    
    return results
```

## Handling Uncertainty Propagation

### Using uncertainties Package

For automatic error propagation:

```python
def generic_fit_with_uncertainties(func, x, y, uy=None, p0=None):
    """
    Fit and return parameter uncertainties using uncertainties package.
    
    Returns parameters as ufloat objects with uncertainty.
    """
    try:
        from uncertainties import ufloat, correlated_values
    except ImportError:
        raise ImportError("Install uncertainties: pip install uncertainties")
    
    from scipy.optimize import curve_fit
    
    # Perform fit
    popt, pcov = curve_fit(func, x, y, p0=p0, sigma=uy, absolute_sigma=True if uy is not None else False)
    
    # Create uncertain parameters
    params_with_uncertainty = correlated_values(popt, pcov)
    
    # Calculate fitted values
    y_fitted = func(x, *popt)
    r_squared = 1 - (np.sum((y - y_fitted)**2) / np.sum((y - np.mean(y))**2))
    
    return params_with_uncertainty, y_fitted, r_squared

# Example usage
params_unc, y_fit, r2 = generic_fit_with_uncertainties(func_linear, x, y, uy)
m, n = params_unc
print(f"Slope: {m}")  # Prints: 2.50+/-0.03
print(f"Intercept: {n}")  # Prints: 1.30+/-0.15
```

## Configuration File Approach

Create a comprehensive configuration system:

```python
# config/constants.py or new config/fitting_config.py
FITTING_CONFIG = {
    'backend': 'scipy',  # Options: 'scipy', 'lmfit', 'least_squares'
    'scipy_options': {
        'method': 'lm',  # Levenberg-Marquardt
        'max_nfev': 10000,
    },
    'least_squares_options': {
        'loss': 'soft_l1',  # Robust loss
        'f_scale': 1.0,
    },
    'lmfit_options': {
        'method': 'leastsq',
    },
}

# fitting_utils.py
def generic_fit(func, x, y, uy=None, p0=None):
    """Generic fit that uses configured backend."""
    from config import FITTING_CONFIG
    
    backend = FITTING_CONFIG['backend']
    
    if backend == 'scipy':
        return generic_fit_scipy(func, x, y, uy, p0)
    elif backend == 'lmfit':
        return generic_fit_lmfit(func, x, y, uy, p0)
    elif backend == 'least_squares':
        return generic_fit_least_squares(func, x, y, uy, p0)
    else:
        raise ValueError(f"Unknown fitting backend: {backend}")
```

Users can then switch backends by editing the config package (e.g. `config/constants.py`) without modifying code.

## Testing New Backends

Always test thoroughly when changing the fitting core:

```python
# tests/test_fitting_backends.py
import pytest
import numpy as np
from fitting.fitting_utils import generic_fit, generic_fit_lmfit

def test_backends_agree():
    """Test that different backends give similar results."""
    # Generate perfect linear data
    x = np.linspace(0, 10, 50)
    y = 2.0 * x + 3.0
    
    def func(t, a, b):
        return a * t + b
    
    # Fit with scipy
    params_scipy, _, _ = generic_fit(func, x, y)
    
    # Fit with lmfit
    params_lmfit, _, _ = generic_fit_lmfit(func, x, y)
    
    # Check agreement
    np.testing.assert_array_almost_equal(params_scipy, params_lmfit, decimal=6)

def test_with_noise():
    """Test fitting with noisy data."""
    x = np.linspace(0, 10, 100)
    y = 2.5 * x + 1.0 + np.random.normal(0, 0.5, 100)
    
    def func(t, a, b):
        return a * t + b
    
    params, y_fit, r2 = generic_fit(func, x, y)
    
    # Check reasonable results
    assert 2.0 < params[0] < 3.0  # Slope near 2.5
    assert 0.5 < params[1] < 1.5  # Intercept near 1.0
    assert r2 > 0.95  # Good fit
```

## Summary

| Approach | Difficulty | Flexibility | When to Use |
|----------|------------|-------------|-------------|
| Modify `generic_fit` | Easy | Low | Simple backend swap |
| Add backend option | Medium | Medium | Support multiple backends |
| Custom fitting functions | Medium | High | Specialized needs per equation |
| Configuration system | Hard | Very High | Production deployments |

**Recommendations**:
- **Start simple**: Modify `generic_fit` directly
- **For production**: Use configuration system
- **For research**: Create specialized fitting functions
- **Always test**: Verify results match expectations

## Next Steps

- **Test thoroughly**: Use known data to validate new backend
- **Benchmark**: Compare performance with original
- **Document**: Explain why you chose a different backend
- **Contribute**: Share your improvements with the community!

---

*For more technical details, see the [API Documentation](api/index).*
