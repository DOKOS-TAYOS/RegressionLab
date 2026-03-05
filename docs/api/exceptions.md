# utils.exceptions

Custom exceptions for the RegressionLab application.

## Overview

The `exceptions.py` module defines specific exception types for different error scenarios, providing better error handling and debugging capabilities. All exceptions inherit from a base `RegressionLabError` class.

## Exception Hierarchy

```
RegressionLabError (base)
├── DataLoadError
│   ├── FileNotFoundError
│   └── InvalidFileTypeError
├── DataValidationError
├── FittingError
├── EquationError
└── ValidationError
```

## Base Exception

### `RegressionLabError`

Base exception class for all RegressionLab-related errors.

**Usage:**
```python
from utils.exceptions import RegressionLabError

class MyCustomError(RegressionLabError):
    """Custom error for my module."""
    pass
```

## Data Loading Exceptions

### `DataLoadError`

Exception raised when data loading fails.

**Usage:**
```python
from utils.exceptions import DataLoadError

if file_type not in supported_types:
    raise DataLoadError(f"Unsupported file type: {file_type}")
```

### `FileNotFoundError`

Exception raised when a requested file is not found.

**Note:** This is a custom exception, not Python's built-in `FileNotFoundError`.

**Usage:**
```python
from utils.exceptions import FileNotFoundError

if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")
```

### `InvalidFileTypeError`

Exception raised when file type is not supported.

**Usage:**
```python
from utils.exceptions import InvalidFileTypeError

if file_type not in ['csv', 'xlsx', 'txt']:
    raise InvalidFileTypeError(f"File type {file_type} not supported")
```

## Data Validation Exceptions

### `DataValidationError`

Exception raised when data validation fails.

**Usage:**
```python
from utils.exceptions import DataValidationError

if data.empty:
    raise DataValidationError("DataFrame is empty")
```

## Fitting Exceptions

### `FittingError`

Exception raised when curve fitting fails.

**Usage:**
```python
from utils.exceptions import FittingError

try:
    popt, pcov = curve_fit(func, x, y)
except RuntimeError as e:
    raise FittingError(f"Fitting failed: {e}")
```

## Equation Exceptions

### `EquationError`

Exception raised when equation evaluation fails.

**Usage:**
```python
from utils.exceptions import EquationError

try:
    result = eval(formula, namespace)
except SyntaxError as e:
    raise EquationError(f"Invalid formula syntax: {e}")
```

## Validation Exceptions

### `ValidationError`

Exception raised when input validation fails.

**Usage:**
```python
from utils.exceptions import ValidationError

if not param_name.isidentifier():
    raise ValidationError(f"Invalid parameter name: {param_name}")
```

## Usage Examples

### Catching Specific Exceptions

```python
from utils.exceptions import (
    DataLoadError, FittingError, ValidationError
)

try:
    data = load_data('file.csv')
    result = fit_data(data)
except DataLoadError as e:
    print(f"Data loading failed: {e}")
except FittingError as e:
    print(f"Fitting failed: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Raising Exceptions with Context

```python
from utils.exceptions import FittingError
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    result = perform_fit(data)
except RuntimeError as e:
    logger.error(f"Fitting failed: {e}", exc_info=True)
    raise FittingError(f"Could not fit data: {str(e)}") from e
```

### Exception Chaining

```python
from utils.exceptions import DataLoadError, FileNotFoundError

try:
    data = load_file(path)
except FileNotFoundError as e:
    # Chain exceptions for better error context
    raise DataLoadError(f"Failed to load data from {path}") from e
```

## Best Practices

1. **Use Specific Exceptions**: Use the most specific exception type
   ```python
   # Good
   raise FileNotFoundError(f"File not found: {path}")
   
   # Less specific
   raise DataLoadError(f"File not found: {path}")
   ```

2. **Provide Context**: Include relevant information in error messages
   ```python
   # Good
   raise ValidationError(f"Parameter '{name}' is not a valid identifier")
   
   # Less informative
   raise ValidationError("Invalid parameter")
   ```

3. **Log Before Raising**: Log errors before raising exceptions
   ```python
   logger.error(f"Failed to load {file_path}", exc_info=True)
   raise DataLoadError(f"Could not load {file_path}")
   ```

4. **Exception Chaining**: Use `from` to chain exceptions
   ```python
   try:
       result = risky_operation()
   except ValueError as e:
       raise CustomError("Operation failed") from e
   ```

5. **Handle Gracefully**: Provide user-friendly error messages
   ```python
   try:
       data = load_data(file_path)
   except FileNotFoundError:
       messagebox.showerror("Error", f"File not found: {file_path}")
   ```

## Integration with Logging

Exceptions work seamlessly with the logging module:

```python
from utils.exceptions import FittingError
from utils.logger import get_logger

logger = get_logger(__name__)

def fit_data(data):
    try:
        # Perform fitting
        result = perform_fit(data)
        return result
    except Exception as e:
        logger.error(f"Fitting failed: {e}", exc_info=True)
        raise FittingError(f"Could not fit data: {str(e)}")
```

## Internationalization

Error messages can be internationalized using the `i18n` module:

```python
from utils.exceptions import FittingError
from i18n import t

raise FittingError(t('error.fitting_failed'))
```

## Testing Exceptions

```python
import pytest
from utils.exceptions import ValidationError, FittingError

def test_validation_error():
    with pytest.raises(ValidationError):
        validate_parameter_names(['invalid name'])

def test_fitting_error():
    with pytest.raises(FittingError):
        fit_invalid_data()
```

---

*For more information about error handling, see [Troubleshooting Guide](../troubleshooting.md).*
