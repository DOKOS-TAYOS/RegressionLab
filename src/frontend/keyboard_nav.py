"""Keyboard navigation: arrow keys to move focus, Enter to activate."""

from tkinter import Event
from typing import Any, Callable, Optional, Sequence


def bind_enter_to_accept(
    widgets: Sequence[Any],
    accept_callback: Callable[[], None],
) -> None:
    """
    Bind Enter key events to trigger accept callback on widgets.

    Binds both <Return> and <KP_Enter> events on each widget to the
    accept_callback function, so that pressing Enter from input widgets
    (Spinbox, Entry, Combobox, etc.) triggers the accept action.

    Args:
        widgets: Sequence of Tkinter widgets to bind events to.
        accept_callback: Callback function with signature ``() -> None`` to call
            when Enter is pressed.
    """
    def _on_enter(_event: Event) -> str:
        accept_callback()
        return "break"

    for w in widgets:
        w.bind("<Return>", _on_enter)
        w.bind("<KP_Enter>", _on_enter)


def setup_arrow_enter_navigation(
    widgets_grid: Sequence[Sequence[Any]],
    on_enter: Optional[Callable[[Any, Event], bool]] = None,
) -> None:
    """
    Set up keyboard navigation for a grid of widgets.

    Binds arrow keys to move focus between widgets in the grid and
    Return/Enter keys to activate the focused widget. The grid is a 2D
    list of focusable widgets (e.g. ttk.Button); use None for empty cells.

    Args:
        widgets_grid: 2D sequence of widgets arranged in a grid layout.
            Use ``None`` for empty cells in the grid.
        on_enter: Optional callback function called when Enter is pressed.
            Signature: ``on_enter(widget, event) -> bool``.
            If it returns ``True``, the default behavior (invoke button) is skipped.
            Use this to handle Enter on non-button widgets (e.g. radiobutton
            -> confirm dialog).
    """
    grid: dict[tuple[int, int], Any] = {}
    for r, row in enumerate(widgets_grid):
        for c, w in enumerate(row):
            if w is not None:
                grid[(r, c)] = w

    def focus_at(nr: int, nc: int) -> None:
        w = grid.get((nr, nc))
        if w is not None:
            w.focus_set()

    def move(event: Event, dr: int, dc: int) -> str:
        current = event.widget
        for (r, c), w in grid.items():
            if w == current:
                focus_at(r + dr, c + dc)
                return "break"
        return "break"

    def invoke_focused(event: Event) -> str:
        w = event.widget
        if on_enter is not None and on_enter(w, event):
            return "break"
        if hasattr(w, "invoke") and callable(getattr(w, "invoke")):
            w.invoke()
        return "break"

    for (r, c), w in grid.items():
        w.bind("<Return>", invoke_focused)
        w.bind("<KP_Enter>", invoke_focused)
        w.bind("<Left>", lambda e, dr=0, dc=-1: move(e, dr, dc))
        w.bind("<Right>", lambda e, dr=0, dc=1: move(e, dr, dc))
        w.bind("<Up>", lambda e, dr=-1, dc=0: move(e, dr, dc))
        w.bind("<Down>", lambda e, dr=1, dc=0: move(e, dr, dc))
