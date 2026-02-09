# frontend.ui_main_menu

Main menu module for the Tkinter interface.

## Overview

The `ui_main_menu.py` module contains the main application window and exit confirmation dialog for the Tkinter desktop interface.

## Key Functions

### Main Menu Creation

#### `create_main_menu(normal_fitting_callback, single_fit_multiple_datasets_callback, multiple_fits_single_dataset_callback, all_fits_single_dataset_callback, watch_data_callback, help_callback) -> Tk`

Create and display the main application menu window.

**Parameters:**
- `normal_fitting_callback`: Function to call for normal fitting
- `single_fit_multiple_datasets_callback`: Function to call for single fit on multiple datasets
- `multiple_fits_single_dataset_callback`: Function to call for multiple fits on single dataset
- `all_fits_single_dataset_callback`: Function to call for all fits on single dataset
- `watch_data_callback`: Function to call for viewing data
- `help_callback`: Function to display help information

**Returns:**
- The main Tk window instance

**Example:**
```python
from frontend.ui_main_menu import create_main_menu

def normal_fit():
    print("Normal fitting selected")

def view_data():
    print("View data selected")

menu = create_main_menu(
    normal_fitting_callback=normal_fit,
    single_fit_multiple_datasets_callback=lambda: print("Multiple datasets"),
    multiple_fits_single_dataset_callback=lambda: print("Multiple fits"),
    all_fits_single_dataset_callback=lambda: print("All fits"),
    watch_data_callback=view_data,
    help_callback=lambda: print("Help")
)

menu.mainloop()
```

### Application Startup

#### `start_main_menu(normal_fitting_callback, single_fit_multiple_datasets_callback, multiple_fits_single_dataset_callback, all_fits_single_dataset_callback, watch_data_callback, help_callback) -> None`

Create and run the main application menu.

This is the entry point for the GUI application.

**Parameters:**
- `normal_fitting_callback`: Function to call for normal fitting
- `single_fit_multiple_datasets_callback`: Function to call for single fit on multiple datasets
- `multiple_fits_single_dataset_callback`: Function to call for multiple fits on single dataset
- `all_fits_single_dataset_callback`: Function to call for all fits on single dataset
- `watch_data_callback`: Function to call for viewing data
- `help_callback`: Function to display help information

**Example:**
```python
from frontend.ui_main_menu import start_main_menu

# Define callbacks
def normal_fit():
    # Perform normal fitting
    pass

def view_data():
    # Show data viewer
    pass

# Start application
start_main_menu(
    normal_fitting_callback=normal_fit,
    single_fit_multiple_datasets_callback=lambda: None,
    multiple_fits_single_dataset_callback=lambda: None,
    all_fits_single_dataset_callback=lambda: None,
    watch_data_callback=view_data,
    help_callback=lambda: None
)
```

### Exit Confirmation

#### `show_exit_confirmation(parent_menu: Tk) -> None`

Display exit confirmation dialog.

**Parameters:**
- `parent_menu`: The parent menu window to close if user confirms exit

**Example:**
```python
from frontend.ui_main_menu import show_exit_confirmation
from tkinter import Tk

root = Tk()
show_exit_confirmation(root)
```

#### `close_application(menu: Tk) -> None`

Close the application and exit.

**Parameters:**
- `menu`: The main menu window to destroy

## Menu Structure

The main menu displays:

1. **Logo**: Application logo (if available)
2. **Welcome Message**: Translated welcome text
3. **Action Buttons** (in order):
   - Normal Fitting
   - Single Fit Multiple Datasets
   - Checker Fitting (Multiple fits on single dataset)
   - Total Fitting (All fits on single dataset)
   - Watch Data (View Data)
   - Information (Help dialog with collapsible sections; optional Donations button)
   - Configure (Configuration dialog to edit .env; saving restarts the app)
   - Exit
4. **Tooltips**: Information and Configure buttons have tooltips (from `menu.tooltip_information`, `menu.tooltip_config`).
5. **Exit**: Closes the application (with confirmation dialog when using the window close button or Exit).

## UI Styling

The menu uses styling from `config.UI_STYLE`:

- **Background**: Configurable background color
- **Foreground**: Configurable text color
- **Fonts**: Configurable font family and sizes
- **Buttons**: Styled with consistent colors and sizes

## Usage Examples

### Complete Application Setup

```python
from frontend.ui_main_menu import start_main_menu
from frontend.ui_dialogs import show_help_dialog
from fitting.workflow_controller import coordinate_data_loading
from frontend.ui_dialogs import (
    ask_file_type, ask_file_name, ask_variables
)

def normal_fitting():
    """Handle normal fitting mode."""
    result = coordinate_data_loading(
        parent_window=root,
        ask_file_type_func=ask_file_type,
        ask_file_name_func=ask_file_name,
        ask_variables_func=ask_variables
    )
    if result:
        # Perform fitting
        pass

def view_data():
    """Handle data viewing."""
    # Show data viewer
    pass

# Start application
start_main_menu(
    normal_fitting_callback=normal_fitting,
    single_fit_multiple_datasets_callback=lambda: None,
    multiple_fits_single_dataset_callback=lambda: None,
    all_fits_single_dataset_callback=lambda: None,
    watch_data_callback=view_data,
    help_callback=lambda: show_help_dialog(root)
)
```

### Custom Menu with Logo

The menu automatically loads the logo from `images/RegressionLab_logo_app.png` if available:

```python
from frontend.ui_main_menu import create_main_menu

menu = create_main_menu(
    normal_fitting_callback=lambda: None,
    single_fit_multiple_datasets_callback=lambda: None,
    multiple_fits_single_dataset_callback=lambda: None,
    all_fits_single_dataset_callback=lambda: None,
    watch_data_callback=lambda: None,
    help_callback=lambda: None
)

# Logo is automatically loaded and displayed if file exists
menu.mainloop()
```

## Integration with Main Program

The main menu is typically used in `main_program.py`:

```python
# main_program.py
from frontend.ui_main_menu import start_main_menu
from utils.logger import setup_logging, get_logger
from i18n import initialize_i18n

# Initialize
setup_logging()
initialize_i18n()

# Define callbacks
def normal_fitting():
    # Implementation
    pass

# ... other callbacks ...

# Start application
start_main_menu(
    normal_fitting_callback=normal_fitting,
    # ... other callbacks ...
)
```

## Best Practices

1. **Callback Functions**: Keep callbacks focused and simple
   ```python
   def normal_fitting():
       # Simple, focused callback
       perform_fitting_workflow()
   ```

2. **Error Handling**: Handle errors in callbacks
   ```python
   def normal_fitting():
       try:
           perform_fitting_workflow()
       except Exception as e:
           messagebox.showerror("Error", str(e))
   ```

3. **State Management**: Use global state or session objects if needed
   ```python
   class AppState:
       def __init__(self):
           self.current_data = None
           self.current_fit = None

   app_state = AppState()

   def normal_fitting():
       result = coordinate_data_loading(...)
       if result:
           app_state.current_data = result[0]
   ```

## Technical Details

### Window Management

- **Window Type**: Tk (root window)
- **Resizable**: Yes (width and height)
- **Fullscreen**: No (can be configured)
- **Focus**: First button receives focus

### Logo Loading

- **Path**: `images/RegressionLab_logo_app.png`
- **Resizing**: Automatically resized to max width of 600px
- **Fallback**: Continues without logo if file not found

### Internationalization

All text is translated using the `i18n` module:
- Menu title.
- Welcome message.
- Button labels.
- Exit confirmation.

---

*For more information about the UI, see [Tkinter Guide](../tkinter-guide.md).*
