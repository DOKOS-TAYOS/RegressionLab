# frontend.keyboard_nav

Keyboard navigation utilities for Tkinter dialogs.

## Overview

The `frontend.keyboard_nav` module provides utilities for implementing keyboard navigation in Tkinter dialogs. It enables arrow key navigation between widgets and Enter key activation, improving accessibility and user experience.

## Functions

### `bind_enter_to_accept(widgets: Sequence[Any], accept_callback: Callable[[], None]) -> None`

Bind `<Return>` and `<KP_Enter>` on each widget to `accept_callback`, so that pressing Enter from a Spinbox, Entry, Combobox, etc. triggers accept.

This function makes it easy to add Enter key support to input widgets, allowing users to confirm their input by pressing Enter instead of clicking a button.

**Parameters:**
- `widgets`: Sequence of Tkinter widgets (Entry, Spinbox, Combobox, etc.)
- `accept_callback`: Function to call when Enter is pressed

**Example:**
```python
from frontend.keyboard_nav import bind_enter_to_accept
from tkinter import ttk

def on_accept():
    print("Enter pressed!")

entry = ttk.Entry(root)
spinbox = ttk.Spinbox(root)
bind_enter_to_accept([entry, spinbox], on_accept)
```

### `setup_arrow_enter_navigation(widgets_grid: Sequence[Sequence[Any]], on_enter: Optional[Callable[[Any, Event], bool]] = None) -> None`

Bind arrow keys to move focus in the given direction and Return/Enter to activate the focused widget.

Creates a grid-based navigation system where:
- **Arrow keys** (← → ↑ ↓) move focus between widgets
- **Enter/Return** activates the focused widget (typically invokes a button)
- `widgets_grid` is a 2D list of focusable widgets (e.g., `ttk.Button`); use `None` for empty cells

If `on_enter` is provided, it is called as `on_enter(widget, event)`. If it returns `True`, the default behavior (invoke button) is skipped. Use it to handle Enter on non-button widgets (e.g., radiobutton -> confirm dialog).

When activating the focused widget, the module calls `invoke()` on the widget if it has that method. If `invoke()` raises `tkinter.TclError` (e.g., widget in an invalid state or window being destroyed), the error is caught and ignored so the application does not crash.

**Parameters:**
- `widgets_grid`: 2D sequence of widgets (rows × columns). Use `None` for empty cells
- `on_enter`: Optional callback `(widget, event) -> bool`. If returns `True`, skips default button invoke

**Example:**
```python
from frontend.keyboard_nav import setup_arrow_enter_navigation
from tkinter import ttk

# Create a grid of buttons
button1 = ttk.Button(root, text="Button 1")
button2 = ttk.Button(root, text="Button 2")
button3 = ttk.Button(root, text="Button 3")
button4 = ttk.Button(root, text="Button 4")

# Arrange in 2x2 grid
widgets_grid = [
    [button1, button2],
    [button3, button4]
]

# Setup navigation: arrow keys move, Enter activates
setup_arrow_enter_navigation(widgets_grid)

# Now users can:
# - Press → to move from button1 to button2
# - Press ↓ to move from button1 to button3
# - Press Enter to activate the focused button
```

**Advanced Example with Custom Enter Handler:**
```python
def custom_enter_handler(widget, event):
    """Handle Enter key on specific widgets."""
    if isinstance(widget, ttk.Radiobutton):
        # Select radiobutton and show confirmation
        widget.invoke()
        show_confirmation_dialog()
        return True  # Skip default behavior
    return False  # Use default behavior

setup_arrow_enter_navigation(widgets_grid, on_enter=custom_enter_handler)
```

## Usage Patterns

### Simple Form with Enter Key Support

```python
from frontend.keyboard_nav import bind_enter_to_accept
from tkinter import ttk

def submit_form():
    # Process form data
    print("Form submitted!")

entry1 = ttk.Entry(root)
entry2 = ttk.Entry(root)
submit_button = ttk.Button(root, text="Submit", command=submit_form)

# Press Enter in any entry to submit
bind_enter_to_accept([entry1, entry2], submit_form)
```

### Dialog with Grid Navigation

```python
from frontend.keyboard_nav import setup_arrow_enter_navigation
from tkinter import ttk

# Create dialog buttons
ok_button = ttk.Button(dialog, text="OK")
cancel_button = ttk.Button(dialog, text="Cancel")

# Arrange buttons horizontally
button_row = [ok_button, cancel_button]

# Enable arrow key navigation (left/right) and Enter activation
setup_arrow_enter_navigation([button_row])
```

## Supported Widgets

These functions work with any Tkinter widget that:
- Can receive focus (`focus_set()` method)
- Can be invoked (`invoke()` method for buttons)

Common widget types:
- `ttk.Button`
- `ttk.Entry`
- `ttk.Spinbox`
- `ttk.Combobox`
- `ttk.Radiobutton`
- `ttk.Checkbutton`

## Keyboard Bindings

The module binds the following keys:

- **`<Return>`**: Enter key (main keyboard)
- **`<KP_Enter>`**: Enter key (numeric keypad)
- **`<Left>`**: Left arrow key
- **`<Right>`**: Right arrow key
- **`<Up>`**: Up arrow key
- **`<Down>`**: Down arrow key

## Best Practices

1. **Grid Layout**: Use `setup_arrow_enter_navigation` with widgets arranged in a logical grid
2. **Empty Cells**: Use `None` for empty cells in the grid to skip them during navigation
3. **Focus Management**: Ensure widgets are focusable (`takefocus=True` for some widgets)
4. **Visual Feedback**: Consider highlighting focused widgets for better UX
5. **Accessibility**: Keyboard navigation improves accessibility for users who prefer keyboard over mouse

## Integration with Dialogs

These utilities are used throughout the `frontend.ui_dialogs` package to provide consistent keyboard navigation:

- File selection dialogs
- Variable selection dialogs
- Equation selection dialogs
- Configuration dialogs

---

*For more information about frontend dialogs, see [ui_dialogs](ui_dialogs.md) and [ui_main_menu](ui_main_menu.md).*
