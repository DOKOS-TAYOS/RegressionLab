#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI Dialogs package.
Contains all Tkinter dialog windows for user interaction, split by concern.
"""

from .data_selection import (
    ask_file_type,
    ask_file_name,
    ask_variables,
    show_data_dialog,
)
from .equation import (
    ask_equation_type,
    ask_num_parameters,
    ask_parameter_names,
    ask_custom_formula,
    ask_num_fits,
)
from .help import show_help_dialog, remove_markdown_bold
from .config_dialog import show_config_dialog
from .result import create_result_window

__all__ = [
    'ask_file_type',
    'ask_file_name',
    'ask_variables',
    'show_data_dialog',
    'ask_equation_type',
    'ask_num_parameters',
    'ask_parameter_names',
    'ask_custom_formula',
    'ask_num_fits',
    'show_help_dialog',
    'remove_markdown_bold',
    'show_config_dialog',
    'create_result_window',
]
