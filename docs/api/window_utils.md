# frontend.window_utils

Utilities for positioning Tkinter windows on screen.

## Overview

The `frontend.window_utils` module provides functions to center Toplevel windows on the screen. All dialogs in the Tkinter interface use this module so that windows appear in consistent positions instead of random locations.

## Functions

### `place_window_centered(win, width=None, height=None, *, preserve_size=False, max_width=900, max_height=650, max_width_ratio=0.7, max_height_ratio=0.7) -> None`

Position a Toplevel window centered on screen.

**Parameters:**
- `win`: The Toplevel window to position
- `width`: Desired width in pixels. If `None` and not `preserve_size`, uses computed size from `max_width` and `max_width_ratio`
- `height`: Desired height in pixels. If `None` and not `preserve_size`, uses computed size from `max_height` and `max_height_ratio`
- `preserve_size`: If `True`, keeps the window's current size and only sets position. Call after widgets are packed/gridded and after `win.update_idletasks()`
- `max_width`: Cap for width when computed from screen (default 900)
- `max_height`: Cap for height when computed from screen (default 650)
- `max_width_ratio`: Max width as fraction of screen (0.0–1.0). Applied when `width` is `None` or to cap explicit `width` on small screens
- `max_height_ratio`: Max height as fraction of screen (0.0–1.0). Applied when `height` is `None` or to cap explicit `height` on small screens

**Usage patterns:**
- **Preserve natural size** (most dialogs): Call after building content, use `preserve_size=True`
- **Fixed size** (help, config): Pass explicit `width` and `height`; ratios cap size on small screens

**Example:**
```python
from frontend.window_utils import place_window_centered
from tkinter import Toplevel, ttk

# Dialog with natural size (from layout)
dlg = Toplevel()
frame = ttk.Frame(dlg, padding=10)
frame.pack()
ttk.Label(frame, text="Select option:").pack()
ttk.Button(frame, text="OK", command=dlg.destroy).pack()
place_window_centered(dlg, preserve_size=True)

# Dialog with fixed size (e.g. help window)
help_win = Toplevel()
# ... build content ...
place_window_centered(help_win, 900, 650, max_width_ratio=0.7, max_height_ratio=0.7)
```
