# streamlit_app

Streamlit Application for RegressionLab – web-based interface for curve fitting operations.

## Overview

The `streamlit_app.app` module is the entry point for the web interface. The main UI logic lives in `streamlit_app.sections`; appearance is driven by `streamlit_app.theme`, which uses the same config as the Tkinter app (`config.env`, `config.theme.UI_STYLE` when available).

**Package layout:**

- **`app.py`** – Entry point: page config, theme injection, session state, sidebar, mode routing.
- **`theme.py`** – Theme from config: `get_streamlit_theme()`, `get_main_css()`. Uses `config.theme.UI_STYLE` (env + theme) when importable; fallback to `config.env` only. Sidebar background is slightly lighter than main area. Colors and fonts come from `UI_BACKGROUND`, `UI_FOREGROUND`, `UI_BUTTON_*`, `UI_FONT_*`, etc.
- **`sections/sidebar.py`** – Sidebar setup, logo (or fallback header with theme colors), language toggle, session state. Initial language from `config.env` (`LANGUAGE`).
- **`sections/data.py`** – `load_uploaded_file`, `show_data_with_pair_plots`, `get_variable_names`, `get_temp_output_dir`
- **`sections/fitting.py`** – `perform_fit`, `show_equation_selector`, `select_variables`, `create_equation_options`. Uses `config.FILE_CONFIG` for plot format/paths.
- **`sections/results.py`** – `show_results`
- **`sections/help_section.py`** – `show_help_section`. Uses `config.DONATIONS_URL` for the donations link.
- **`sections/modes.py`** – `mode_normal_fitting`, `mode_multiple_datasets`, `mode_checker_fitting`, `mode_total_fitting`, `mode_view_data`. Uses `config.DATA_FILE_TYPES`.

**Imports:** `from streamlit_app.app import main`; `from streamlit_app.sections import mode_normal_fitting, perform_fit, load_uploaded_file`, etc. (modes and helpers are in `sections`). The application offers the same functionality as the Tkinter desktop version, with the same configuration sources (env, paths, theme).

## Main Application

#### `main() -> None`

Main Streamlit application entry point.

This function sets up the Streamlit page configuration, injects theme CSS from config (`get_streamlit_theme()`, `get_main_css()`), caches the theme in `st.session_state.streamlit_theme` for reuse by sections (e.g. logo), initializes session state, displays the UI, and routes to the appropriate operation mode handler.

**Example:**
```python
# Run with: streamlit run src/streamlit_app/app.py
if __name__ == "__main__":
    main()
```

## Operation Modes

The application supports five operation modes, aligned with the desktop version:

### Normal Fitting

Single file, single equation fitting.

**Function:** `mode_normal_fitting(equation_types: List[str]) -> None`

**Features:**
- Optional loop fitting: checkbox to fit another file with the same equation without changing mode
- File upload (CSV, XLSX, TXT)
- Variable selection
- Equation selection (including custom)
- Single fit execution
- Result display (equation, parameters, statistics in three columns; plot; download below)

**Example Usage:**
```python
from streamlit_app.sections import mode_normal_fitting
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
from streamlit_app.sections import mode_multiple_datasets

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
from streamlit_app.sections import mode_checker_fitting

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
from streamlit_app.sections import mode_total_fitting

mode_total_fitting(AVAILABLE_EQUATION_TYPES)
```

### View Data

View data from a file without fitting.

**Function:** `mode_view_data(equation_types: List[str]) -> None`

**Features:**
- File upload (CSV, XLSX, TXT)
- Data table and optional pair plots
- No equation selection or fitting

**Example Usage:**
```python
from streamlit_app.sections import mode_view_data

mode_view_data(AVAILABLE_EQUATION_TYPES)
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

Perform curve fitting and return results. Uses the backend fit function (from `fitting.get_fitting_function` or custom evaluator); the backend may return `(text, y_fitted, equation, fit_info)` — only the first three values are used.

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
    'equation_name': str,       # Display name
    'parameters': str,          # Formatted parameters and statistics (plain text)
    'equation': str,             # Formula and formatted equation
    'plot_path': str,           # Path to saved plot (PNG/JPG/PDF)
    'plot_name': str,           # Plot name
    'plot_path_display': str    # Optional: path to PNG preview when plot_path is PDF
}
```

**Example:**
```python
from streamlit_app.sections import perform_fit

result = perform_fit(
    data=data,
    x_name='x',
    y_name='y',
    equation_name='linear_function',
    plot_name='my_fit'
)

if result:
    st.image(result['plot_path'], width='stretch')
    with open(result['plot_path'], 'rb') as f:
        st.download_button("Download", data=f.read(), file_name=result['plot_name'] + '.png')
```

## UI Components

Sidebar and shared UI are implemented in `streamlit_app.sections.sidebar` and other section modules.

#### `setup_sidebar(version: str)` / sidebar helpers

Setup the application sidebar.

The sidebar contains:
- **Brand header**: Application name and version
- **Language selector**: Toggle between Spanish and English
- **Operation mode selector**: Radio for Normal Fitting, Multiple Datasets, Checker Fitting, Total Fitting, View Data

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

#### `select_variables(data, key_prefix='') -> Tuple[str, str, str]`

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

**Layout:** Three columns (equation left, parameters center, statistics right), then the plot image, then the download button below the plot.
- **Column 1 – Equation**: Formula and formatted equation with fitted values
- **Column 2 – Parameters**: Fit parameters with uncertainties and IC 95%
- **Column 3 – Statistics**: R², RMSE, χ², χ²_red, degrees of freedom
- **Plot**: Full-width below the columns
- **Download**: Button below the plot (saves PNG/JPG/PDF; when output format is PDF, in-app preview uses PNG)

## Session State Management

#### `initialize_session_state() -> None`

Initialize Streamlit session state variables.

**Variables:**
- `language`: Current language (initialized from `config.env` `LANGUAGE`; 'es', 'en', etc.)
- `results`: List of fitting results
- `plot_counter`: Counter for plot filenames

#### `cycle_language() -> None`

Cycle to the next supported language (es → en → de → es).

Updates the session state language and re-initializes the i18n system.

## Configuration

Configuration is shared with the Tkinter app: `config.env` (`.env`), `config.paths`, and when available `config.theme`. The Streamlit UI does not provide an in-app configuration dialog; edit `.env` (or use the Tkinter Configure menu) to change language, UI colors, fonts, plot style, paths, etc.

### Page Configuration

```python
st.set_page_config(
    page_title="RegressionLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

### Theme and CSS

- **Source:** `streamlit_app/theme.py`. Theme is built from `config.theme.UI_STYLE` when importable (same env + theme as Tkinter); otherwise from `config.env` only. All colors are converted to hex for CSS (no tkinter at runtime in theme).
- **Applied in:** `app.py` calls `get_streamlit_theme()` (cached in `st.session_state.streamlit_theme`), then `get_main_css(theme)`, and injects the returned CSS once per run.
- **Rules:** Main area uses `UI_BACKGROUND` and `UI_FOREGROUND`; sidebar uses a slightly lighter background (`sidebar_bg`); buttons use `UI_BUTTON_BG` and `UI_BUTTON_FG`; headings/accents use primary and accent2; fonts from `UI_FONT_FAMILY` and `UI_FONT_SIZE`.
- **Sidebar layout:** `sections/sidebar.py` defines layout-only CSS (brand, version badge, section labels); colors come from the global theme CSS.

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
from streamlit_app.sections import perform_fit, load_uploaded_file
from config import DATA_FILE_TYPES

st.title("Custom Fitting Interface")

uploaded_file = st.file_uploader("Upload data", type=list(DATA_FILE_TYPES))
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
                st.image(result['plot_path'], width='stretch')
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

*For more information about the Streamlit interface, see [Streamlit Guide](../streamlit-guide.md).*
