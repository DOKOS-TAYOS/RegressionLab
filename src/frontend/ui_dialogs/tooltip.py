"""Tooltip binding for Tkinter widgets."""

from typing import Any, Optional
from tkinter import Toplevel, ttk

from config import UI_STYLE


def bind_tooltip(widget: Any, text: str, delay_ms: int = 500) -> None:
    """
    Bind a tooltip to a Tkinter widget.

    Shows a tooltip window after a delay when the mouse enters the widget,
    and hides it when the mouse leaves. Uses a contrasting background and
    border so the tooltip is visible over the UI.

    Args:
        widget: Tkinter widget to bind the tooltip to.
        text: Tooltip text to display when mouse hovers over the widget.
        delay_ms: Delay in milliseconds before showing the tooltip (default: ``500``).
    """
    tooltip_window: Optional[Toplevel] = None
    after_id: Optional[str] = None

    def show_tooltip() -> None:
        nonlocal tooltip_window
        if tooltip_window is not None:
            return
        tooltip_window = Toplevel(widget)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.wm_geometry("+0+0")
        tooltip_window.configure(background=UI_STYLE['tooltip_border'])
        label = ttk.Label(
            tooltip_window,
            text=text,
            style='Tooltip.TLabel',
        )
        label.pack(padx=1, pady=1)
        widget.update_idletasks()
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip() -> None:
        nonlocal tooltip_window, after_id
        if after_id is not None:
            widget.after_cancel(after_id)
            after_id = None
        if tooltip_window is not None:
            tooltip_window.destroy()
            tooltip_window = None

    def on_enter(_event: Any) -> None:
        nonlocal after_id
        after_id = widget.after(delay_ms, show_tooltip)

    def on_leave(_event: Any) -> None:
        hide_tooltip()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
