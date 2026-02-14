# frontend.ui_dialogs

UI Dialogs package containing all Tkinter dialog windows for user interaction.

## Overview

The `frontend.ui_dialogs` package provides all dialog windows used in the Tkinter interface. It is split into submodules; the package re-exports public functions so that `from frontend.ui_dialogs import open_load_dialog, show_help_dialog`, etc. continue to work.

All dialogs use `frontend.window_utils.place_window_centered` to appear centered on screen. Small dialogs keep their natural size; help and config dialogs use fixed dimensions (900×650 and 760×800 respectively).

**Package structure:**
- **`ui_dialogs/data_selection.py`** – `ask_variables`, `ask_multiple_x_variables`, `show_data_dialog`
- **`ui_dialogs/load_data_dialog.py`** – `open_load_dialog` (native file picker for loading CSV, TXT, XLSX)
- **`ui_dialogs/equation.py`** – `ask_equation_type`, `ask_num_parameters`, `ask_parameter_names`, `ask_custom_formula`, `ask_num_fits`
- **`ui_dialogs/help.py`** – `show_help_dialog`, `show_data_view_help_dialog`
- **`ui_dialogs/config_dialog.py`** – `show_config_dialog`
- **`ui_dialogs/result.py`** – `create_result_window`
- **`ui_dialogs/save_data_dialog.py`** – `open_save_dialog` (save DataFrame to file)
- **`ui_dialogs/tooltip.py`** – `bind_tooltip`

Dialogs cover file selection, variable selection, equation selection, and result display.

## File Selection Dialogs

#### `open_load_dialog(parent) -> Tuple[Optional[str], Optional[str]]`

Opens the native OS file dialog to select a data file (CSV, TXT, or XLSX).

Replaces the previous two-step flow (file type + file name) with a single native dialog. Works on Windows, Linux, and macOS. The default filter shows all supported formats; users can also filter by CSV, TXT, or XLSX only.

**Parameters:**
- `parent`: Parent Tkinter window (`Tk` or `Toplevel`)

**Returns:**
- `(file_path, file_type)` if user selects a file; `(None, None)` if user cancels
- `file_type` is one of `'csv'`, `'txt'`, `'xlsx'`

**Example:**
```python
from frontend.ui_dialogs import open_load_dialog
from tkinter import Tk

root = Tk()
path, file_type = open_load_dialog(root)
if path and file_type:
    print(f"Selected: {path} (type: {file_type})")
```

## Variable Selection Dialog

#### `ask_variables(parent_window, variable_names: list) -> Tuple[str, str, str]`

Dialog to select independent (x) and dependent (y) variables and plot name.

Presents a form to select x and y variables from the dataset columns, and allows the user to enter a custom plot name. The dialog filters out uncertainty columns (those starting with 'u') to avoid confusion.

**Parameters:**
- `parent_window`: Parent Tkinter window
- `variable_names`: List of available variable names from the dataset

**Returns:**
- Tuple of `(x_name, y_name, plot_name)`

**Example:**
```python
from frontend.ui_dialogs import ask_variables

variables = ['x', 'y', 'ux', 'uy', 'time', 'distance']
x_name, y_name, plot_name = ask_variables(root, variables)

if x_name and y_name:
    print(f"X: {x_name}, Y: {y_name}, Plot: {plot_name}")
```

**Notes:**
- Uncertainty columns (starting with 'u') are automatically filtered out.
- First variable is default for X, second for Y.
- Plot name is optional.

#### `ask_multiple_x_variables(parent_window, variable_names: List[str], num_vars: int, first_x_name: str) -> List[str]`

Dialog to select multiple independent (x) variables for multidimensional fitting (custom formulas with 2+ variables).

**Parameters:**
- `parent_window`: Parent Tkinter window
- `variable_names`: List of available variable names from the dataset
- `num_vars`: Number of independent variables to select (2 or more)
- `first_x_name`: Name of the first x variable already selected in the main variables dialog

**Returns:**
- List of x variable names in order (`[x_0, x_1, ...]`), or empty list if user cancels

**Example:**
```python
from frontend.ui_dialogs import ask_multiple_x_variables

x_names = ask_multiple_x_variables(root, ['temp', 'pressure', 'y'], num_vars=2, first_x_name='temp')
# User selects: ['temp', 'pressure'] -> x_names = ['temp', 'pressure']
```

## Data Display Dialog

#### `show_data_dialog(parent_window, data) -> None`

Dialog to display loaded data with optional transform, clean, and save options.

**Parameters:**
- `parent_window`: Parent Tkinter window
- `data`: Data to display (DataFrame or string representation)

**Example:**
```python
from frontend.ui_dialogs import show_data_dialog
import pandas as pd

data = pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 6]})
show_data_dialog(root, data)
```

**Features:**
- Scrollable text widget with table display.
- Monospaced font for alignment.
- Read-only display.
- **Pair plots**: Button to open scatter matrix of variable pairs. When there are more than 8 variables, a selection dialog appears first (max 10 for readability). Auto-updates when data is transformed or cleaned (if already open).
- **Save updated data**: Button opens file save dialog (CSV, TXT, XLSX).
- **Help**: Button opens `show_data_view_help_dialog` with detailed info about every option and mode (pair plots, transforms, cleaning, save). Content available in Spanish, English, and German.
- **Transform**: Dropdown (FFT, DCT, Hilbert, Laplace, cepstrum, Hadamard, envelope, log, exp, sqrt, standardize, normalize, etc., plus inverses) and Transform button (same style as equation buttons). Applies to all numeric columns.
- **Clean**: Dropdown (drop NaN, drop duplicates, fill NaN, remove outliers) and Clean button (same style as equation buttons).

## Save Data Dialog

#### `open_save_dialog(parent, data, on_focus_data) -> None`

Open a save file dialog for the current DataFrame.

**Parameters:**
- `parent`: Parent Toplevel window
- `data`: DataFrame to save
- `on_focus_data`: Callback to restore focus to the data window after save/cancel

**Example:**
```python
from frontend.ui_dialogs import open_save_dialog

open_save_dialog(parent_window, data_df, on_focus_data=parent_window.focus_set)
```

**Behavior:**
- Uses native file picker for save path.
- Supports CSV, TXT, XLSX formats.
- Saves via `loaders.saving_utils.save_dataframe`.

## Equation Selection Dialog

#### `ask_equation_type(parent_window) -> str`

Dialog to select fitting equation type.

Displays a grid of buttons for predefined equation types, plus options for custom equations and exiting. Each button represents a mathematical model that can be fitted to the data.

**Parameters:**
- `parent_window`: Parent Tkinter window

**Returns:**
- Selected equation type identifier, 'custom' for custom equation, or EXIT_SIGNAL to exit

**Example:**
```python
from frontend.ui_dialogs import ask_equation_type

selected = ask_equation_type(root)
if selected == 'custom':
    # Handle custom equation
    pass
elif selected and selected != EXIT_SIGNAL:
    print(f"Selected equation: {selected}")
```

**Available Equations:**
- Linear: `y=mx+n`, `y=mx`.
- Quadratic: `y=cx²+bx+a`, `y=ax²`.
- Fourth power: `y=ax⁴`.
- Trigonometric: `y=a sin(bx)`, `y=a sin(bx+c)`, `y=a cos(bx)`, `y=a cos(bx+c)`.
- Hyperbolic: `y=a sinh(bx)`, `y=a cosh(bx)`.
- Logarithmic: `y=a ln(x)`.
- Inverse: `y=a/x`, `y=a/x²`.
- Custom formula.

## Custom Equation Dialogs

#### `ask_num_parameters(parent_window) -> int`

Dialog to ask for number of parameters in a custom function.

**Parameters:**
- `parent_window`: Parent Tkinter window

**Returns:**
- Selected number of parameters (1-12)

**Example:**
```python
from frontend.ui_dialogs import ask_num_parameters

num_params = ask_num_parameters(root)
print(f"Number of parameters: {num_params}")
```

#### `ask_parameter_names(parent_window, num_params: int) -> List[str]`

Dialog to ask for parameter names in a custom function.

Shows a dialog for each parameter, allowing the user to enter parameter names. Supports Greek letters and provides a reference guide.

**Parameters:**
- `parent_window`: Parent Tkinter window
- `num_params`: Number of parameters to request

**Returns:**
- List of parameter names

**Example:**
```python
from frontend.ui_dialogs import ask_parameter_names

param_names = ask_parameter_names(root, 3)
# User enters: ['a', 'b', 'c']
print(f"Parameters: {param_names}")
```

**Features:**
- Greek letter reference guide.
- Exit option available.
- Validates parameter names.

#### `ask_custom_formula(parent_window, parameter_names: List[str]) -> str`

Dialog to ask for custom function formula.

**Parameters:**
- `parent_window`: Parent Tkinter window
- `parameter_names`: List of parameter names

**Returns:**
- Formula entered by the user

**Example:**
```python
from frontend.ui_dialogs import ask_custom_formula

params = ['a', 'b', 'c']
formula = ask_custom_formula(root, params)
# User enters: "a*x**2 + b*x + c"
print(f"Formula: {formula}")
```

**Features:**
- Greek letter reference guide.
- Shows parameter names for reference.
- Exit option available.

## Multiple Fits Dialog

#### `ask_num_fits(parent_window, min_val: int = 2, max_val: int = 10) -> int`

Dialog to ask for number of multiple fits.

**Parameters:**
- `parent_window`: Parent Tkinter window
- `min_val`: Minimum number of fits (default: 2)
- `max_val`: Maximum number of fits (default: 10)

**Returns:**
- Selected number of fits

**Example:**
```python
from frontend.ui_dialogs import ask_num_fits

num_fits = ask_num_fits(root, min_val=2, max_val=5)
print(f"Number of fits: {num_fits}")
```

## Help Dialog

#### `show_data_view_help_dialog(parent_window: Tk | Toplevel) -> None`

Display help dialog for the Watch Data window (transform, clean, save options).

Shows a dialog with **collapsible sections**: Pair plots, Transform (with each option detailed), Clean (with each option detailed), and Save. Content is localized (Spanish, English, German). Window size: up to 900×650 px; **Accept** button fixed at bottom.

**Parameters:**
- `parent_window`: Parent Tkinter window (the data view Toplevel)

**Example:**
```python
from frontend.ui_dialogs import show_data_view_help_dialog

show_data_view_help_dialog(watch_data_window)
```

#### `show_help_dialog(parent_window: Tk | Toplevel) -> None`

Display help and information dialog about the application.

**Parameters:**
- `parent_window`: Parent Tkinter window

**Content (collapsible sections):**
- **Objective**: What RegressionLab does
- **Advantages**: Key benefits (9 points)
- **Fitting Modes**: Normal, Multiple Datasets, Checker, Total, View Data, Loop mode
- **Custom Functions**: How to define custom formulas
- **Data Format**: Column names, uncertainty prefix (`u`), non-negative uncertainties
- **Data Location**: Input directory, supported file formats
- **Output Location**: Where plots and logs are saved
- **View Data Options**: Pair plots, transforms, cleaning, save (detailed reference)
- **Statistics**: R², RMSE, χ², reduced χ², DoF, 95% parameter confidence intervals

**Features:**
- Collapsible sections (click header to expand/collapse); first two sections expanded by default.
- Scrollable content with mouse wheel.
- Sizing: up to 70% of screen width/height (max 900×650).
- Optional **Donations** button at bottom if `DONATIONS_URL` is set in config.
- **Accept** button closes the dialog.

**Example:**
```python
from frontend.ui_dialogs import show_help_dialog

show_help_dialog(root)
```

## Configuration Dialog

#### `show_config_dialog(parent_window: Any) -> bool`

Show the configuration dialog to edit `.env` settings (same options as in the Configuration Guide).

**Parameters:**
- `parent_window`: Parent Tkinter window (Tk or Toplevel)

**Returns:**
- `True` if the user clicked **Accept** and the `.env` file was written successfully (caller should restart the application).
- `False` if the user clicked **Cancel** or closed the window.

**Behavior:**
- Dialog is modal and grouped by **collapsible sections** derived from `ENV_SCHEMA`: Language, UI, Plot, Font, Paths, Links, Updates, Logging. Click a section header to expand or collapse.
- Each option shows a label and description (from i18n keys `config.label_*`, `config.desc_*`). Values are edited via:
  - **Checkboxes** for boolean keys (e.g. `PLOT_SHOW_TITLE`, `PLOT_SHOW_GRID`, `LOG_CONSOLE`).
  - **Dropdowns** (read-only combobox) for keys with `options` in the schema (e.g. `LANGUAGE`, `FILE_PLOT_FORMAT`, `LOG_LEVEL`).
  - **Text entries** for other keys.
- **Accept**: Validates and writes all schema keys to `.env` (via `write_env_file`), then closes the dialog and returns `True`. On write error, shows an error message and keeps the dialog open.
- **Cancel** (or WM_DELETE_WINDOW): Closes the dialog and returns `False`.
- A hint at the bottom reminds the user that the application will restart after saving.

**Example:**
```python
from frontend.ui_dialogs import show_config_dialog

if show_config_dialog(root):
    # User saved; restart the app (e.g. os.execv or relaunch main)
    pass
```

## Result Display Dialog

#### `create_result_window(fit_name: str, text: str, equation_str: str, output_path: str, figure_3d: Optional[Any] = None, fit_info: Optional[Dict[str, Any]] = None) -> Toplevel`

Create a Tkinter window to display the fitting results.

**Parameters:**
- `fit_name`: Name of the fit for window title
- `text`: Formatted text with parameters, uncertainties, R², and statistics
- `equation_str`: Formatted equation string
- `output_path`: Path to the plot image file
- `figure_3d`: Optional matplotlib Figure for 3D plot (embeds interactive canvas; used for 2-variable fits)
- `fit_info`: Optional dict with keys `fit_func`, `params`, `cov`, `x_names`; when provided, adds a **Prediction** button to evaluate the fitted function at user-specified inputs with uncertainty propagation

**Returns:**
- The created Toplevel window

**Example:**
```python
from frontend.ui_dialogs import create_result_window

result_window = create_result_window(
    fit_name='Linear Fit',
    text='a = 2.0 ± 0.1\nb = 1.0 ± 0.05\nR²=0.99',
    equation_str='y = 2.0*x + 1.0',
    output_path='output/fit.png'
)

# With prediction support:
result_window = create_result_window(
    fit_name='Linear Fit',
    text=param_text,
    equation_str=equation,
    output_path='output/fit.png',
    fit_info={'fit_func': fit_func, 'params': popt, 'cov': pcov, 'x_names': ['x']}
)
# Window shows a Prediction button; clicking it opens a dialog to evaluate at user inputs
```

**Layout:**
- **Top**: Equation (selectable text).
- **Middle**: Parameters (left) and plot image or 3D canvas (right).
- **Bottom**: Accept button; optionally **Prediction** button when `fit_info` is provided.

## Usage Examples

### Complete Workflow

```python
from frontend.ui_dialogs import (
    open_load_dialog, ask_variables,
    ask_equation_type, ask_num_parameters,
    ask_parameter_names, ask_custom_formula
)

# 1. Select file (native file picker)
path, file_type = open_load_dialog(root)
if not path or not file_type:
    return

# 2. Load data (e.g. via loaders.load_data(path, file_type)), then select variables
variables = ['x', 'y', 'ux', 'uy']
x_name, y_name, plot_name = ask_variables(root, variables)
if not x_name or not y_name:
    return

# 3. Select equation
eq_type = ask_equation_type(root)
if eq_type == 'custom':
    num_params = ask_num_parameters(root)
    param_names = ask_parameter_names(root, num_params)
    formula = ask_custom_formula(root, param_names)
```

### Displaying Results

```python
from frontend.ui_dialogs import create_result_window

# After performing fit
result_window = create_result_window(
    fit_name='My Fit',
    text=parameter_text,
    equation_str=equation,
    output_path=plot_path,
    r_squared=r_squared
)

# Window stays open until user clicks Accept
```

## Best Practices

1. **Error Handling**: Always check return values
   ```python
   path, file_type = open_load_dialog(root)
   if not path or not file_type:
       return  # User cancelled
   ```

2. **Validation**: Validate user input before proceeding
   ```python
   x_name, y_name, plot_name = ask_variables(root, variables)
   if not x_name or not y_name:
       messagebox.showwarning("Error", "Please select both variables")
       return
   ```

3. **User Feedback**: Provide clear feedback
   ```python
   if selected == EXIT_SIGNAL:
       print("User cancelled operation")
   ```

## Technical Details

### Dialog Behavior

- **Modal**: All dialogs are modal (block parent window).
- **Focus**: First input widget receives focus.
- **Keyboard**: Enter key typically accepts, Escape cancels.
- **Styling**: Uses `config.UI_STYLE` for consistent appearance.

### Internationalization

All dialog text is translated using the `i18n` module:
- Dialog titles.
- Labels and messages.
- Button text.
- Help content.

### Widget Types

- **Native file dialog**: File selection (via `open_load_dialog`).
- **Combobox**: Variable selection.
- **Entry**: Text input (plot name, formula, parameters).
- **Spinbox**: Numeric input (number of parameters, fits).
- **Text**: Multi-line display (data, help, results).

---

*For more information about dialogs, see [Tkinter Guide](../tkinter-guide.md).*
