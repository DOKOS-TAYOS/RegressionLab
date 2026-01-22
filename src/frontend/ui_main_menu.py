#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main menu module.
Contains the main application window and exit confirmation dialog.
"""

from tkinter import Tk, Toplevel, Frame, Label, Button, TOP, LEFT, RIGHT
from typing import Callable, Optional
import sys
from config import UI_STYLE
from i18n import t


def create_main_menu(
    normal_fitting_callback: Callable,
    single_fit_multiple_datasets_callback: Callable,
    multiple_fits_single_dataset_callback: Callable,
    all_fits_single_dataset_callback: Callable,
    watch_data_callback: Callable,
    help_callback: Callable
) -> Tk:
    """
    Create and display the main application menu window.
    
    Args:
        normal_fitting_callback: Function to call for normal fitting
        single_fit_multiple_datasets_callback: Function to call for single fit on multiple datasets
        multiple_fits_single_dataset_callback: Function to call for multiple fits on single dataset
        all_fits_single_dataset_callback: Function to call for all fits on single dataset
        watch_data_callback: Function to call for viewing data
        help_callback: Function to display help information
        
    Returns:
        The main Tk window instance
    """
    menu = Tk()
    menu.title(t('menu.title'))
    menu.attributes('-fullscreen', False)
    menu.configure(background=UI_STYLE['bg'])
    menu.resizable(width=True, height=True)
    
    # Create main frame
    main_frame = Frame(
        menu,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )
    
    # Welcome message
    message = Label(
        main_frame,
        text=t('menu.welcome'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold')
    )
    
    # Button configuration
    btn_config = {
        'width': UI_STYLE['button_width_wide'],
        'bg': UI_STYLE['bg'],
        'fg': UI_STYLE['fg'],
        'activebackground': UI_STYLE['active_bg'],
        'activeforeground': UI_STYLE['active_fg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size'])
    }
    
    # Create buttons
    normal_fitting_button = Button(
        main_frame,
        text=t('menu.normal_fitting'),
        command=normal_fitting_callback,
        **btn_config
    )
    
    multiple_datasets_button = Button(
        main_frame,
        text=t('menu.multiple_datasets'),
        command=single_fit_multiple_datasets_callback,
        **btn_config
    )
    
    help_button = Button(
        main_frame,
        text=t('menu.information'),
        command=help_callback,
        **btn_config
    )
    
    multiple_fits_button = Button(
        main_frame,
        text=t('menu.checker_fitting'),
        command=multiple_fits_single_dataset_callback,
        **btn_config
    )
    
    view_data_button = Button(
        main_frame,
        text=t('menu.view_data'),
        command=watch_data_callback,
        **btn_config
    )
    
    all_fits_button = Button(
        main_frame,
        text=t('menu.total_fitting'),
        command=all_fits_single_dataset_callback,
        **btn_config
    )
    
    # Exit button with different styling
    exit_button = Button(
        main_frame,
        text=t('menu.exit'),
        command=lambda: show_exit_confirmation(menu),
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_cancel'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    
    # Layout
    main_frame.grid(column=0, row=0)
    message.grid(column=0, row=0, columnspan=2, padx=UI_STYLE['padding'], pady=6)
    normal_fitting_button.grid(column=0, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    multiple_datasets_button.grid(column=1, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    multiple_fits_button.grid(column=0, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    all_fits_button.grid(column=1, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    help_button.grid(column=0, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    view_data_button.grid(column=1, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    exit_button.grid(column=1, row=4, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    normal_fitting_button.focus_set()
    
    return menu


def show_exit_confirmation(parent_menu: Tk) -> None:
    """
    Display exit confirmation dialog.
    
    Args:
        parent_menu: The parent menu window to close if user confirms exit
    """
    exit_level = Toplevel()
    exit_level.title(t('menu.exit_title'))
    exit_level.resizable(width=False, height=False)
    exit_level.configure(background=UI_STYLE['bg'])
    
    # Message
    message = Label(
        exit_level,
        text=t('menu.exit_confirm'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'])
    )
    
    # Buttons
    close_button = Button(
        exit_level,
        text=t('menu.yes'),
        command=lambda: close_application(parent_menu),
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_cancel'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    
    abort_button = Button(
        exit_level,
        text=t('menu.no'),
        command=exit_level.destroy,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_cyan'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    
    # Layout
    message.pack(side=TOP, padx=5, pady=UI_STYLE['padding'])
    close_button.pack(side=LEFT, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    abort_button.pack(side=RIGHT, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    close_button.focus_set()
    exit_level.transient(master=parent_menu)
    parent_menu.wait_window(exit_level)


def close_application(menu: Tk) -> None:
    """
    Close the application and exit.
    
    Args:
        menu: The main menu window to destroy
    """
    menu.destroy()
    sys.exit()


def start_main_menu(
    normal_fitting_callback: Callable,
    single_fit_multiple_datasets_callback: Callable,
    multiple_fits_single_dataset_callback: Callable,
    all_fits_single_dataset_callback: Callable,
    watch_data_callback: Callable,
    help_callback: Callable
) -> None:
    """
    Create and run the main application menu.
    
    This is the entry point for the GUI application.
    
    Args:
        normal_fitting_callback: Function to call for normal fitting
        single_fit_multiple_datasets_callback: Function to call for single fit on multiple datasets
        multiple_fits_single_dataset_callback: Function to call for multiple fits on single dataset
        all_fits_single_dataset_callback: Function to call for all fits on single dataset
        watch_data_callback: Function to call for viewing data
        help_callback: Function to display help information
    """
    menu = create_main_menu(
        normal_fitting_callback=normal_fitting_callback,
        single_fit_multiple_datasets_callback=single_fit_multiple_datasets_callback,
        multiple_fits_single_dataset_callback=multiple_fits_single_dataset_callback,
        all_fits_single_dataset_callback=all_fits_single_dataset_callback,
        watch_data_callback=watch_data_callback,
        help_callback=help_callback
    )
    
    # Store menu globally for callbacks that need it
    import __main__
    __main__.menu = menu
    
    menu.wait_window(menu)
    menu.mainloop()
