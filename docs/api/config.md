# config

Configuration package for RegressionLab.

## Overview

The `config` package centralizes all application configuration, constants, and settings. It is split into submodules; the main package re-exports everything so that `from config import PLOT_CONFIG`, `from config import __version__`, etc. continue to work.

**Package structure:**
- **`config/env.py`** – Environment variables, `.env` loading, `get_env`, `get_current_env_values`, `write_env_file`
- **`config/theme.py`** – `UI_THEME`, `UI_STYLE`, `PLOT_CONFIG`, `FONT_CONFIG`, `setup_fonts`
- **`config/paths.py`** – `FILE_CONFIG`, `get_project_root`, `ensure_output_directory`, `get_output_path`
- **`config/constants.py`** – `__version__`, `EQUATIONS`, `AVAILABLE_EQUATION_TYPES`, `EXIT_SIGNAL`, `MATH_FUNCTION_REPLACEMENTS`, `SUPPORTED_LANGUAGE_CODES`, `LANGUAGE_ALIASES`, `DATA_FILE_TYPES`
- **`config/equations.yaml`** – Single source of truth for equation definitions (function name, formula, param_names). Loaded by `constants.py` into `EQUATIONS`.

Usage remains the same: import from `config` (e.g. `from config import PLOT_CONFIG, get_project_root`).

## Key Components

### Application Metadata

```python
__version__ = "0.9.0"
__author__ = "Alejandro Mata Ali"
__email__ = "alejandro.mata.ali@gmail.com"
```

### Equations Configuration

Equations are defined in **`config/equations.yaml`**. Each entry has:
- **`function`**: Name of the fitting function (e.g. `fit_linear_function_with_n`)
- **`formula`**: Display formula for the UI (e.g. `"y = mx + n"`)
- **`param_names`**: List of parameter names for the fit

`constants.py` loads this file into the **`EQUATIONS`** dictionary. The keys of `EQUATIONS` are the equation IDs; **`AVAILABLE_EQUATION_TYPES`** is the list of those keys (order matches the YAML file).

```python
# EQUATIONS structure (from equations.yaml)
EQUATIONS = {
    'linear_function_with_n': {
        'function': 'fit_linear_function_with_n',
        'formula': 'y = mx + n',
        'param_names': ['n', 'm'],
    },
    'linear_function': { 'function': 'fit_linear_function', 'formula': 'y = mx', 'param_names': ['m'] },
    # ...
}
AVAILABLE_EQUATION_TYPES = list(EQUATIONS.keys())  # Same order as in YAML
```

This defines which equations appear in the UI and how they are invoked.

### Configuration Dictionaries

The module provides configuration dictionaries that are loaded from environment variables:

#### `PLOT_CONFIG`

Dictionary containing plot configuration settings:

```python
PLOT_CONFIG = {
    'figsize': (12, 6),           # Figure size (width, height) in inches
    'dpi': 100,                   # Resolution
    'line_color': 'black',        # Fitted curve color
    'line_width': 1.0,            # Fitted curve width
    'line_style': '-',            # Line style ('-', '--', '-.', ':')
    'marker_format': 'o',         # Marker style ('o', 's', '^', 'd')
    'marker_size': 5,             # Marker size
    'error_color': 'crimson',     # Error bar color
    'marker_face_color': 'crimson',  # Marker fill color
    'marker_edge_color': 'crimson',  # Marker edge color
    'show_title': False           # Show plot title
}
```

#### `UI_THEME`

Dictionary containing UI theme configuration for Tkinter:

```python
UI_THEME = {
    'background': 'midnight blue',
    'foreground': 'snow',
    'button_fg': 'lime green',
    'button_fg_cancel': 'red2',
    'button_fg_cyan': 'cyan2',
    'active_bg': 'navy',
    'active_fg': 'snow',
    'border_width': 8,
    'relief': 'ridge',
    'padding_x': 8,
    'padding_y': 8,
    'button_width': 12,
    'button_width_wide': 28,
    'font_size': 16,
    'font_size_large': 20,
    'font_family': 'Menlo',
    'spinbox_width': 10,
    'entry_width': 25
}
```

#### `UI_STYLE`

Backwards-compatible mapping for dialog components (uses `UI_THEME` values).

#### `FONT_CONFIG`

Dictionary containing font configuration for plots:

```python
FONT_CONFIG = {
    'family': 'serif',
    'title_size': 'xx-large',
    'title_weight': 'semibold',
    'axis_size': 30,
    'axis_style': 'italic',
    'tick_size': 16,
    'param_font': ('Courier', 10)
}
```

### Configuration Functions

#### `get_env(key, default, cast_type=str)`

Generic function to get environment variables with type casting.

```python
def get_env(key: str, default, cast_type=str):
    """
    Get environment variable with type casting and default value.
    
    Args:
        key: Environment variable name
        default: Default value if variable not found
        cast_type: Type to cast the value to (str, int, float, bool)
        
    Returns:
        The environment variable value cast to the specified type, or default
    """
```

#### `setup_fonts()`

Setup and return font properties for plots.

```python
def setup_fonts() -> Tuple[FontProperties, FontProperties]:
    """
    Setup and return font properties for plots.
    Uses caching to avoid recreating fonts on every call.
    
    Returns:
        Tuple of (title_font, axis_font) FontProperties objects
    """
```

#### `get_project_root() -> Path`

Get the project root directory.

```python
def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root (parent of src/)
    """
```

#### `ensure_output_directory(output_dir=None) -> str`

Create output directory if it doesn't exist.

```python
def ensure_output_directory(output_dir: str = None) -> str:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Optional directory path. If None, uses FILE_CONFIG['output_dir']
        
    Returns:
        The output directory path (absolute path from project root)
        
    Raises:
        OSError: If directory cannot be created
    """
```

#### `get_output_path(fit_name, output_dir=None) -> str`

Get the full output path for a plot.

```python
def get_output_path(fit_name: str, output_dir: str = None) -> str:
    """
    Get the full output path for a plot.
    
    Args:
        fit_name: Name of the fit/adjustment (used in filename)
        output_dir: Optional directory path. If None, uses FILE_CONFIG['output_dir']
        
    Returns:
        Full path to the output file
    """
```

## Environment Variables

Configuration is loaded from `.env` file using `python-dotenv`.

### Example Configuration

```ini
# Language
LANGUAGE="es"

# Plot settings
PLOT_FIGSIZE_WIDTH=12
PLOT_FIGSIZE_HEIGHT=6
DPI=100
PLOT_LINE_COLOR="black"

# UI settings (Tkinter)
UI_BACKGROUND="midnight blue"
UI_FOREGROUND="snow"
UI_FONT_SIZE=16

# File paths
FILE_INPUT_DIR="input"
FILE_OUTPUT_DIR="output"

# Logging
LOG_LEVEL=INFO
LOG_FILE=regressionlab.log
```

See [Configuration Guide](../configuration.md) for complete documentation.

## Constants

### Signals

```python
EXIT_SIGNAL = "Exit"  # Returned when user cancels operation
```

### File Configuration

```python
FILE_CONFIG = {
    'input_dir': 'input',           # Input directory for data files
    'output_dir': 'output',         # Output directory for plots
    'filename_template': 'fit_{}', # Filename template ({} replaced by fit name)
    'plot_format': 'png'            # Output plot format (png, jpg, or pdf)
}
```
Values are read from `.env` (e.g. `FILE_INPUT_DIR`, `FILE_OUTPUT_DIR`, `FILE_FILENAME_TEMPLATE`, `FILE_PLOT_FORMAT`).

Equation-to-function mapping is provided by the **`function`** field of each entry in **`EQUATIONS`** (loaded from `equations.yaml`). The workflow controller and UI use `EQUATIONS[eq_id]['function']` to resolve the fitting function name.

## Usage Examples

### Getting Current Configuration

```python
from config import PLOT_CONFIG, UI_THEME, FONT_CONFIG, __version__, get_project_root

# Application version
print(f"RegressionLab v{__version__}")

# Plot configuration (dictionary, not function)
print(f"Figure size: {PLOT_CONFIG['figsize']}")
print(f"DPI: {PLOT_CONFIG['dpi']}")

# UI theme configuration
print(f"Background: {UI_THEME['background']}")
print(f"Font size: {UI_THEME['font_size']}")

# Font configuration
print(f"Font family: {FONT_CONFIG['family']}")

# Project root
root = get_project_root()
print(f"Project root: {root}")
```

### Checking Available Equations

```python
from config import AVAILABLE_EQUATION_TYPES, EQUATIONS

# List all equations
print(f"Available equations: {len(AVAILABLE_EQUATION_TYPES)}")
for eq_id in AVAILABLE_EQUATION_TYPES:
    info = EQUATIONS[eq_id]
    print(f"  - {eq_id}: {info['formula']} -> {info['function']}")

# Check if equation exists
if 'linear_function' in AVAILABLE_EQUATION_TYPES:
    print("Linear fitting available")
```

### Adding New Equations

To add a new equation to the system:

1. Implement the mathematical and fitting functions in the appropriate module under `fitting/functions/` (e.g. `special.py`, `polynomials.py`).
2. Add an entry to **`config/equations.yaml`** with `function`, `formula`, and `param_names`. The key is the equation ID (e.g. `my_equation`).
3. Add translations for the equation ID in `src/locales/en.json`, `src/locales/es.json`, and `src/locales/de.json` under the `equations` key.

## Configuration Best Practices

### For End Users

1. **Copy template**: Start with `.env.example`
   ```bash
   cp .env.example .env
   ```

2. **Modify gradually**: Change one setting at a time
3. **Restart app**: Changes require restart
4. **Keep backup**: Save working configuration

### For Developers

1. **Add defaults**: Always provide fallback values
   ```python
   line_width = float(os.getenv('PLOT_LINE_WIDTH', 1.0))
   ```

2. **Validate input**: Check types and ranges
   ```python
   dpi = int(os.getenv('DPI', 100))
   if dpi < 50 or dpi > 1200:
       dpi = 100  # Reset to default
   ```

3. **Document new settings**: Update `.env.example` and docs
4. **Type hints**: Use proper types in getters
   ```python
   def get_dpi() -> int:
       return int(os.getenv('DPI', 100))
   ```

## Technical Details

### Loading Order

1. Environment variables loaded from `.env` (see `config/env.py`)
2. Defaults applied for missing values
3. Validation performed
4. Configuration exposed via package; values are effectively immutable during runtime

### Thread Safety

Configuration is loaded once at startup. Changes to `.env` during runtime are not reflected until restart.

### Performance

- Configuration loaded once per module
- Values cached in memory
- No disk I/O after initial load

---

*For complete configuration options, see [Configuration Guide](../configuration.md)*
