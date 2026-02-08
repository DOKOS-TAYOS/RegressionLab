"""Tooltip binding for Tkinter widgets."""

from typing import Any, Optional
from tkinter import Toplevel, Label

from config import UI_STYLE

# Colores del tooltip: distintos del fondo y de los botones, con borde visible
TOOLTIP_BG = "#fffacd"   # lemon chiffon
TOOLTIP_FG = "black"
TOOLTIP_BORDER = "gray40"


def bind_tooltip(widget: Any, text: str, delay_ms: int = 500) -> None:
    """
    Bind a tooltip to a widget: show after delay on Enter, hide on Leave.
    Uses a contrasting background and border so the tooltip is visible over the UI.
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
        tooltip_window.configure(background=TOOLTIP_BORDER)
        label = Label(
            tooltip_window,
            text=text,
            justify="left",
            bg=TOOLTIP_BG,
            fg=TOOLTIP_FG,
            relief="solid",
            borderwidth=1,
            highlightbackground=TOOLTIP_BORDER,
            highlightthickness=1,
            font=(UI_STYLE['font_family'], max(8, UI_STYLE['font_size'] - 2)),
            padx=6,
            pady=4,
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
