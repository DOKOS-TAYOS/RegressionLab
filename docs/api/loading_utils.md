# loaders.loading_utils

Loading utilities for data file operations.

## Overview

The `loading_utils.py` module provides functions to load data from CSV, TXT and Excel files.

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

## Integration with Data Loader

The loading utilities are typically used through the higher-level `data_loader` module:

```python
from loaders.data_loader import load_data

# Load data using file path from native file picker or other source
data = load_data('input/experiment.csv', 'csv')
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

---

*For more information about data loading, see [Data Loader](data_loader.md).*
