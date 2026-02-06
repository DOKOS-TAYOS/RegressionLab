"""
Frontend module.
Contains all UI-related functionality including dialogs, main menu, and utilities.
"""

from .ui_main_menu import start_main_menu, create_main_menu, show_exit_confirmation
from .ui_dialogs import (
    ask_file_type,
    ask_file_name,
    ask_variables,
    show_data_dialog,
    ask_equation_type,
    ask_num_parameters,
    ask_parameter_names,
    ask_custom_formula,
    ask_num_fits,
    create_result_window,
    show_help_dialog,
    remove_markdown_bold,
    show_config_dialog,
)
from .image_utils import (
    plot_display_path,
    preview_path_to_remove_after_display,
    load_image_scaled,
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
    'show_help_dialog',
    'remove_markdown_bold',
    'show_config_dialog',
    # Image utilities
    'plot_display_path',
    'preview_path_to_remove_after_display',
    'load_image_scaled',
]
