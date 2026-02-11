# frontend.image_utils

Image loading and scaling utilities for the Tkinter frontend.

## Overview

The `frontend.image_utils` module provides utilities for handling images in the Tkinter GUI, particularly for displaying plot images. It handles PDF preview generation and image scaling to fit display constraints.

## Functions

### `plot_display_path(output_path: str) -> str`

Return the path to use for displaying a plot in the GUI.

When the saved file is PDF, returns the `_preview.png` path if it exists, so Tkinter can show the image without breaking (Tkinter cannot display PDF files directly).

**Parameters:**
- `output_path`: Full path to the saved plot file (e.g., PDF or PNG)

**Returns:**
- Path to the image file to display (preview PNG for PDFs when available, otherwise the original path)

**Example:**
```python
from frontend.image_utils import plot_display_path

# If output is PDF, returns preview PNG path
display_path = plot_display_path("/output/fit_result.pdf")
# Returns: "/output/fit_result_preview.png" if preview exists
# Otherwise: "/output/fit_result.pdf"
```

### `preview_path_to_remove_after_display(display_path: str, original_output_path: str) -> Optional[str]`

Return the path of an auxiliary preview file to remove after display.

If the displayed image is an auxiliary preview file (`_preview.png`), return its path so the caller can delete it after the window is closed. This helps clean up temporary preview files created for PDF display.

**Parameters:**
- `display_path`: Path actually used for display (may be preview PNG)
- `original_output_path`: Original output path (e.g., PDF path)

**Returns:**
- Path to the preview file to delete, or `None` if no cleanup needed

**Example:**
```python
from frontend.image_utils import preview_path_to_remove_after_display

display_path = "/output/fit_result_preview.png"
original_path = "/output/fit_result.pdf"
preview_to_remove = preview_path_to_remove_after_display(display_path, original_path)
# Returns: "/output/fit_result_preview.png"
# After window closes, delete this file
```

### `load_image_scaled(path: str, max_width: int, max_height: int) -> Optional[Any]`

Load an image from file and return a Tk PhotoImage scaled to fit within max dimensions.

Uses PIL (Pillow) when available. The image is converted to RGB, so transparency is not preserved—this is intended for plot previews. For logos or images that need transparency, load with PIL directly (e.g., in `ui_main_menu`). Supports PNG, JPG, JPEG. Returns `None` if the file cannot be opened (e.g., missing PIL), so callers can fall back to `tkinter.PhotoImage(file=path)` for raster formats or skip showing.

**Parameters:**
- `path`: Path to the image file
- `max_width`: Maximum width in pixels
- `max_height`: Maximum height in pixels

**Returns:**
- `ImageTk.PhotoImage` scaled to fit, or `None` on failure

**Example:**
```python
from frontend.image_utils import load_image_scaled

# Load and scale image to fit 800x600 display
photo = load_image_scaled("/output/plot.png", max_width=800, max_height=600)
if photo:
    label.config(image=photo)
    label.image = photo  # Keep a reference
```

## Usage Pattern

These utilities are typically used together when displaying plot results:

```python
from frontend.image_utils import (
    plot_display_path,
    preview_path_to_remove_after_display,
    load_image_scaled
)

# Get display path (handles PDF preview)
display_path = plot_display_path(output_path)

# Load and scale image
photo = load_image_scaled(display_path, max_width=800, max_height=600)
if photo:
    label.config(image=photo)
    label.image = photo
    
# Track preview file for cleanup
preview_to_remove = preview_path_to_remove_after_display(display_path, output_path)

# Later, when window closes:
if preview_to_remove and os.path.exists(preview_to_remove):
    os.remove(preview_to_remove)
```

## Dependencies

- **PIL/Pillow**: Required for `load_image_scaled()` to work. Falls back gracefully if not available.
- **Tkinter**: Required for `PhotoImage` objects.

## Notes

- PDF files cannot be displayed directly in Tkinter, so preview PNG files are used when available.
- `load_image_scaled` converts to RGB; use PIL directly for images that must preserve transparency (e.g., logos).
- Image scaling uses LANCZOS resampling for high quality.
- Functions handle missing files and import errors gracefully.

---

*For more information about frontend utilities, see [ui_dialogs](ui_dialogs.md) and [ui_main_menu](ui_main_menu.md).*
