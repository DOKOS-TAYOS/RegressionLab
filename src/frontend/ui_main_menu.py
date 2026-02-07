"""
Main menu module.
Contains the main application window and exit confirmation dialog.
"""

# Standard library
import os
import sys
from tkinter import Tk, Toplevel, Frame, Label, Button, TOP, LEFT, RIGHT
from typing import Callable

# Third-party packages
from PIL import Image, ImageTk

# Local imports
from config import (
    BUTTON_STYLE_ACCENT,
    BUTTON_STYLE_DANGER,
    BUTTON_STYLE_PRIMARY,
    BUTTON_STYLE_SECONDARY,
    UI_STYLE,
    __version__,
)
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
    menu.title(f"{t('menu.title')} — v{__version__}")
    menu.attributes('-fullscreen', False)
    menu.configure(background=UI_STYLE['bg'])
    menu.resizable(width=True, height=True)
    # Closing with X: same as Exit button (show confirmation, then close app)
    menu.protocol("WM_DELETE_WINDOW", lambda: show_exit_confirmation(menu))

    # Create main frame
    main_frame = Frame(
        menu,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )
    
    # Load and display logo
    logo_label = None
    try:
        # Get the project root directory (3 levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        logo_path = os.path.join(project_root, 'images', 'RegressionLab_logo_app.png')
        
        if os.path.exists(logo_path):
            # Load the image and resize it to fit nicely
            logo_image = Image.open(logo_path)
            # Resize to a reasonable width (e.g., 400 pixels) while maintaining aspect ratio
            max_width = 600
            aspect_ratio = logo_image.height / logo_image.width
            new_height = int(max_width * aspect_ratio)
            logo_image = logo_image.resize((max_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Create label for logo
            logo_label = Label(
                main_frame,
                image=logo_photo,
                bg=UI_STYLE['bg']
            )
            # Keep a reference to prevent garbage collection
            logo_label.image = logo_photo
    except Exception as e:
        # If logo fails to load, continue without it
        print(f"Warning: Could not load logo: {e}")
    
    # Welcome message
    message = Label(
        main_frame,
        text=t('menu.welcome'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold')
    )
    version_label = Label(
        main_frame,
        text=f"v{__version__}",
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], max(8, UI_STYLE['font_size'] - 2))
    )
    
    # Primary actions: main fitting and data options (green, bordered)
    btn_primary = {**BUTTON_STYLE_PRIMARY, 'width': UI_STYLE['button_width_wide']}
    normal_fitting_button = Button(
        main_frame,
        text=t('menu.normal_fitting'),
        command=normal_fitting_callback,
        **btn_primary
    )
    multiple_datasets_button = Button(
        main_frame,
        text=t('menu.multiple_datasets'),
        command=single_fit_multiple_datasets_callback,
        **btn_primary
    )
    multiple_fits_button = Button(
        main_frame,
        text=t('menu.checker_fitting'),
        command=multiple_fits_single_dataset_callback,
        **btn_primary
    )
    all_fits_button = Button(
        main_frame,
        text=t('menu.total_fitting'),
        command=all_fits_single_dataset_callback,
        **btn_primary
    )
    view_data_button = Button(
        main_frame,
        text=t('menu.view_data'),
        command=watch_data_callback,
        **btn_primary
    )
    help_button = Button(
        main_frame,
        text=t('menu.information'),
        command=help_callback,
        **btn_primary
    )

    # Secondary: config (neutral, bordered)
    config_button = Button(
        main_frame,
        text=t('menu.config'),
        command=lambda: _handle_config(menu),
        width=UI_STYLE['button_width'],
        **BUTTON_STYLE_SECONDARY
    )

    # Danger: exit (red, bordered)
    exit_button = Button(
        main_frame,
        text=t('menu.exit'),
        command=lambda: show_exit_confirmation(menu),
        width=UI_STYLE['button_width'],
        **BUTTON_STYLE_DANGER
    )
    
    # Layout
    main_frame.grid(column=0, row=0)
    
    # Place logo if it was loaded successfully
    _pad = UI_STYLE['padding']
    current_row = 0
    if logo_label:
        logo_label.grid(column=0, row=current_row, columnspan=2, padx=_pad, pady=6)
        current_row += 1
    message.grid(column=0, row=current_row, columnspan=2, padx=_pad, pady=6)
    current_row += 1
    version_label.grid(column=0, row=current_row, columnspan=2, padx=_pad, pady=(0, 6))
    current_row += 1
    normal_fitting_button.grid(column=0, row=current_row, padx=_pad, pady=_pad)
    multiple_datasets_button.grid(column=1, row=current_row, padx=_pad, pady=_pad)
    current_row += 1
    multiple_fits_button.grid(column=0, row=current_row, padx=_pad, pady=_pad)
    all_fits_button.grid(column=1, row=current_row, padx=_pad, pady=_pad)
    current_row += 1
    help_button.grid(column=0, row=current_row, padx=_pad, pady=_pad)
    view_data_button.grid(column=1, row=current_row, padx=_pad, pady=_pad)
    current_row += 1
    config_button.grid(column=0, row=current_row, padx=_pad, pady=_pad)
    exit_button.grid(column=1, row=current_row, padx=_pad, pady=_pad)
    
    normal_fitting_button.focus_set()
    
    return menu


def _handle_config(menu: Tk) -> None:
    """
    Open configuration dialog. If user saves, restart the application.
    """
    from frontend.ui_dialogs import show_config_dialog
    if show_config_dialog(menu):
        menu.destroy()
        os.execv(sys.executable, [sys.executable] + sys.argv)


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
    
    # Buttons: confirm exit = danger, cancel = accent
    close_button = Button(
        exit_level,
        text=t('menu.yes'),
        command=lambda: _close_application(parent_menu),
        width=UI_STYLE['button_width'],
        **BUTTON_STYLE_DANGER
    )
    abort_button = Button(
        exit_level,
        text=t('menu.no'),
        command=exit_level.destroy,
        width=UI_STYLE['button_width'],
        **BUTTON_STYLE_ACCENT
    )
    
    # Layout
    message.pack(side=TOP, padx=5, pady=UI_STYLE['padding'])
    close_button.pack(side=LEFT, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    abort_button.pack(side=RIGHT, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    close_button.focus_set()
    exit_level.transient(master=parent_menu)
    # Closing with X = cancel exit (same as "No")
    exit_level.protocol("WM_DELETE_WINDOW", exit_level.destroy)
    parent_menu.wait_window(exit_level)


def _close_application(menu: Tk) -> None:
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

    menu.mainloop()
