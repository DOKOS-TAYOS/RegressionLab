# loaders.data_loader

High-level data loading interface for RegressionLab.

## Overview

The `data_loader` module provides functions for loading experimental data from various file formats into pandas DataFrames. It handles file type detection, encoding issues, and data validation.

## Key Functions

### Data Loading

#### `load_data_workflow(filename: str, file_type: str) -> Tuple[pd.DataFrame, str]`

Complete data loading workflow - recommended entry point.

This convenience function combines path preparation and data loading into a single operation. It's the main entry point for loading data files in the application.

**Parameters:**
- `filename`: File name without extension (e.g., 'Ejemplo')
- `file_type`: File type ('csv', 'xlsx', 'txt')

**Returns:**
- Tuple of (data DataFrame, complete file path). The file path is returned so it can be used for reloading in loop mode.

**Raises:**
- `DataLoadError`: If data cannot be loaded

**Example:**
```python
from loaders.data_loader import load_data_workflow

# Load data using workflow
data, file_path = load_data_workflow('Ejemplo', 'xlsx')
print(data.head())
print(f"Loaded from: {file_path}")
```

#### `load_data(file_path: str, file_type: str) -> pd.DataFrame`

Primary function for loading data files.

Loads data from CSV or Excel files based on the specified file type.

**Parameters:**
- `file_path`: Complete path to the file
- `file_type`: File type ('csv', 'xlsx', 'txt')

**Returns:**
- DataFrame with loaded data

**Raises:**
- `InvalidFileTypeError`: If file type is not supported
- `DataLoadError`: If file cannot be loaded

**Example:**
```python
from loaders.data_loader import load_data

# Load CSV file
data = load_data('input/experiment1.csv', 'csv')

# Load Excel file
data = load_data('input/experiment2.xlsx', 'xlsx')

print(data.head())
print(f"Columns: {data.columns.tolist()}")
```

### Variable Extraction

#### `get_variable_names(data: pd.DataFrame, filter_uncertainty: bool = False) -> List[str]`

Extract variable names from DataFrame.

When `filter_uncertainty` is False, returns all column names (e.g., 'x', 'ux', 'y', 'uy'). When True, excludes uncertainty columns (e.g., 'ux', 'uy') so only base variables like 'x', 'y' are returned. Uncertainty columns are assumed to be named 'u<varname>'.

**Parameters:**
- `data`: DataFrame with the data
- `filter_uncertainty`: If True, exclude uncertainty columns from the result

**Returns:**
- List of column names as strings

**Example:**
```python
from loaders.data_loader import get_variable_names

# All columns (default)
all_vars = get_variable_names(data, filter_uncertainty=False)
print(f"All columns: {all_vars}")  # ['x', 'ux', 'y', 'uy']

# Only data columns (no uncertainties)
data_vars = get_variable_names(data, filter_uncertainty=True)
print(f"Data columns: {data_vars}")  # ['x', 'y']
```

### Path Management

#### `prepare_data_path(filename: str, file_type: str, base_dir: str = None) -> str`

Construct the complete path to a data file.

This function builds an absolute path from the project root to the data file, ensuring cross-platform compatibility using pathlib.

**Parameters:**
- `filename`: File name without extension (e.g., 'Ejemplo', 'Exper1')
- `file_type`: File extension ('csv', 'xlsx', 'txt')
- `base_dir`: Base directory where data files are located (relative to project root). If None, uses FILE_INPUT_DIR from environment variables or default 'input'

**Returns:**
- Complete file path (absolute from project root)

**Example:**
```python
from loaders.data_loader import prepare_data_path

# Prepare path for a file
file_path = prepare_data_path('Ejemplo', 'xlsx')
print(f"Full path: {file_path}")  # e.g., 'C:/Users/user/project/input/Ejemplo.xlsx'
```

#### `get_file_list_by_type(file_type: str, csv: list, xlsx: list, txt: list) -> list`

Get list of files based on selected type.

This function acts as a selector/router that returns the appropriate file list based on the user's file type selection.

**Parameters:**
- `file_type`: File type ('csv', 'xlsx', 'txt')
- `csv`: List of CSV file names (without extension)
- `xlsx`: List of XLSX file names (without extension)
- `txt`: List of TXT file names (without extension)

**Returns:**
- List of files of the specified type

**Raises:**
- `InvalidFileTypeError`: If file type is not valid

**Example:**
```python
from loaders.data_loader import get_file_list_by_type

csv_files = ['data1', 'data2']
xlsx_files = ['experiment1', 'experiment2']
txt_files = ['notes']

# Get CSV files
csv_list = get_file_list_by_type('csv', csv_files, xlsx_files, txt_files)
print(csv_list)  # ['data1', 'data2']
```

## Supported File Formats

File type dispatch is done via a module-level reader registry (`_READERS`): each key is a file type (`'csv'`, `'xlsx'`, `'txt'`) and the value is the corresponding reader from `loading_utils`. To add a new format, implement the reader and register it in `_READERS`.

### CSV Files

**Supported delimiters:**
- Comma (`,`)
- Semicolon (`;`)
- Tab (`\t`)

**Encoding:** Auto-detected (UTF-8, Latin-1, etc.)

**Example CSV:**
```csv
time,temperature,utime,utemperature
0,20.0,0.1,0.5
1,25.3,0.1,0.5
2,30.1,0.1,0.5
3,35.4,0.1,0.5
```

### Excel Files

**Supported format:**
- `.xlsx` (Excel 2007+) - use `file_type='xlsx'`

**Requirements:**
- Data in first sheet
- Column headers in first row
- No merged cells in data area

**Example Excel structure:**
```
| x     | y     | ux   | uy   |
|-------|-------|------|------|
| 1.0   | 2.5   | 0.1  | 0.2  |
| 2.0   | 5.1   | 0.1  | 0.2  |
| 3.0   | 7.4   | 0.1  | 0.2  |
```

## Data Format Requirements

### Column Naming

- **Variable columns**: Any valid name (e.g., `time`, `voltage`, `concentration`)
- **Uncertainty columns**: Prefix with `u` (e.g., `utime`, `uvoltage`)

### Data Types

- All data values must be numeric
- NaN values will cause fitting to fail
- Infinite values not allowed

### Minimum Requirements

- At least 2 columns (X and Y)
- At least 5 data points (more recommended)
- No duplicate column names

## Error Handling

### Common Errors

**FileNotFoundError:**
```python
try:
    data = load_data('nonexistent.csv', 'csv')
except FileNotFoundError:
    print("File not found!")
```

**UnicodeDecodeError:**
```python
try:
    data = load_data('bad_encoding.csv', 'csv')
except UnicodeDecodeError:
    print("Encoding issue - try saving as UTF-8")
```

**InvalidFileTypeError:**
```python
from utils.exceptions import InvalidFileTypeError

try:
    data = load_data('corrupt.xlsx', 'xlsx')
except InvalidFileTypeError as e:
    print(f"Invalid file type: {e}")
except Exception as e:
    print(f"Failed to load: {e}")
```

## Advanced Usage

### Custom Delimiter CSV

For CSV files with unusual delimiters, modify the loader:

```python
from loaders.loading_utils import csv_reader

# Custom delimiter
data = csv_reader('data.txt', delimiter='|')
```

### Specific Excel Sheet

To read from a specific sheet, you need to use `excel_reader` directly:

```python
from loaders.loading_utils import excel_reader

# Read from second sheet
data = excel_reader('data.xlsx', sheet_name='Sheet2')
```

Note: The `load_data` function reads from the first sheet by default.

### Handling Missing Data

```python
# Load data
data = load_data('experiment.csv', 'csv')

# Check for missing values
if data.isnull().any().any():
    print("Warning: Missing values detected")
    
    # Drop rows with NaN
    data = data.dropna()
    
    # Or fill with interpolation
    data = data.interpolate(method='linear')
```

## Integration with Fitting

Typical workflow:

```python
from loaders.data_loader import load_data_workflow, get_variable_names
from fitting.fitting_functions import fit_linear_function_with_n

# 1. Load data using workflow
data, file_path = load_data_workflow('experiment', 'csv')

# 2. Get available variables
variables = get_variable_names(data, filter_uncertainty=True)
print(f"Available variables: {variables}")

# 3. Select variables (e.g., from UI or manually)
x_name = 'time'
y_name = 'temperature'

# 4. Convert DataFrame to dict format for fitting
data_dict = {col: data[col].values for col in data.columns}

# 5. Perform fitting
text, y_fitted, equation, *_ = fit_linear_function_with_n(
    data_dict, x_name, y_name
)

print(f"Fitting complete:\n{text}")  # R² is included in the text output
```

## Performance Considerations

### File Size

- **CSV**: Fast for files < 100 MB
- **Excel**: Slower for large files (use CSV if possible)

### Optimization Tips

1. **Use CSV for large datasets**: Faster than Excel
2. **Clean data before loading**: Remove unnecessary columns
3. **Use appropriate dtypes**: Specify numeric types explicitly
4. **Cache loaded data**: Don't reload unnecessarily

### Memory Usage

```python
# Check DataFrame memory usage
data_memory = data.memory_usage(deep=True).sum()
print(f"Data uses {data_memory / 1024**2:.2f} MB")

# Optimize memory if needed
data = data.astype('float32')  # Use 32-bit instead of 64-bit
```

## Troubleshooting

### Data Won't Load

1. **Check file exists**: Verify path is correct
2. **Check permissions**: Ensure read access
3. **Try opening in Excel/text editor**: Verify file isn't corrupt
4. **Check encoding**: Try UTF-8 if special characters present

### Wrong Data Loaded

1. **Check delimiter**: CSV may use semicolon instead of comma
2. **Check headers**: Ensure first row contains column names
3. **Check sheet**: Excel file may have data in different sheet

### Uncertainty Columns Not Detected

1. **Check naming**: Must be exactly `u` + variable name
2. **Check case**: Lowercase `u` required
3. **Check spelling**: No extra characters or spaces

---

*See also: [loading_utils](loading_utils.md) for low-level file readers.*
