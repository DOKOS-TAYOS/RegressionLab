# streamlit_app.app

Streamlit Application for RegressionLab - Web-based interface for curve fitting operations.

## Overview

The `streamlit_app.app` module is the entry point for the web interface; the main UI logic is organized in the `streamlit_app.sections` package. `app.py` sets up the page, sidebar, and mode routing; each operation mode and shared components (data loading, fitting, results, help) live in `streamlit_app/sections/`:

- **`sections/sidebar.py`** – Sidebar setup, logo, language toggle, session state
- **`sections/data.py`** – `load_uploaded_file`, `show_data_with_pair_plots`, `get_variable_names`, `get_temp_output_dir`
- **`sections/fitting.py`** – `perform_fit`, `show_equation_selector`, `select_variables`, `create_equation_options`
- **`sections/results.py`** – `show_results`
- **`sections/help_section.py`** – `show_help_section`
- **`sections/modes.py`** – `mode_normal_fitting`, `mode_multiple_datasets`, `mode_checker_fitting`, `mode_total_fitting`

Imports such as `from streamlit_app.app import main, mode_normal_fitting` or `from streamlit_app.sections import perform_fit, load_uploaded_file` work as before. The application offers the same functionality as the Tkinter desktop version but in a web browser.

## Main Application

#### `main() -> None`

Main Streamlit application entry point.

This function sets up the Streamlit page configuration, initializes session state, displays the UI, and routes to the appropriate operation mode handler.

**Example:**
```python
# Run with: streamlit run src/streamlit_app/app.py
if __name__ == "__main__":
    main()
```

## Operation Modes

The application supports four operation modes, matching the desktop version:

### Normal Fitting

Single file, single equation fitting.

**Function:** `mode_normal_fitting(equation_types: List[str]) -> None`

**Features:**
- File upload (CSV, XLSX, TXT)
- Variable selection
- Equation selection (including custom)
- Single fit execution
- Result display with plot

**Example Usage:**
```python
from streamlit_app.app import mode_normal_fitting
from config import AVAILABLE_EQUATION_TYPES

mode_normal_fitting(AVAILABLE_EQUATION_TYPES)
```

### Multiple Datasets

Multiple files, single equation fitting.

**Function:** `mode_multiple_datasets(equation_types: List[str]) -> None`

**Features:**
- Multiple file upload
- Per-file variable selection
- Single equation for all files
- Batch fitting
- Results for each dataset

**Example Usage:**
```python
from streamlit_app.app import mode_multiple_datasets

mode_multiple_datasets(AVAILABLE_EQUATION_TYPES)
```

### Checker Fitting

Single file, multiple equations fitting.

**Function:** `mode_checker_fitting(equation_types: List[str]) -> None`

**Features:**
- Single file upload
- Variable selection
- Multiple equation selection
- Compare fits
- Results comparison

**Example Usage:**
```python
from streamlit_app.app import mode_checker_fitting

mode_checker_fitting(AVAILABLE_EQUATION_TYPES)
```

### Total Fitting

Single file, all equations fitting.

**Function:** `mode_total_fitting(equation_types: List[str]) -> None`

**Features:**
- Single file upload
- Variable selection
- Automatic fitting with all equations
- Comprehensive comparison
- All results displayed

**Example Usage:**
```python
from streamlit_app.app import mode_total_fitting

mode_total_fitting(AVAILABLE_EQUATION_TYPES)
```

## Key Functions

### Data Loading

#### `load_uploaded_file(uploaded_file) -> pd.DataFrame`

Load data from uploaded file.

**Parameters:**
- `uploaded_file`: Streamlit UploadedFile object

**Returns:**
- DataFrame with loaded data or `None` if loading fails

**Example:**
```python
uploaded_file = st.file_uploader("Upload file", type=['csv', 'xlsx'])
if uploaded_file:
    data = load_uploaded_file(uploaded_file)
    if data is not None:
        st.dataframe(data)
```

### Fitting

#### `perform_fit(data, x_name, y_name, equation_name, plot_name, custom_formula=None, parameter_names=None) -> Optional[Dict[str, Any]]`

Perform curve fitting and return results.

**Parameters:**
- `data`: DataFrame with data
- `x_name`: X variable name
- `y_name`: Y variable name
- `equation_name`: Type of equation to fit
- `plot_name`: Name for the plot
- `custom_formula`: Optional custom formula
- `parameter_names`: Optional parameter names for custom formula

**Returns:**
- Dictionary with fitting results or `None` if fitting fails

**Result Dictionary:**
```python
{
    'equation_name': str,      # Display name
    'parameters': str,         # Formatted parameters
    'equation': str,           # Formatted equation
    'r_squared': float,        # R² value
    'plot_path': str,          # Path to plot image
    'plot_name': str           # Plot name
}
```

**Example:**
```python
result = perform_fit(
    data=data,
    x_name='x',
    y_name='y',
    equation_name='linear_function',
    plot_name='my_fit'
)

if result:
    st.write(f"R² = {result['r_squared']:.4f}")
    st.image(result['plot_path'])
```

## UI Components

Sidebar and shared UI are implemented in `streamlit_app.sections.sidebar` and other section modules.

#### `setup_sidebar(version: str)` / sidebar helpers

Setup the application sidebar.

The sidebar contains:
- **Brand header**: Application name and version
- **Language selector**: Toggle between Spanish and English
- **Operation mode selector**: Radio buttons for mode selection

**Parameters:**
- `version`: Application version string

**Returns:**
- Selected operation mode

#### `show_help_section() -> None`

Display expandable help section.

Shows information about:
- Application objective
- Advantages
- Fitting modes explanation
- Data format requirements

#### `_select_variables(data, key_prefix='') -> Tuple[str, str, str]`

Show variable selection widgets and return selected values.

**Parameters:**
- `data`: DataFrame with data
- `key_prefix`: Optional prefix for Streamlit widget keys

**Returns:**
- Tuple of `(x_name, y_name, plot_name)`

#### `show_equation_selector(equation_types: List[str]) -> Tuple[str, Optional[str], Optional[List[str]]]`

Show equation type selector and return selection.

**Parameters:**
- `equation_types`: List of available equation type names

**Returns:**
- Tuple of `(equation_name, custom_formula, parameter_names)`

**Features:**
- Dropdown for predefined equations
- Custom formula input with parameter configuration
- Formula examples

#### `show_results(results: List[Dict[str, Any]]) -> None`

Display fitting results.

**Parameters:**
- `results`: List of result dictionaries from `perform_fit()`

Displays:
- Equation display
- Parameter values
- R² value
- Plot image
- Download button for plot

## Session State Management

#### `initialize_session_state() -> None`

Initialize Streamlit session state variables.

**Variables:**
- `language`: Current language ('es' or 'en')
- `results`: List of fitting results
- `plot_counter`: Counter for plot filenames

#### `toggle_language() -> None`

Toggle between Spanish and English.

Updates the session state language and re-initializes the i18n system.

## Configuration

### Page Configuration

```python
st.set_page_config(
    page_title="RegressionLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

### CSS Styling

The sidebar uses custom CSS defined in `SIDEBAR_CSS` in `sections/sidebar.py` for:
- Brand header styling
- Button hover effects
- Section titles
- Responsive design

## Usage Examples

### Running the Application

```bash
# From project root
streamlit run src/streamlit_app/app.py

# Or using the provided script
bin/run_streamlit.sh  # Linux/Mac
bin/run_streamlit.bat  # Windows
```

### Custom Integration

```python
import streamlit as st
from streamlit_app.app import perform_fit, load_uploaded_file

st.title("Custom Fitting Interface")

uploaded_file = st.file_uploader("Upload data", type=['csv'])
if uploaded_file:
    data = load_uploaded_file(uploaded_file)
    if data is not None:
        x_name = st.selectbox("X variable", data.columns)
        y_name = st.selectbox("Y variable", data.columns)
        
        if st.button("Fit Linear"):
            result = perform_fit(
                data, x_name, y_name,
                'linear_function', 'fit'
            )
            if result:
                st.image(result['plot_path'])
```

## File Handling

### Temporary Files

The application uses temporary directories for plot storage in Streamlit Cloud:

**Function:** `get_temp_output_dir() -> Path`

Creates a session-specific temporary directory that persists during the session.

### File Upload

- Supports CSV, XLSX, TXT formats
- Files are temporarily saved for processing
- Automatic cleanup after processing

## Internationalization

- Language toggle in sidebar
- All UI text translated
- Language persists in session state
- Automatic re-initialization on toggle

## Error Handling

### Import Errors

```python
try:
    from config import __version__, AVAILABLE_EQUATION_TYPES
except ImportError as e:
    st.error(f"Error importing configuration: {e}")
```

### Fitting Errors

```python
try:
    result = perform_fit(...)
except FittingError as e:
    st.error(f"Fitting failed: {e}")
```

### General Errors

All errors are logged and displayed to the user with helpful messages.

## Best Practices

1. **Session State**: Use session state for persistent data
   ```python
   if 'data' not in st.session_state:
       st.session_state.data = None
   ```

2. **File Upload**: Always validate uploaded files
   ```python
   if uploaded_file is not None:
       if uploaded_file.size > MAX_SIZE:
           st.error("File too large")
   ```

3. **Progress Indicators**: Show progress for long operations
   ```python
   with st.spinner("Fitting..."):
       result = perform_fit(...)
   ```

4. **Error Messages**: Provide clear error messages
   ```python
   if result is None:
       st.error("Fitting failed. Please check your data.")
   ```

## Technical Details

### Dependencies

- **Streamlit**: Web framework
- **Pandas**: Data handling
- **NumPy**: Numerical operations
- **Matplotlib**: Plot generation
- **All RegressionLab modules**: For fitting functionality

### Performance

- **Lazy Loading**: Heavy imports loaded only when needed
- **Caching**: Logo and static content cached
- **Temporary Files**: Efficient cleanup after use

### Deployment

The application is designed for deployment on:
- **Streamlit Cloud**: Automatic deployment
- **Local Server**: For development
- **Docker**: Containerized deployment

### Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design
- Mobile-friendly interface

---

*For more information about the Streamlit interface, see [Streamlit Guide](../streamlit-guide.md)*
