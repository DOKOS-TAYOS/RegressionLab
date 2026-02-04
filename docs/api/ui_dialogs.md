# frontend.ui_dialogs

UI Dialogs package containing all Tkinter dialog windows for user interaction.

## Overview

The `frontend.ui_dialogs` package provides all dialog windows used in the Tkinter interface. It is split into submodules; the package re-exports public functions so that `from frontend.ui_dialogs import ask_file_type, show_help_dialog`, etc. continue to work.

**Package structure:**
- **`ui_dialogs/data_selection.py`** – `ask_file_type`, `ask_file_name`, `ask_variables`, `show_data_dialog`, `get_variable_names`
- **`ui_dialogs/equation.py`** – `ask_equation_type`, `ask_num_parameters`, `ask_parameter_names`, `ask_custom_formula`, `ask_num_fits`
- **`ui_dialogs/help.py`** – `show_help_dialog`
- **`ui_dialogs/config_dialog.py`** – `show_config_dialog`
- **`ui_dialogs/result.py`** – `create_result_window`
- **`ui_dialogs/tooltip.py`** – `bind_tooltip`

Dialogs cover file selection, variable selection, equation selection, and result display.

## File Selection Dialogs

#### `ask_file_type(parent_window) -> str`

Dialog to ask for data file type.

Presents radio buttons with file type options (xlsx, csv, txt, Exit/Salir). User can select one option.

**Parameters:**
- `parent_window`: Parent Tkinter window

**Returns:**
- Selected file type ('csv', 'xlsx', 'txt', EXIT_SIGNAL, or '')

**Example:**
```python
from frontend.ui_dialogs import ask_file_type
from tkinter import Tk

root = Tk()
file_type = ask_file_type(root)
if file_type and file_type != EXIT_SIGNAL:
    print(f"Selected: {file_type}")
```

#### `ask_file_name(parent_window, file_list: list) -> str`

Dialog to select a specific file from the list.

**Parameters:**
- `parent_window`: Parent Tkinter window
- `file_list`: List of available file names

**Returns:**
- Selected file name (without extension)

**Example:**
```python
from frontend.ui_dialogs import ask_file_name

file_list = ['data1', 'data2', 'experiment1']
selected = ask_file_name(root, file_list)
if selected:
    print(f"Selected file: {selected}")
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
- Uncertainty columns (starting with 'u') are automatically filtered out
- First variable is default for X, second for Y
- Plot name is optional

## Data Display Dialog

#### `show_data_dialog(parent_window, data) -> None`

Dialog to display loaded data.

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
- Scrollable text widget
- Monospaced font for alignment
- Read-only display
- Terminal-style appearance (dark background, green text)

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
- Linear: `y=mx+n`, `y=mx`
- Quadratic: `y=cx²+bx+a`, `y=ax²`
- Fourth power: `y=ax⁴`
- Trigonometric: `y=a sin(bx)`, `y=a sin(bx+c)`, `y=a cos(bx)`, `y=a cos(bx+c)`
- Hyperbolic: `y=a sinh(bx)`, `y=a cosh(bx)`
- Logarithmic: `y=a ln(x)`
- Inverse: `y=a/x`, `y=a/x²`
- Custom formula

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
- Greek letter reference guide
- Exit option available
- Validates parameter names

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
- Greek letter reference guide
- Shows parameter names for reference
- Exit option available

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

#### `show_help_dialog(parent_window: Tk | Toplevel) -> None`

Display help and information dialog about the application.

Shows information about:
- Application objective and purpose
- Key advantages and features
- What each fitting mode does
- How to navigate the application
- Where data files should be located
- Where output plots are saved

**Parameters:**
- `parent_window`: Parent Tkinter window

**Example:**
```python
from frontend.ui_dialogs import show_help_dialog

show_help_dialog(root)
```

**Features:**
- Scrollable content
- Formatted text display
- Responsive sizing (70% of screen)

## Result Display Dialog

#### `create_result_window(fit_name: str, text: str, equation_str: str, output_path: str, r_squared: float = None) -> Toplevel`

Create a Tkinter window to display the fitting results.

**Parameters:**
- `fit_name`: Name of the fit for window title
- `text`: Formatted text with parameters and uncertainties
- `equation_str`: Formatted equation string
- `output_path`: Path to the plot image file
- `r_squared`: Coefficient of determination (R²), optional

**Returns:**
- The created Toplevel window

**Example:**
```python
from frontend.ui_dialogs import create_result_window

result_window = create_result_window(
    fit_name='Linear Fit',
    text='a = 2.0 ± 0.1\nb = 1.0 ± 0.05',
    equation_str='y = 2.0*x + 1.0',
    output_path='output/fit.png',
    r_squared=0.99
)

# Window displays:
# - Equation at top
# - Parameters on left
# - Plot image on right
# - Accept button at bottom
```

**Layout:**
- **Top**: Equation (selectable text)
- **Middle**: Parameters (left) and plot image (right)
- **Bottom**: Accept button

## Usage Examples

### Complete Workflow

```python
from frontend.ui_dialogs import (
    ask_file_type, ask_file_name, ask_variables,
    ask_equation_type, ask_num_parameters,
    ask_parameter_names, ask_custom_formula
)

# 1. Select file type
file_type = ask_file_type(root)
if file_type == EXIT_SIGNAL:
    return

# 2. Select file
file_list = ['data1', 'data2']
file_name = ask_file_name(root, file_list)
if not file_name:
    return

# 3. Select variables
variables = ['x', 'y', 'ux', 'uy']
x_name, y_name, plot_name = ask_variables(root, variables)
if not x_name or not y_name:
    return

# 4. Select equation
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
   file_type = ask_file_type(root)
   if not file_type or file_type == EXIT_SIGNAL:
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

- **Modal**: All dialogs are modal (block parent window)
- **Focus**: First input widget receives focus
- **Keyboard**: Enter key typically accepts, Escape cancels
- **Styling**: Uses `config.UI_STYLE` for consistent appearance

### Internationalization

All dialog text is translated using the `i18n` module:
- Dialog titles
- Labels and messages
- Button text
- Help content

### Widget Types

- **RadioButtons**: File type selection
- **Combobox**: File and variable selection
- **Entry**: Text input (plot name, formula, parameters)
- **Spinbox**: Numeric input (number of parameters, fits)
- **Text**: Multi-line display (data, help, results)

---

*For more information about dialogs, see [Tkinter Guide](../tkinter-guide.md)*
