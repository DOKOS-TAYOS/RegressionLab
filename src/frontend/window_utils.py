"""Utilities for Tkinter window positioning."""

from typing import Optional

from tkinter import Toplevel


def place_window_centered(
    win: Toplevel,
    width: Optional[int] = None,
    height: Optional[int] = None,
    *,
    preserve_size: bool = False,
    max_width: int = 900,
    max_height: int = 650,
    max_width_ratio: float = 0.7,
    max_height_ratio: float = 0.7,
) -> None:
    """
    Position a Toplevel window centered on screen.

    Args:
        win: The Toplevel window to position.
        width: Desired width in pixels. If None and not preserve_size, uses computed size.
        height: Desired height in pixels. If None and not preserve_size, uses computed size.
        preserve_size: If True, keeps the window's current size and only sets position.
            Call after widgets are packed/gridded and after win.update_idletasks().
        max_width: Cap for width when computed from screen (default 900).
        max_height: Cap for height when computed from screen (default 650).
        max_width_ratio: Max width as fraction of screen when width is None.
        max_height_ratio: Max height as fraction of screen when height is None.
    """
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    if preserve_size:
        w = max(1, win.winfo_reqwidth())
        h = max(1, win.winfo_reqheight())
        offset_x = max(0, (screen_width - w) // 2)
        offset_y = max(0, (screen_height - h) // 2)
        win.geometry(f"+{offset_x}+{offset_y}")
        return
    if width is None:
        width = min(max_width, int(screen_width * max_width_ratio))
    else:
        width = min(width, int(screen_width * max_width_ratio))
    if height is None:
        height = min(max_height, int(screen_height * max_height_ratio))
    else:
        height = min(height, int(screen_height * max_height_ratio))
    offset_x = max(0, (screen_width - width) // 2)
    offset_y = max(0, (screen_height - height) // 2)
    win.geometry(f"{width}x{height}+{offset_x}+{offset_y}")
