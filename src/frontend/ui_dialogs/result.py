#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Result window for displaying fitting results and plot."""

from tkinter import Toplevel, Frame, Label, Button, Text, PhotoImage

from config import UI_THEME
from i18n import t


def create_result_window(
    fit_name: str, text: str, equation_str: str, output_path: str
) -> Toplevel:
    """
    Create a Tkinter window to display the fitting results.

    Args:
        fit_name: Name of the fit for window title
        text: Formatted text with parameters and uncertainties
        equation_str: Formatted equation string
        output_path: Path to the plot image file

    Returns:
        The created Toplevel window
    """
    plot_level = Toplevel()
    plot_level.title(fit_name)
    plot_level.configure(background=UI_THEME['background'])

    plot_level.imagen = PhotoImage(file=output_path)

    equation_width = len(equation_str) + 2
    plot_level.equation_text = Text(
        plot_level,
        relief=UI_THEME['relief'],
        borderwidth=UI_THEME['border_width'],
        bg=UI_THEME['background'],
        fg=UI_THEME['foreground'],
        font=(UI_THEME['font_family'], UI_THEME['font_size_large'], 'bold'),
        height=1,
        width=equation_width,
        wrap='none',
        cursor='arrow'
    )
    plot_level.equation_text.insert('1.0', equation_str)
    plot_level.equation_text.config(state='disabled')

    text_lines = text.split('\n')
    num_lines = len(text_lines)
    max_line_length = max(len(line) for line in text_lines) if text_lines else 0
    param_width = max_line_length + 2
    plot_level.middle_frame = Frame(plot_level, bg=UI_THEME['background'])
    plot_level.label_parameters = Text(
        plot_level.middle_frame,
        relief=UI_THEME['relief'],
        borderwidth=UI_THEME['border_width'],
        bg=UI_THEME['background'],
        fg=UI_THEME['foreground'],
        font=(UI_THEME['font_family'], UI_THEME['font_size']),
        height=num_lines,
        width=param_width,
        wrap='none',
        cursor='arrow'
    )
    plot_level.label_parameters.insert('1.0', text)
    plot_level.label_parameters.config(state='disabled')

    plot_level.image = Label(
        plot_level.middle_frame,
        image=plot_level.imagen,
        relief=UI_THEME['relief'],
        borderwidth=UI_THEME['border_width'],
        bg=UI_THEME['background'],
        fg=UI_THEME['foreground']
    )

    plot_level.accept_button = Button(
        plot_level,
        text=t('dialog.accept'),
        command=plot_level.destroy,
        width=UI_THEME['button_width'],
        bg=UI_THEME['background'],
        fg=UI_THEME['button_fg'],
        activebackground=UI_THEME['active_bg'],
        activeforeground=UI_THEME['active_fg'],
        font=(UI_THEME['font_family'], UI_THEME['font_size'])
    )

    plot_level.equation_text.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    plot_level.middle_frame.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    _px, _py = UI_THEME['padding_x'], UI_THEME['padding_y']
    plot_level.label_parameters.pack(
        in_=plot_level.middle_frame, side='left', padx=_px, pady=_py
    )
    plot_level.image.pack(
        in_=plot_level.middle_frame, side='left', padx=_px, pady=_py
    )
    plot_level.accept_button.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    plot_level.accept_button.focus_set()

    return plot_level
