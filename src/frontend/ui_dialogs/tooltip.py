"""Tooltip binding for Tkinter widgets."""

from typing import Any, Optional
from tkinter import Label, Toplevel

from config import UI_STYLE


def bind_tooltip(widget: Any, text: str, delay_ms: int = 500) -> None:
    """
    Bind a tooltip to a widget: show after delay on Enter, hide on Leave.
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
        label = Label(
            tooltip_window,
            text=text,
            justify="left",
            bg="#ffffcc",
            fg="black",
            relief="solid",
            borderwidth=1,
            font=(UI_STYLE['font_family'], max(8, UI_STYLE['font_size'] - 2)),
            padx=6,
            pady=4,
        )
        label.pack()
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
