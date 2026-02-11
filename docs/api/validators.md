# utils.validators

Data validation utilities for the RegressionLab application.

## Overview

The `validators.py` module provides functions to validate data integrity, file paths, and parameter values before processing. It ensures data quality and prevents errors during fitting operations.

## Key Functions

### File Validation

#### `validate_file_path(file_path: str) -> None`

Validate that a file path exists and is accessible.

**Parameters:**
- `file_path`: Path to the file

**Raises:**
- `FileNotFoundError`: If file does not exist
- `ValidationError`: If path is not a file

**Example:**
```python
from utils.validators import validate_file_path

try:
    validate_file_path('input/data.csv')
    # File exists and is accessible
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

#### `validate_file_type(file_type: str, allowed_types: List[str] = None) -> None`

Validate that a file type is supported.

**Parameters:**
- `file_type`: File extension (e.g., 'csv', 'xlsx')
- `allowed_types`: List of allowed file types (default: ['csv', 'xlsx', 'txt'])

**Raises:**
- `InvalidFileTypeError`: If file type is not supported

**Example:**
```python
from utils.validators import validate_file_type

# Default allowed types
validate_file_type('csv')  # OK
validate_file_type('txt')  # Raises InvalidFileTypeError

# Custom allowed types
validate_file_type('json', allowed_types=['json', 'yaml'])
```

### DataFrame Validation

#### `validate_dataframe(data: pd.DataFrame, min_rows: int = 2) -> None`

Validate that a DataFrame is suitable for fitting.

**Parameters:**
- `data`: DataFrame to validate
- `min_rows`: Minimum number of rows required

**Raises:**
- `DataValidationError`: If DataFrame is invalid

**Example:**
```python
from utils.validators import validate_dataframe
import pandas as pd

data = pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 6]})

# Default minimum (2 rows)
validate_dataframe(data)  # OK

# Custom minimum
validate_dataframe(data, min_rows=5)  # Raises DataValidationError
```

#### `validate_column_exists(data: pd.DataFrame, column_name: str) -> None`

Validate that a column exists in a DataFrame.

**Parameters:**
- `data`: DataFrame to check
- `column_name`: Name of the column

**Raises:**
- `DataValidationError`: If column does not exist

**Example:**
```python
from utils.validators import validate_column_exists

data = pd.DataFrame({'x': [1, 2], 'y': [2, 4]})

validate_column_exists(data, 'x')  # OK
validate_column_exists(data, 'z')  # Raises DataValidationError
```

### Numeric Data Validation

#### `validate_numeric_data(data: pd.Series, column_name: str) -> None`

Validate that data in a column is numeric and has no NaN values.

**Parameters:**
- `data`: Series to validate
- `column_name`: Name of the column (for error messages)

**Raises:**
- `DataValidationError`: If data is not numeric or contains NaN

**Example:**
```python
from utils.validators import validate_numeric_data
import pandas as pd

data = pd.Series([1.0, 2.0, 3.0])
validate_numeric_data(data, 'x')  # OK

data_with_nan = pd.Series([1.0, None, 3.0])
validate_numeric_data(data_with_nan, 'x')  # Raises DataValidationError
```

**Checks:**
- Data type is numeric
- No NaN values
- No infinite values

### Uncertainty Validation

#### `validate_uncertainty_column(data: pd.DataFrame, var_name: str) -> None`

Validate that uncertainty column exists and is valid for a variable.

**Parameters:**
- `data`: DataFrame containing the data
- `var_name`: Name of the variable (uncertainty column should be 'u{var_name}')

**Raises:**
- `DataValidationError`: If uncertainty column is missing or invalid

**Example:**
```python
from utils.validators import validate_uncertainty_column

data = pd.DataFrame({
    'x': [1, 2, 3],
    'ux': [0.1, 0.1, 0.1],
    'y': [2, 4, 6],
    'uy': [0.2, 0.2, 0.2]
})

validate_uncertainty_column(data, 'x')  # Checks 'ux'
validate_uncertainty_column(data, 'y')  # Checks 'uy'
```

**Checks:**
- Column exists
- Data is numeric
- Values are non-negative

### Comprehensive Fitting Data Validation

#### `validate_fitting_data(data: pd.DataFrame, x_name: str, y_name: str) -> None`

Comprehensive validation for fitting data.

Validates:
- DataFrame is not empty
- Required columns exist
- Data is numeric
- Uncertainty columns exist and are valid

**Parameters:**
- `data`: DataFrame with data to fit
- `x_name`: Name of the independent variable column
- `y_name`: Name of the dependent variable column

**Raises:**
- `DataValidationError`: If any validation fails

**Example:**
```python
from utils.validators import validate_fitting_data

data = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'ux': [0.1] * 4,
    'y': [2, 4, 6, 8],
    'uy': [0.2] * 4
})

validate_fitting_data(data, 'x', 'y')
# Validates everything needed for fitting
```

### Parameter Validation

#### `validate_parameter_names(param_names: List[str]) -> None`

Validate parameter names for custom equations.

**Parameters:**
- `param_names`: List of parameter names

**Raises:**
- `ValidationError`: If parameter names are invalid

**Example:**
```python
from utils.validators import validate_parameter_names

# Valid names
validate_parameter_names(['a', 'b', 'c'])  # OK
validate_parameter_names(['alpha', 'beta'])  # OK

# Invalid names
validate_parameter_names([])  # Raises ValidationError (empty)
validate_parameter_names(['a', 'a'])  # Raises ValidationError (duplicate)
validate_parameter_names(['a b'])  # Raises ValidationError (invalid identifier)
```

**Checks:**
- List is not empty
- No duplicate names
- All names are valid Python identifiers

#### `validate_positive_integer(value: Any, name: str) -> int`

Validate that a value is a positive integer.

**Parameters:**
- `value`: Value to validate
- `name`: Name of the parameter (for error messages)

**Returns:**
- The validated integer value

**Raises:**
- `ValidationError`: If value is not a positive integer

**Example:**
```python
from utils.validators import validate_positive_integer

# Valid
num = validate_positive_integer(5, 'num_params')  # Returns 5
num = validate_positive_integer('10', 'num_params')  # Returns 10

# Invalid
validate_positive_integer(0, 'num_params')  # Raises ValidationError
validate_positive_integer(-1, 'num_params')  # Raises ValidationError
validate_positive_integer('abc', 'num_params')  # Raises ValidationError
```

## Usage Examples

### Complete Data Validation

```python
from utils.validators import (
    validate_file_path, validate_file_type,
    validate_fitting_data
)
import pandas as pd

# 1. Validate file
file_path = 'input/data.csv'
validate_file_path(file_path)
validate_file_type('csv')

# 2. Load data
data = pd.read_csv(file_path)

# 3. Validate data
validate_fitting_data(data, 'x', 'y')

# Data is ready for fitting
```

### Custom Validation Workflow

```python
from utils.validators import (
    validate_dataframe, validate_column_exists,
    validate_numeric_data, validate_uncertainty_column
)

def custom_validation(data, x_name, y_name):
    # Step by step validation
    validate_dataframe(data, min_rows=3)
    validate_column_exists(data, x_name)
    validate_column_exists(data, y_name)
    validate_numeric_data(data[x_name], x_name)
    validate_numeric_data(data[y_name], y_name)
    validate_uncertainty_column(data, x_name)
    validate_uncertainty_column(data, y_name)
    
    print("All validations passed")
```

### Error Handling

```python
from utils.validators import validate_fitting_data
from utils.exceptions import DataValidationError

try:
    validate_fitting_data(data, 'x', 'y')
except DataValidationError as e:
    print(f"Data validation failed: {e}")
    # Handle error appropriately
```

## Best Practices

1. **Validate Early**: Validate data as soon as it's loaded
   ```python
   data = load_data('file.csv')
   validate_fitting_data(data, 'x', 'y')  # Before any processing
   ```

2. **Specific Validation**: Use specific validators for targeted checks
   ```python
   # Check specific column
   validate_numeric_data(data['x'], 'x')
   
   # Check uncertainty
   validate_uncertainty_column(data, 'x')
   ```

3. **Error Messages**: Validators provide informative error messages
   ```python
   try:
       validate_fitting_data(data, 'x', 'y')
   except DataValidationError as e:
       # Error message includes details about what failed
       print(e)
   ```

4. **Combined Validation**: Use comprehensive validator when possible
   ```python
   # Instead of multiple individual checks
   validate_fitting_data(data, 'x', 'y')
   
   # Instead of:
   # validate_dataframe(data)
   # validate_column_exists(data, 'x')
   # validate_column_exists(data, 'y')
   # ...
   ```

## Integration with Data Loading

Validators are integrated into the data loading workflow:

```python
from loaders.loading_utils import csv_reader
from utils.validators import validate_fitting_data

def load_and_validate(file_path, x_name, y_name):
    # Load data (includes basic validation)
    data = csv_reader(file_path)
    
    # Comprehensive validation
    validate_fitting_data(data, x_name, y_name)
    
    return data
```

## Technical Details

### Validation Order

The `validate_fitting_data` function performs validations in this order:
1. DataFrame structure (not None, not empty, minimum rows)
2. Column existence
3. Numeric data type
4. Uncertainty columns

### Performance

- **Early Exit**: Validation stops at first failure
- **Efficient Checks**: Uses pandas/numpy operations; duplicate and infinite-value checks reuse a single computed mask to avoid repeated array operations
- **Minimal Overhead**: Fast validation for typical datasets

### Error Messages

All validators provide detailed error messages including:
- What was validated
- What value was found
- What was expected
- Available alternatives (when applicable)

---

*For more information about validation, see [Troubleshooting Guide](../troubleshooting.md).*
