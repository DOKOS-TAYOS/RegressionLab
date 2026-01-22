#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Frontend module.
Contains all UI-related functionality including dialogs, main menu, and utilities.
"""

from frontend.ui_main_menu import start_main_menu, create_main_menu, show_exit_confirmation
from frontend.ui_dialogs import (
    ask_file_type,
    ask_file_name,
    ask_variables,
    show_data_dialog,
    ask_equation_type,
    ask_num_parameters,
    ask_parameter_names,
    ask_custom_formula,
    ask_num_fits,
    create_result_window
)

__all__ = [
    # Main menu
    'start_main_menu',
    'create_main_menu',
    'show_exit_confirmation',
    # Dialogs
    'ask_file_type',
    'ask_file_name',
    'ask_variables',
    'show_data_dialog',
    'ask_equation_type',
    'ask_num_parameters',
    'ask_parameter_names',
    'ask_custom_formula',
    'ask_num_fits',
    'create_result_window',
]
