# fitting.custom_function_evaluator

Custom Function Evaluator Module for safe runtime evaluation of user-defined mathematical functions.

## Overview

The `custom_function_evaluator.py` module provides safe runtime evaluation of custom mathematical functions for curve fitting. It allows users to define their own mathematical formulas that are then evaluated and used for curve fitting operations.

## Key Features

- **Safe evaluation** with restricted namespace
- **Automatic conversion** of mathematical notation to NumPy functions
- **Integration** with the generic_fit function
- **No dynamic file generation** required

## Class: CustomFunctionEvaluator

### Constructor

#### `__init__(equation_str: str, parameter_names: List[str])`

Initialize the custom function evaluator.

**Parameters:**
- `equation_str`: Mathematical formula as string (e.g., "a*sin(x) + b")
- `parameter_names`: List of parameter names used in the formula

**Raises:**
- `ValidationError`: If parameter names are invalid
- `EquationError`: If equation cannot be parsed

**Example:**
```python
from fitting.custom_function_evaluator import CustomFunctionEvaluator

# Create evaluator for quadratic function
evaluator = CustomFunctionEvaluator("a*x**2 + b*x + c", ["a", "b", "c"])

# Create evaluator for exponential decay
evaluator = CustomFunctionEvaluator("a*exp(-b*x)", ["a", "b"])
```

### Methods

#### `fit(data: Union[dict, pd.DataFrame], x_name: str, y_name: str) -> Tuple[str, NDArray, str, Optional[dict]]`

Perform curve fitting using the custom function.

This method uses the generic_fit function from fitting_utils to perform the actual curve fitting with error propagation.

**Parameters:**
- `data`: Data dictionary or DataFrame containing x, y and their uncertainties
- `x_name`: Name of the independent variable
- `y_name`: Name of the dependent variable

**Returns:**
- Tuple of `(text, y_fitted, equation, fit_info)` (same as `generic_fit`):
  - `text`: Formatted text with parameters, uncertainties, R², and statistics
  - `y_fitted`: Array with fitted y values
  - `equation`: Formatted equation with parameter values
  - `fit_info`: Optional dict with fit metadata (for advanced use)

**Raises:**
- `FittingError`: If fitting fails
- `EquationError`: If equation evaluation fails

**Example:**
```python
from fitting.custom_function_evaluator import CustomFunctionEvaluator
import pandas as pd

# Create evaluator
evaluator = CustomFunctionEvaluator("a*x**2 + b", ["a", "b"])

# Load data
data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [2, 5, 10, 17]})

# Perform fit (use first three values if fit_info not needed)
text, y_fitted, equation, *_ = evaluator.fit(data, 'x', 'y')

print(f"Equation: {equation}")
print(f"Results:\n{text}")  # R² is included in the text output
```

#### `get_function() -> Callable`

Get the generated function for direct use.

**Returns:**
- The callable function that evaluates the formula

**Example:**
```python
evaluator = CustomFunctionEvaluator("a*sin(b*x)", ["a", "b"])

# Get the function
func = evaluator.get_function()

# Use directly with scipy.optimize.curve_fit
from scipy.optimize import curve_fit
import numpy as np

x_data = np.array([0, 1, 2, 3])
popt, pcov = curve_fit(func, x_data, y_data, p0=[1.0, 1.0])
```

## Mathematical Function Conversion

The module automatically converts standard mathematical notation to NumPy function calls using mappings from `config.MATH_FUNCTION_REPLACEMENTS`.

### Supported Conversions

| Mathematical Notation | NumPy Equivalent |
|----------------------|------------------|
| `ln(x)` | `np.log(x)` |
| `log(x)` | `np.log(x)` |
| `sin(x)` | `np.sin(x)` |
| `cos(x)` | `np.cos(x)` |
| `tan(x)` | `np.tan(x)` |
| `exp(x)` | `np.exp(x)` |
| `sqrt(x)` | `np.sqrt(x)` |

### Example Conversions

```python
# User input: "a*ln(x) + b"
# Converted to: "a*np.log(x) + b"

# User input: "a*sin(b*x) + c*cos(d*x)"
# Converted to: "a*np.sin(b*x) + c*np.cos(d*x)"
```

## Formula Syntax

### Valid Syntax

- **Variables**: `x` (independent variable), parameter names (e.g., `a`, `b`, `c`)
- **Operators**: `+`, `-`, `*`, `/`, `**` (power)
- **Functions**: Standard mathematical functions (automatically converted to NumPy)
- **Parentheses**: For grouping expressions

### Examples

```python
# Linear
"a*x + b"

# Quadratic
"a*x**2 + b*x + c"

# Exponential
"a*exp(-b*x)"

# Trigonometric
"a*sin(b*x + c)"

# Logarithmic
"a*ln(x) + b"

# Complex
"a*exp(-x/b) * sin(c*x + d)"
```

## Security

The evaluator uses a restricted namespace for security:

- **No builtins**: Only safe operations allowed
- **Restricted imports**: Only NumPy is available
- **Parameter validation**: Parameter names must be valid Python identifiers
- **Syntax checking**: Formula syntax is validated before evaluation

## Error Handling

### Common Errors

1. **Syntax Error**: Invalid formula syntax
   ```python
   # Error: "a*x +" (incomplete)
   # Raises: EquationError
   ```

2. **Division by Zero**: Formula evaluates to division by zero
   ```python
   # Error: "a/x" where x contains zeros
   # Raises: EquationError
   ```

3. **Invalid Parameters**: Parameter names are invalid
   ```python
   # Error: ["a b", "c"] (space in name)
   # Raises: ValidationError
   ```

4. **Parameter Count Mismatch**: Wrong number of parameters
   ```python
   # Error: Function expects 3 params, but 2 provided
   # Raises: EquationError
   ```

## Usage Examples

### Basic Custom Function

```python
from fitting.custom_function_evaluator import CustomFunctionEvaluator
import pandas as pd

# Define custom function: y = a*x^2 + b*x + c
evaluator = CustomFunctionEvaluator(
    "a*x**2 + b*x + c",
    ["a", "b", "c"]
)

# Create sample data
data = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [3, 7, 13, 21, 31],
    'ux': [0.1] * 5,
    'uy': [0.2] * 5
})

# Perform fit
text, y_fitted, equation, *_ = evaluator.fit(data, 'x', 'y')

print(equation)  # y=a*x**2 + b*x + c
print(f"Results:\n{text}")  # R² is included in the text output
```

### Exponential Decay

```python
# Exponential decay: y = a*exp(-b*x)
evaluator = CustomFunctionEvaluator(
    "a*exp(-b*x)",
    ["a", "b"]
)

data = pd.DataFrame({
    'x': [0, 1, 2, 3, 4],
    'y': [10, 6.7, 4.5, 3.0, 2.0],
    'ux': [0.1] * 5,
    'uy': [0.2] * 5
})

text, y_fitted, equation, *_ = evaluator.fit(data, 'x', 'y')
```

### Trigonometric Function

```python
# Sinusoidal: y = a*sin(b*x + c)
evaluator = CustomFunctionEvaluator(
    "a*sin(b*x + c)",
    ["a", "b", "c"]
)

data = pd.DataFrame({
    'x': [0, 1, 2, 3, 4],
    'y': [0, 1, 0, -1, 0],
    'ux': [0.1] * 5,
    'uy': [0.1] * 5
})

text, y_fitted, equation, *_ = evaluator.fit(data, 'x', 'y')
```

## Integration with Workflow

The custom function evaluator integrates seamlessly with the fitting workflow:

```python
from fitting.workflow_controller import coordinate_custom_equation
from frontend.ui_dialogs import (
    ask_num_parameters, ask_parameter_names, ask_custom_formula
)

# User provides formula through UI
eq_id, fit_func = coordinate_custom_equation(
    parent_window=root,
    ask_num_parameters_func=ask_num_parameters,
    ask_parameter_names_func=ask_parameter_names,
    ask_custom_formula_func=ask_custom_formula
)

if fit_func:
    # Use like any other fitting function (backend returns 4-tuple)
    text, y_fitted, equation, *_ = fit_func(data, 'x', 'y')
```

## Best Practices

1. **Parameter Names**: Use descriptive, single-word names
   ```python
   # Good
   ["amplitude", "frequency", "phase"]
   
   # Bad
   ["a b", "param1", "x"]
   ```

2. **Formula Clarity**: Write formulas in standard mathematical notation
   ```python
   # Good
   "a*exp(-b*x) + c"
   
   # Bad
   "a*e**(-b*x)+c"
   ```

3. **Error Handling**: Always catch EquationError and ValidationError
   ```python
   try:
       evaluator = CustomFunctionEvaluator(formula, params)
       result = evaluator.fit(data, 'x', 'y')
   except ValidationError as e:
       print(f"Invalid parameters: {e}")
   except EquationError as e:
       print(f"Formula error: {e}")
   ```

4. **Testing**: Test formulas with simple data first
   ```python
   # Test with known values
   test_data = pd.DataFrame({
       'x': [1, 2, 3],
       'y': [2, 4, 6],  # y = 2*x
       'ux': [0.1] * 3,
       'uy': [0.1] * 3
   })
   ```

## Technical Details

### Function Generation

The evaluator creates a callable function with signature:
```python
def custom_func(x: NDArray, *params: float) -> NDArray:
    # Evaluates formula with x and parameters
    return result
```

This function is compatible with `scipy.optimize.curve_fit`.

### Namespace Safety

The evaluation uses a restricted namespace:
```python
namespace = {
    'np': np,  # Only NumPy
    'x': x,    # Independent variable
    **dict(zip(parameter_names, params))  # Parameters
}
```

No builtins or other modules are accessible.

---

*For more information about custom functions, see [Extending Guide](../extending.md).*
