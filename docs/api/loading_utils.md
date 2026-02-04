# loaders.loading_utils

Loading utilities for data file operations.

## Overview

The `loading_utils.py` module provides functions to load data from CSV and Excel files, and scan directories for available data files. All file operations are relative to the project root directory.

## Key Functions

### File Readers

#### `csv_reader(file_path: str) -> pd.DataFrame`

Load data from a CSV file.

**Parameters:**
- `file_path`: Path to the CSV file

**Returns:**
- DataFrame with the CSV data, treating 'no' as NaN values

**Raises:**
- `FileNotFoundError`: If file does not exist
- `DataLoadError`: If file cannot be read

**Example:**
```python
from loaders.loading_utils import csv_reader

# Load CSV file
data = csv_reader('input/data.csv')
print(f"Loaded {len(data)} rows, {len(data.columns)} columns")
```

**Notes:**
- The function treats the string 'no' as a NaN value
- Uses UTF-8 encoding
- Automatically infers data types

#### `excel_reader(file_path: str) -> pd.DataFrame`

Load data from an Excel file (.xlsx).

**Parameters:**
- `file_path`: Path to the Excel file

**Returns:**
- DataFrame with the Excel data

**Raises:**
- `FileNotFoundError`: If file does not exist
- `DataLoadError`: If file cannot be read

**Example:**
```python
from loaders.loading_utils import excel_reader

# Load Excel file
data = excel_reader('input/data.xlsx')
print(f"Loaded {len(data)} rows, {len(data.columns)} columns")
```

**Notes:**
- Supports `.xlsx` format
- Reads the first sheet by default
- Handles missing values automatically

### File Discovery

#### `get_file_names(directory: str = None) -> Tuple[List[str], List[str], List[str]]`

Get categorized file names from a directory.

Scans the specified directory and categorizes files by extension, returning file names without their extensions. This allows the UI to present clean file names to the user while the full path can be reconstructed when needed.

**Parameters:**
- `directory`: Name of the directory to scan (default: None, relative to project root)

**Returns:**
- Tuple of three lists: `(csv_files, xlsx_files, txt_files)`
- Each list contains file names without extensions

**Raises:**
- `FileNotFoundError`: If directory does not exist

**Example:**
```python
from loaders.loading_utils import get_file_names

# Get files from default input directory
csv, xlsx, txt = get_file_names()

print(f"CSV files: {csv}")    # ['data1', 'data2']
print(f"XLSX files: {xlsx}")  # ['experiment1']
print(f"TXT files: {txt}")    # ['notes']

# Get files from specific directory
csv, xlsx, txt = get_file_names('custom_input')
```

**Notes:**
- Returns file names **without** extensions
- Only scans the specified directory (not subdirectories)
- Handles permission errors gracefully

## File Path Resolution

All file paths are resolved relative to the project root directory. The project root is determined automatically (see `config.paths.get_project_root`).

### Example Path Resolution

```python
# If project root is: /path/to/RegressionLab
# And input_dir is: "input"

# File: input/data.csv
# Resolves to: /path/to/RegressionLab/input/data.csv
```

## Error Handling

### File Not Found

```python
from loaders.loading_utils import csv_reader
from utils.exceptions import FileNotFoundError

try:
    data = csv_reader('nonexistent.csv')
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

### Invalid File Type

```python
from loaders.loading_utils import excel_reader
from utils.exceptions import DataLoadError

try:
    data = excel_reader('corrupted.xlsx')
except DataLoadError as e:
    print(f"Failed to load: {e}")
```

### Empty Files

```python
from loaders.loading_utils import csv_reader
from utils.exceptions import DataLoadError

try:
    data = csv_reader('empty.csv')
except DataLoadError as e:
    print(f"File is empty: {e}")
```

## Data Format Requirements

### CSV Format

- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Header**: First row should contain column names
- **Missing values**: Use 'no' or leave empty

**Example CSV:**
```csv
x,y,ux,uy
1.0,2.0,0.1,0.2
2.0,4.0,0.1,0.2
3.0,6.0,0.1,0.2
```

### Excel Format

- **Sheets**: Reads first sheet by default
- **Header**: First row should contain column names
- **Missing values**: Empty cells or 'no'

**Example Excel:**
| x | y | ux | uy |
|---|---|----|----|
| 1.0 | 2.0 | 0.1 | 0.2 |
| 2.0 | 4.0 | 0.1 | 0.2 |
| 3.0 | 6.0 | 0.1 | 0.2 |

## Usage Examples

### Basic File Loading

```python
from loaders.loading_utils import csv_reader, excel_reader

# Load CSV
csv_data = csv_reader('input/experiment.csv')

# Load Excel
excel_data = excel_reader('input/experiment.xlsx')
```

### Discovering Available Files

```python
from loaders.loading_utils import get_file_names

# Get all available files
csv_files, xlsx_files, txt_files = get_file_names()

# Present to user
print("Available CSV files:")
for filename in csv_files:
    print(f"  - {filename}")

print("Available Excel files:")
for filename in xlsx_files:
    print(f"  - {filename}")
```

### Complete Workflow

```python
from loaders.loading_utils import get_file_names, csv_reader
from loaders.data_loader import get_file_list_by_type

# 1. Get available files
csv, xlsx, txt = get_file_names()

# 2. Get file list for specific type
file_list = get_file_list_by_type('csv', csv, xlsx, txt)

# 3. User selects file (e.g., 'data1')
selected_file = 'data1'

# 4. Load the file
file_path = f'input/{selected_file}.csv'
data = csv_reader(file_path)

print(f"Loaded {len(data)} rows")
```

## Integration with Data Loader

The loading utilities are typically used through the higher-level `data_loader` module:

```python
from loaders.data_loader import load_data_workflow

# High-level function handles file discovery and loading
data, file_path = load_data_workflow('data1', 'csv')
```

## Best Practices

1. **Error Handling**: Always wrap file operations in try-except blocks
   ```python
   try:
       data = csv_reader('data.csv')
   except FileNotFoundError:
       print("File not found")
   except DataLoadError as e:
       print(f"Loading error: {e}")
   ```

2. **Path Validation**: Use absolute paths when possible
   ```python
   from pathlib import Path
   file_path = Path('input') / 'data.csv'
   data = csv_reader(str(file_path))
   ```

3. **File Discovery**: Check if files exist before presenting to user
   ```python
   csv, xlsx, txt = get_file_names()
   if not csv and not xlsx and not txt:
       print("No data files found")
   ```

4. **Data Validation**: Validate loaded data before use
   ```python
   from utils.validators import validate_dataframe
   
   data = csv_reader('data.csv')
   validate_dataframe(data, min_rows=2)
   ```

## Technical Details

### File Reading Implementation

- **CSV**: Uses `pandas.read_csv()` with UTF-8 encoding
- **Excel**: Uses `pandas.read_excel()` with automatic format detection
- **Error Handling**: Catches pandas exceptions and converts to custom exceptions

### Directory Scanning

- **Performance**: Single directory scan, no recursion
- **Filtering**: Only includes files with recognized extensions
- **Case Sensitivity**: Extension matching is case-insensitive on Windows

### Path Handling

- **Cross-platform**: Uses `pathlib.Path` for cross-platform compatibility
- **Relative paths**: All paths relative to project root
- **Validation**: Checks existence and file type before operations

---

*For more information about data loading, see [Data Loader](data_loader.md)*
