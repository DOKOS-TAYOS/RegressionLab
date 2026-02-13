# API Documentation

This section provides technical documentation for RegressionLab's Python API. It's intended for developers who want to understand the codebase, contribute to the project, or integrate RegressionLab into their own applications.

## Architecture Overview

RegressionLab follows a modular architecture with clear separation of concerns:

```
RegressionLab/
├── src/
│   ├── config/                # Configuration package
│   │   ├── color_utils.py     # Hex color utilities (lighten, muted)
│   │   ├── env.py             # Environment and .env
│   │   ├── theme.py           # UI theme and plot style
│   │   ├── paths.py           # Paths and output
│   │   ├── constants.py       # Version, signals, EQUATIONS (from YAML)
│   │   └── equations.yaml     # Equation definitions (function, formula, format, param_names)
│   ├── i18n.py                # Internationalization
│   ├── main_program.py        # Entry point for Tkinter app
│   │
│   ├── fitting/               # Curve fitting core
│   │   ├── functions/         # Mathematical and fit_* functions
│   │   │   ├── _base.py
│   │   │   ├── polynomials.py
│   │   │   ├── trigonometric.py
│   │   │   ├── inverse.py
│   │   │   └── special.py
│   │   ├── fitting_functions/ # Re-exports (fitting.fitting_functions)
│   │   ├── fitting_utils.py
│   │   ├── estimators.py
│   │   ├── workflow_controller.py
│   │   └── custom_function_evaluator.py
│   │
│   ├── frontend/              # User interface (Tkinter)
│   │   ├── ui_main_menu.py
│   │   ├── image_utils.py
│   │   ├── keyboard_nav.py    # Keyboard navigation
│   │   └── ui_dialogs/        # Dialog package
│   │       ├── data_selection.py
│   │       ├── equation.py
│   │       ├── help.py
│   │       ├── config_dialog.py
│   │       ├── result.py
│   │       └── tooltip.py
│   │
│   ├── data_analysis/         # Transforms and cleaning
│   │   ├── _utils.py          # Shared get_numeric_columns
│   │   ├── transforms.py
│   │   └── cleaning.py
│   │
│   ├── loaders/               # Data loading
│   │   ├── data_loader.py
│   │   ├── loading_utils.py
│   │   └── saving_utils.py
│   │
│   ├── plotting/              # Visualization
│   │   └── plot_utils.py
│   │
│   ├── streamlit_app/         # Web interface
│   │   ├── app.py             # Entry point
│   │   ├── theme.py           # Streamlit theme config
│   │   └── sections/          # UI sections
│   │       ├── sidebar.py
│   │       ├── data.py
│   │       ├── fitting.py
│   │       ├── results.py
│   │       ├── help_section.py
│   │       └── modes.py
│   │
│   ├── locales/               # Translation JSON (en, es, de)
│   │
│   └── utils/                 # Utilities
│       ├── exceptions.py
│       ├── logger.py
│       └── validators.py
```

## Module Reference

### Core Modules

- **[config](config.md)** - Configuration management and application constants
- **[i18n](i18n.md)** - Internationalization and translation system

### Fitting Modules

- **[fitting.fitting_functions](fitting_functions.md)** - Mathematical functions and curve fitting implementations
- **[fitting.fitting_utils](fitting_utils.md)** - Generic fitting utilities and helpers
- **[fitting.workflow_controller](workflow_controller.md)** - Orchestrates fitting workflows and modes
- **[fitting.custom_function_evaluator](custom_function_evaluator.md)** - Evaluates user-defined custom formulas
- **[fitting.estimators](estimators.md)** - Parameter estimation functions for initial guesses

### Data Loading and Saving

- **[loaders.data_loader](data_loader.md)** - High-level data loading interface
- **[loaders.loading_utils](loading_utils.md)** - CSV and Excel file readers
- **[loaders.saving_utils](saving_utils.md)** - Save DataFrame to CSV, TXT, XLSX

### Data Analysis

- **[data_analysis](data_analysis.md)** - Transforms (FFT, DCT, log, exp, etc.) and cleaning (drop NaN, outliers, etc.). Used by the View Data window in Tkinter and Streamlit.

### Visualization

- **[plotting.plot_utils](plot_utils.md)** - Plot generation and styling (2D fit, pair, residual, 3D)

### User Interface

- **[frontend.ui_main_menu](ui_main_menu.md)** - Main menu and navigation (Tkinter)
- **[frontend.ui_dialogs](ui_dialogs.md)** - Dialog windows and user input (Tkinter)
- **[frontend.image_utils](image_utils.md)** - Image loading and scaling utilities
- **[frontend.keyboard_nav](keyboard_nav.md)** - Keyboard navigation utilities
- **[streamlit_app.app](streamlit_app.md)** - Web interface (Streamlit)

### Utilities

- **[utils.exceptions](exceptions.md)** - Custom exception classes
- **[utils.logger](logger.md)** - Logging configuration and utilities
- **[utils.validators](validators.md)** - Data validation functions

## Quick Start for Developers

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-repo/RegressionLab.git
cd RegressionLab

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements-dev.txt   # or: pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Running the Application

```bash
# From project root (activate .venv first if using setup scripts)
# Bin launchers require .venv (run setup.bat / setup.sh first).
# Tkinter (desktop)
python src/main_program.py
# Or: bin\run.bat (Windows) / ./bin/run.sh (Linux/macOS)

# Streamlit (web)
streamlit run src/streamlit_app/app.py
# Or: bin\run_streamlit.bat (Windows) / ./bin/run_streamlit.sh (Linux/macOS)
```

### Code Style

RegressionLab follows PEP 8 with these conventions:

- **Line length**: 100 characters max
- **Docstrings**: Google style (use "Examples:" for example blocks)
- **Type hints**: Required for function signatures
- **Imports**: Sorted alphabetically, grouped by standard/third-party/local. Cross-package imports use the package root (e.g. `from config import X`, `from loaders import Y`). Imports within the same package use full module paths (e.g. `from config.constants import Z`, `from loaders.loading_utils import csv_reader`) to avoid circular references

Example:

```python
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray


def example_function(data: NDArray, threshold: float = 0.5) -> Tuple[NDArray, float]:
    """
    Short description of what the function does.
    
    Longer explanation if needed, including mathematical
    formulation or algorithmic details.
    
    Args:
        data: Input data array
        threshold: Cutoff value for filtering
        
    Returns:
        Tuple of (filtered_data, metric_value)
        
    Raises:
        ValueError: If data is empty or threshold is negative
    """
    if len(data) == 0:
        raise ValueError("Data cannot be empty")
    
    filtered = data[data > threshold]
    metric = np.mean(filtered)
    
    return filtered, metric
```

## Common Development Tasks

### Adding a New Fitting Function

See [Extending RegressionLab](../extending.md) for detailed instructions.

Quick summary:
1. Add mathematical function in `fitting/functions/` (e.g. `polynomials.py`, `special.py`)
2. Create fitting wrapper function
3. Export the fit function from `src/fitting/functions/__init__.py`, then register in `config/equations.yaml` (add entry with `function`, `formula`, `format`, `param_names`) and add translations in `src/locales/`
4. Test thoroughly

### Modifying the UI

**Tkinter**:
- Main menu: Edit `frontend/ui_main_menu.py`
- Keyboard navigation: Edit `frontend/keyboard_nav.py` (see [keyboard_nav](keyboard_nav.md))
- Image utilities: Edit `frontend/image_utils.py` (see [image_utils](image_utils.md))
- Dialogs: Edit modules in `frontend/ui_dialogs/` (e.g. `data_selection.py`, `equation.py`)
- Styling: Configure in `.env` file

**Streamlit**:
- Entry point: `streamlit_app/app.py`; UI logic in `streamlit_app/sections/`
- Theme: `streamlit_app/theme.py`
- CSS in `SIDEBAR_CSS` in `sections/sidebar.py`
- Add new modes in `sections/modes.py`

### Adding a New Data Format

1. Create reader function in `loaders/loading_utils.py`
2. Register it in the `FILE_TYPE_READERS` dict in `loaders/data_loader.py` (key = file type, value = reader function)
3. Add file type filter to `open_load_dialog()` in `frontend/ui_dialogs/load_data_dialog.py`
4. Test with sample data

### Changing Plot Style

- **Per-plot**: Pass parameters to `create_plot()` in `plotting/plot_utils.py`
- **Globally**: Configure in `.env` file
- **Programmatically**: Modify `PLOT_CONFIG` and related settings in `config/theme.py`

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py               # Pytest fixtures
├── run_tests.py              # Test runner (invokes pytest)
├── test_config.py            # Configuration
├── test_custom_function_evaluator.py
├── test_data_loader.py       # Data loading
├── test_exceptions.py
├── test_fitting_functions.py  # Curve fitting
├── test_fitting_utils.py
├── test_i18n.py
├── test_loading_utils.py
├── test_logger.py
├── test_validators.py        # Validation
└── test_workflow_controller.py
```

Run tests via `pytest tests/` or `python tests/run_tests.py`, or use `bin/run_tests.bat` (Windows) / `bin/run_tests.sh` (Linux/macOS). The bin test launchers require `.venv` (run setup first).

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_fitting_functions.py

# Specific test
pytest tests/test_fitting_functions.py::test_linear_fit

# With coverage
pytest tests/ --cov=src

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x
```

### Writing Tests

Example test:

```python
import numpy as np
import pandas as pd
import pytest
from fitting.fitting_functions import func_lineal, ajlineal


def test_func_lineal_scalar():
    """Test linear function with scalar input."""
    result = func_lineal(5.0, 2.0)
    assert result == 10.0


def test_func_lineal_array():
    """Test linear function with array input."""
    t = np.array([1, 2, 3])
    result = func_lineal(t, 2.0)
    expected = np.array([2, 4, 6])
    np.testing.assert_array_equal(result, expected)


def test_ajlineal_perfect_fit():
    """Test linear fitting with perfect data."""
    # Generate perfect linear data
    x = np.linspace(0, 10, 50)
    y = 3.0 * x  # y = 3*x
    
    data = pd.DataFrame({'x': x, 'y': y})
    
    text, y_fitted, equation, *_ = ajlineal(data, 'x', 'y')
    
    # Check R² is nearly perfect (R² is included in text output)
    assert 'R²' in text or 'R^2' in text
    
    # Check fitted values match data
    np.testing.assert_array_almost_equal(y_fitted, y, decimal=10)


@pytest.mark.parametrize("slope,n_points", [
    (1.0, 10),
    (2.5, 50),
    (-1.5, 100),
])
def test_ajlineal_various_slopes(slope, n_points):
    """Test linear fitting with various slopes and data sizes."""
    x = np.linspace(0, 10, n_points)
    y = slope * x + np.random.normal(0, 0.1, n_points)
    
    data = pd.DataFrame({'x': x, 'y': y})
    
    text, _, _ = ajlineal(data, 'x', 'y')
    
    # Even with noise, should be good fit (R² is included in text output)
    assert 'R²' in text or 'R^2' in text
```

## API Conventions

### Return Values

**Fitting functions** return a 4-tuple from `generic_fit` (and from `get_fitting_function` / custom evaluator):
```python
(text: str, y_fitted: NDArray, equation: str, fit_info: Optional[dict])
```
Callers that only need the main result use the first three; `fit_info` holds fit metadata. `text` contains formatted parameters, uncertainties, R², and statistics.

**Data loaders** return pandas DataFrame

**Plot functions** return path to saved plot (str or Path)

### Error Handling

- Use `FittingError` for curve fitting failures
- Use `DataLoadError` for data loading problems
- Use standard Python exceptions for other errors
- Always log errors before raising

Example:
```python
from utils.exceptions import FittingError
from utils.logger import get_logger

logger = get_logger(__name__)

def risky_operation(data):
    try:
        result = perform_fit(data)
        return result
    except RuntimeError as e:
        logger.error(f"Fitting failed: {e}", exc_info=True)
        raise FittingError(f"Could not fit data: {str(e)}")
```

### Logging

Use the logger from `utils.logger`:

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed diagnostic information")
logger.info("General informational message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include traceback
logger.critical("Critical error")
```

### Type Hints

Always include type hints:

```python
from typing import Optional, List, Tuple, Callable
from numpy.typing import NDArray
import numpy as np

def process_data(
    data: NDArray[np.floating],
    threshold: float,
    callback: Optional[Callable[[float], None]] = None
) -> Tuple[NDArray[np.floating], List[int]]:
    """Process data and return results."""
    ...
```

## Performance Considerations

### NumPy Best Practices

- Use vectorized operations instead of loops
- Pre-allocate arrays when possible
- Use in-place operations to reduce memory

```python
# Bad - loop
result = []
for x_val in x:
    result.append(a * x_val + b)
result = np.array(result)

# Good - vectorized
result = a * x + b

# Bad - creates new array
data = data + 1

# Good - in-place
data += 1
```

### Caching

Use `functools.lru_cache` for expensive computations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param1: float, param2: float) -> float:
    """Cache results of expensive computation."""
    ...
```

### Lazy Imports

Import heavy libraries only when needed:

```python
def function_using_scipy():
    """Function that uses SciPy."""
    # Import here, not at module level
    from scipy.optimize import curve_fit
    
    result = curve_fit(...)
    return result
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: int, param2: str, param3: Optional[float] = None) -> bool:
    """
    Short one-line summary.
    
    Longer description with more details about what the function does,
    including any important algorithms or mathematical formulations.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        param3: Optional parameter with default value
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is negative
        KeyError: When param2 not found in database
        
    Examples:
        >>> example_function(5, "test")
        True
        >>> example_function(0, "hello", 3.14)
        False
        
    Note:
        Additional notes or warnings for users.
    """
    ...
```

## Module Details

For detailed documentation of each module, see the individual module pages:

- **Core**: [config](config.md), [i18n](i18n.md)
- **Fitting**: [fitting_functions](fitting_functions.md), [fitting_utils](fitting_utils.md), [workflow_controller](workflow_controller.md), [custom_function_evaluator](custom_function_evaluator.md), [estimators](estimators.md)
- **Loaders**: [data_loader](data_loader.md), [loading_utils](loading_utils.md), [saving_utils](saving_utils.md)
- **Data Analysis**: [data_analysis](data_analysis.md)
- **Plotting**: [plot_utils](plot_utils.md)
- **Frontend**: [ui_main_menu](ui_main_menu.md), [ui_dialogs](ui_dialogs.md), [image_utils](image_utils.md), [keyboard_nav](keyboard_nav.md), [streamlit_app](streamlit_app.md)
- **Utils**: [exceptions](exceptions.md), [logger](logger.md), [validators](validators.md)

## Contributing

See [Contributing Guide](../contributing.md) for:
- Code style guidelines
- Pull request process
- Development workflow
- Testing requirements

---

*Last updated: February 2026.*
