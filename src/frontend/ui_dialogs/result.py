"""Result window for displaying fitting results and plot."""

from pathlib import Path
from tkinter import Frame, Toplevel, Text, PhotoImage, ttk

from config import UI_STYLE
from frontend.image_utils import (
    load_image_scaled,
    plot_display_path,
    preview_path_to_remove_after_display,
)
from i18n import t

# Max size for result plot image so it fits in the window
_RESULT_PLOT_MAX_WIDTH = 920
_RESULT_PLOT_MAX_HEIGHT = 720
# Thin raised border for result frames
_RESULT_FRAME_BORDER = 1
_RESULT_FRAME_RELIEF = 'raised'


def create_result_window(
    fit_name: str, text: str, equation_str: str, output_path: str
) -> Toplevel:
    """
    Create a Tkinter window to display the fitting results.

    Creates a new ``Toplevel`` window showing the fitting results including
    parameter values, uncertainties, statistics, and the fitted equation plot.

    Args:
        fit_name: Name of the fit for window title.
        text: Formatted text with parameters, uncertainties, and statistics.
        equation_str: Formatted equation string with parameter values.
        output_path: Path to the plot image file to display.

    Returns:
        The created ``Toplevel`` window instance.
    """
    plot_level = Toplevel()
    plot_level.title(fit_name)
    plot_level.configure(background=UI_STYLE['bg'])

    display_path = plot_display_path(output_path)
    preview_to_remove = preview_path_to_remove_after_display(display_path, output_path)

    def _on_close() -> None:
        if preview_to_remove:
            try:
                Path(preview_to_remove).unlink(missing_ok=True)
            except OSError:
                pass
        plot_level.destroy()

    plot_level.imagen = load_image_scaled(
        display_path, _RESULT_PLOT_MAX_WIDTH, _RESULT_PLOT_MAX_HEIGHT
    )
    if plot_level.imagen is None and Path(display_path).exists():
        try:
            plot_level.imagen = PhotoImage(file=display_path)
        except Exception:
            plot_level.imagen = None

    equation_lines = equation_str.split('\n')
    equation_height = max(1, len(equation_lines))
    equation_width = max(len(line) for line in equation_lines) + 2 if equation_lines else 2
    plot_level.equation_text = Text(
        plot_level,
        relief=_RESULT_FRAME_RELIEF,
        borderwidth=_RESULT_FRAME_BORDER,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold'),
        height=equation_height,
        width=equation_width,
        wrap='none',
        cursor='arrow',
    )
    plot_level.equation_text.insert('1.0', equation_str)
    plot_level.equation_text.config(state='disabled')

    text_lines = text.split('\n')
    num_lines = len(text_lines)
    max_line_length = max(len(line) for line in text_lines) if text_lines else 0
    param_width = max_line_length + 2
    plot_level.middle_frame = Frame(
        plot_level,
        relief=_RESULT_FRAME_RELIEF,
        borderwidth=_RESULT_FRAME_BORDER,
        bg=UI_STYLE['bg'],
    )
    plot_level.label_parameters = Text(
        plot_level.middle_frame,
        relief=_RESULT_FRAME_RELIEF,
        borderwidth=_RESULT_FRAME_BORDER,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
        height=num_lines,
        width=param_width,
        wrap='none',
        cursor='arrow',
    )
    plot_level.label_parameters.insert('1.0', text)
    plot_level.label_parameters.config(state='disabled')

    if plot_level.imagen is not None:
        plot_level.image = ttk.Label(
            plot_level.middle_frame,
            image=plot_level.imagen,
        )
        plot_level.image.image = plot_level.imagen  # keep reference
    else:
        plot_level.image = ttk.Label(
            plot_level.middle_frame,
            text=t('dialog.plot_preview_unavailable'),
        )

    plot_level.accept_button = ttk.Button(
        plot_level,
        text=t('dialog.accept'),
        command=_on_close,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )

    _pad = UI_STYLE['padding']
    plot_level.equation_text.pack(padx=_pad, pady=_pad)
    plot_level.middle_frame.pack(padx=_pad, pady=_pad)
    plot_level.label_parameters.pack(
        in_=plot_level.middle_frame, side='left', padx=_pad, pady=_pad
    )
    plot_level.image.pack(
        in_=plot_level.middle_frame, side='left', padx=_pad, pady=_pad
    )
    plot_level.accept_button.pack(padx=_pad, pady=_pad)

    for w in (plot_level.equation_text, plot_level.label_parameters, plot_level.accept_button):
        w.bind("<Return>", lambda e: _on_close())
        w.bind("<KP_Enter>", lambda e: _on_close())
    plot_level.bind("<Return>", lambda e: _on_close())
    plot_level.bind("<KP_Enter>", lambda e: _on_close())

    plot_level.accept_button.focus_set()
    plot_level.protocol("WM_DELETE_WINDOW", _on_close)
    plot_level.resizable(False, False)

    return plot_level
