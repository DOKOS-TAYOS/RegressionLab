"""Result window for displaying fitting results and plot."""

from pathlib import Path
from tkinter import Frame, Toplevel, Text, PhotoImage, ttk, Entry, StringVar
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt

from config import PLOT_CONFIG, UI_STYLE
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


def _predict_with_uncertainty(
    fit_func: Any,
    params: List[float],
    cov: np.ndarray,
    x_values: List[float],
    num_indep: int,
) -> Tuple[float, Optional[float]]:
    """
    Evaluate fitted function at x_values and propagate parameter uncertainty.

    Args:
        fit_func: The model function (x, *params) -> y
        params: Fitted parameter values
        cov: Covariance matrix from fit
        x_values: Values for each independent variable
        num_indep: Number of independent variables

    Returns:
        Tuple (y_pred, sigma_y). sigma_y is None if covariance invalid.
    """
    x_arr = np.array(x_values, dtype=float)
    if num_indep == 1:
        x_point = x_arr.reshape(-1)
    else:
        x_point = x_arr.reshape(1, -1)

    try:
        y_pred = fit_func(x_point, *params)
        y_pred = float(np.squeeze(y_pred))
    except Exception:
        return float('nan'), None

    params_arr = np.array(params, dtype=float)
    cov_arr = np.asarray(cov)
    if cov_arr.size == 0 or not np.all(np.isfinite(cov_arr)):
        return y_pred, None

    eps = np.sqrt(np.finfo(float).eps) * np.maximum(np.abs(params_arr), 1.0)
    J = np.zeros(len(params))
    for i in range(len(params)):
        p_plus = list(params)
        p_minus = list(params)
        p_plus[i] = params[i] + eps[i]
        p_minus[i] = params[i] - eps[i]
        try:
            y_plus = float(np.squeeze(fit_func(x_point, *p_plus)))
            y_minus = float(np.squeeze(fit_func(x_point, *p_minus)))
            J[i] = (y_plus - y_minus) / (2.0 * eps[i])
        except Exception:
            return y_pred, None

    var_y = J @ cov_arr @ J
    sigma_y = float(np.sqrt(np.maximum(var_y, 0.0)))
    return y_pred, sigma_y


def _show_prediction_dialog(parent: Toplevel, fit_info: Dict[str, Any]) -> None:
    """Open a prediction dialog for evaluating the fitted function at user-specified x values."""
    fit_func = fit_info['fit_func']
    params = fit_info['params']
    cov = fit_info['cov']
    x_names = fit_info['x_names']
    num_indep = len(x_names)

    pred_win = Toplevel(parent)
    pred_win.title(t('dialog.prediction_title'))
    pred_win.configure(background=UI_STYLE['bg'])
    pred_win.transient(parent)
    pred_win.grab_set()

    _pad = UI_STYLE['padding']
    entry_vars: List[StringVar] = []
    entries: List[Entry] = []

    for i, name in enumerate(x_names):
        lbl = ttk.Label(pred_win, text=f"{name}:")
        lbl.grid(row=i, column=0, padx=_pad, pady=_pad, sticky='e')
        var = StringVar(value='0')
        entry_vars.append(var)
        ent = ttk.Entry(pred_win, textvariable=var, width=15)
        ent.grid(row=i, column=1, padx=_pad, pady=_pad, sticky='w')
        entries.append(ent)

    result_var = StringVar(value=t('dialog.prediction_result_placeholder'))

    def _update_result(*_args: Any) -> None:
        try:
            x_vals = []
            for var in entry_vars:
                val = var.get().strip()
                if not val:
                    result_var.set(t('dialog.prediction_result_placeholder'))
                    return
                x_vals.append(float(val))
        except ValueError:
            result_var.set(t('dialog.prediction_invalid_input'))
            return

        y_pred, sigma_y = _predict_with_uncertainty(
            fit_func, params, cov, x_vals, num_indep
        )
        if np.isnan(y_pred):
            result_var.set(t('dialog.prediction_invalid_input'))
            return
        if sigma_y is not None and np.isfinite(sigma_y):
            result_var.set(t('dialog.prediction_result_with_uncertainty', y=f"{y_pred:.6g}", uy=f"{sigma_y:.4g}"))
        else:
            result_var.set(t('dialog.prediction_result', y=f"{y_pred:.6g}"))

    for var in entry_vars:
        var.trace_add('write', _update_result)

    result_label = ttk.Label(pred_win, textvariable=result_var, font=(UI_STYLE['font_family'], UI_STYLE['font_size'], 'bold'))
    result_label.grid(row=num_indep, column=0, columnspan=2, padx=_pad, pady=_pad * 2)

    ttk.Button(pred_win, text=t('dialog.accept'), command=pred_win.destroy).grid(
        row=num_indep + 1, column=0, columnspan=2, padx=_pad, pady=_pad
    )

    if entries:
        entries[0].focus_set()
    _update_result()


def create_result_window(
    fit_name: str,
    text: str,
    equation_str: str,
    output_path: str,
    figure_3d: Optional[Any] = None,
    fit_info: Optional[Dict[str, Any]] = None,
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
        figure_3d: Optional matplotlib Figure for 3D plot (embeds interactive canvas, rotatable with mouse).
        fit_info: Optional dict with 'fit_func', 'params', 'cov', 'x_names' for prediction feature.

    Returns:
        The created ``Toplevel`` window instance.
    """
    plot_level = Toplevel()
    plot_level.title(fit_name)
    plot_level.configure(background=UI_STYLE['bg'])

    display_path = plot_display_path(output_path)
    preview_to_remove = preview_path_to_remove_after_display(display_path, output_path)

    def _on_close() -> None:
        if hasattr(plot_level, 'matplotlib_canvas') and plot_level.matplotlib_canvas is not None:
            try:
                fig = plot_level.matplotlib_canvas.figure
                fig.savefig(output_path, bbox_inches='tight', dpi=PLOT_CONFIG['dpi'])
                if Path(output_path).suffix.lower() == '.pdf':
                    preview_path = Path(output_path).parent / (Path(output_path).stem + '_preview.png')
                    fig.savefig(
                        str(preview_path),
                        bbox_inches='tight',
                        dpi=PLOT_CONFIG['dpi'],
                        format='png',
                    )
                plot_level.matplotlib_canvas.get_tk_widget().destroy()
                plt.close(fig)
            except Exception:
                pass
        elif preview_to_remove:
            try:
                Path(preview_to_remove).unlink(missing_ok=True)
            except OSError:
                pass
        plot_level.destroy()

    _pad = UI_STYLE['padding']

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

    plot_level.imagen = None
    plot_level.matplotlib_canvas = None
    if figure_3d is not None:
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            plot_level.matplotlib_canvas = FigureCanvasTkAgg(
                figure_3d, master=plot_level.middle_frame
            )
            plot_level.matplotlib_canvas.draw()
            
        except Exception:
            plot_level.matplotlib_canvas = None
    if plot_level.matplotlib_canvas is None:
        plot_level.imagen = load_image_scaled(
            display_path, _RESULT_PLOT_MAX_WIDTH, _RESULT_PLOT_MAX_HEIGHT
        )
        if plot_level.imagen is None and Path(display_path).exists():
            try:
                plot_level.imagen = PhotoImage(file=display_path)
            except Exception:
                plot_level.imagen = None

    if plot_level.matplotlib_canvas is not None:
        plot_level.image = plot_level.matplotlib_canvas.get_tk_widget()
    elif plot_level.imagen is not None:
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

    button_frame = Frame(plot_level, bg=UI_STYLE['bg'])
    plot_level.accept_button = ttk.Button(
        button_frame,
        text=t('dialog.accept'),
        command=_on_close,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )
    plot_level.accept_button.pack(side='left', padx=_pad, pady=_pad)
    focusables = [plot_level.equation_text, plot_level.label_parameters, plot_level.accept_button]
    if fit_info is not None:
        plot_level.prediction_button = ttk.Button(
            button_frame,
            text=t('dialog.prediction'),
            command=lambda: _show_prediction_dialog(plot_level, fit_info),
            width=UI_STYLE['button_width'],
        )
        plot_level.prediction_button.pack(side='left', padx=_pad, pady=_pad)
        focusables.append(plot_level.prediction_button)

    plot_level.equation_text.pack(padx=_pad, pady=_pad)
    plot_level.middle_frame.pack(padx=_pad, pady=_pad)
    plot_level.label_parameters.pack(
        in_=plot_level.middle_frame, side='left', padx=_pad, pady=_pad
    )
    plot_level.image.pack(
        in_=plot_level.middle_frame, side='left', padx=_pad, pady=_pad
    )
    button_frame.pack(padx=_pad, pady=_pad)

    for w in focusables:
        w.bind("<Return>", lambda e: _on_close())
        w.bind("<KP_Enter>", lambda e: _on_close())
    plot_level.bind("<Return>", lambda e: _on_close())
    plot_level.bind("<KP_Enter>", lambda e: _on_close())

    plot_level.accept_button.focus_set()
    plot_level.protocol("WM_DELETE_WINDOW", _on_close)
    plot_level.resizable(plot_level.matplotlib_canvas is not None, plot_level.matplotlib_canvas is not None)
    if plot_level.matplotlib_canvas is not None:
        plot_level._figure_3d = figure_3d  # keep reference to avoid garbage collection

    return plot_level
