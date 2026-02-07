"""Shared image loading and scaling for the Tkinter frontend."""

from pathlib import Path
from typing import Any, Optional


def plot_display_path(output_path: str) -> str:
    """
    Return the path to use for displaying a plot in the GUI.

    When the saved file is PDF, returns the ``_preview.png`` path if it exists,
    so Tkinter can show the image without breaking.

    Args:
        output_path: Full path to the saved plot file (e.g. PDF or PNG).

    Returns:
        Path to the image file to display (preview PNG for PDFs when available).
    """
    p = Path(output_path)
    if p.suffix.lower() == '.pdf':
        preview = p.parent / (p.stem + '_preview.png')
        if preview.exists():
            return str(preview)
    return output_path


def preview_path_to_remove_after_display(
    display_path: str, original_output_path: str
) -> Optional[str]:
    """
    Return the path of an auxiliary preview file to remove after display.

    If the displayed image is an auxiliary preview file (``_preview.png``),
    return its path so the caller can delete it after the window is closed.

    Args:
        display_path: Path actually used for display (may be preview PNG).
        original_output_path: Original output path (e.g. PDF path).

    Returns:
        Path to the preview file to delete, or None if no cleanup needed.
    """
    if display_path == original_output_path:
        return None
    p = Path(display_path)
    if p.name.endswith("_preview.png") and p.exists():
        return display_path
    return None


def load_image_scaled(
    path: str,
    max_width: int,
    max_height: int,
) -> Optional[Any]:
    """
    Load an image from file and return a Tk PhotoImage scaled to fit within max dimensions.

    Uses PIL when available. Supports PNG, JPG, JPEG. Returns None if the file cannot be
    opened (e.g. missing PIL), so callers can fall back to tkinter.PhotoImage(file=path)
    for raster formats or skip showing.

    Args:
        path: Path to the image file.
        max_width: Maximum width in pixels.
        max_height: Maximum height in pixels.

    Returns:
        ImageTk.PhotoImage scaled to fit, or None on failure.
    """
    try:
        from PIL import Image, ImageTk
    except ImportError:
        return None
    try:
        img = Image.open(path).convert('RGB')
    except OSError:
        return None
    w, h = img.size
    if w > max_width or h > max_height:
        ratio = min(max_width / w, max_height / h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)
