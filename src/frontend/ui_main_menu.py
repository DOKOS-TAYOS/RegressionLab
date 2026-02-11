"""
Main menu module.
Contains the main application window and exit confirmation dialog.
"""

# Standard library
import os
import sys
from tkinter import Tk, Toplevel, TOP, LEFT, RIGHT
from tkinter import ttk
from typing import Callable

# Third-party packages
from PIL import Image, ImageTk

# Local imports
from config import (
    UI_STYLE,
    __version__,
    configure_ttk_styles,
)
from frontend.keyboard_nav import setup_arrow_enter_navigation
from frontend.ui_dialogs.tooltip import bind_tooltip
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
    menu.resizable(width=False, height=False)
    configure_ttk_styles(menu)
    # Closing with X: same as Exit button (show confirmation, then close app)
    menu.protocol("WM_DELETE_WINDOW", lambda: show_exit_confirmation(menu))

    # Main frame: ttk with Raised.TFrame (lighter border) and inner content frame
    outer_frame = ttk.Frame(menu, style='Raised.TFrame')
    main_frame = ttk.Frame(outer_frame, padding=UI_STYLE['border_width'])

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
            logo_label = ttk.Label(main_frame, image=logo_photo)
            # Keep a reference to prevent garbage collection
            logo_label.image = logo_photo
    except Exception as e:
        # If logo fails to load, continue without it
        print(f"Warning: Could not load logo: {e}")
    
    # Welcome message
    message = ttk.Label(main_frame, text=t('menu.welcome'), style='LargeBold.TLabel')
    version_label = ttk.Label(main_frame, text=f"v{__version__}")

    # Primary actions: main fitting and data options (green)
    normal_fitting_button = ttk.Button(
        main_frame,
        text=t('menu.normal_fitting'),
        command=normal_fitting_callback,
        style='Primary.TButton',
        width=UI_STYLE['button_width_wide'],
    )
    multiple_datasets_button = ttk.Button(
        main_frame,
        text=t('menu.multiple_datasets'),
        command=single_fit_multiple_datasets_callback,
        style='Primary.TButton',
        width=UI_STYLE['button_width_wide'],
    )
    multiple_fits_button = ttk.Button(
        main_frame,
        text=t('menu.checker_fitting'),
        command=multiple_fits_single_dataset_callback,
        style='Primary.TButton',
        width=UI_STYLE['button_width_wide'],
    )
    all_fits_button = ttk.Button(
        main_frame,
        text=t('menu.total_fitting'),
        command=all_fits_single_dataset_callback,
        style='Primary.TButton',
        width=UI_STYLE['button_width_wide'],
    )
    view_data_button = ttk.Button(
        main_frame,
        text=t('menu.view_data'),
        command=watch_data_callback,
        style='Primary.TButton',
        width=UI_STYLE['button_width_wide'],
    )
    help_button = ttk.Button(
        main_frame,
        text=t('menu.information'),
        command=help_callback,
        style='Primary.TButton',
        width=UI_STYLE['button_width_wide'],
    )

    # Secondary: config (neutral)
    config_button = ttk.Button(
        main_frame,
        text=t('menu.config'),
        command=lambda: _handle_config(menu),
        style='Secondary.TButton',
        width=UI_STYLE['button_width'],
    )

    # Danger: exit (red)
    exit_button = ttk.Button(
        main_frame,
        text=t('menu.exit'),
        command=lambda: show_exit_confirmation(menu),
        style='Danger.TButton',
        width=UI_STYLE['button_width'],
    )

    # Tooltips for menu buttons
    bind_tooltip(normal_fitting_button, t('menu.tooltip_normal_fitting'))
    bind_tooltip(multiple_datasets_button, t('menu.tooltip_multiple_datasets'))
    bind_tooltip(multiple_fits_button, t('menu.tooltip_checker_fitting'))
    bind_tooltip(all_fits_button, t('menu.tooltip_total_fitting'))
    bind_tooltip(view_data_button, t('menu.tooltip_view_data'))
    bind_tooltip(help_button, t('menu.tooltip_information'))
    bind_tooltip(config_button, t('menu.tooltip_config'))
    bind_tooltip(exit_button, t('menu.tooltip_exit'))
    
    # Layout
    outer_frame.grid(column=0, row=0)
    main_frame.pack(fill='both', expand=True)
    
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

    setup_arrow_enter_navigation([
        [normal_fitting_button, multiple_datasets_button],
        [multiple_fits_button, all_fits_button],
        [help_button, view_data_button],
        [config_button, exit_button],
    ])
    normal_fitting_button.focus_set()

    return menu


def _handle_config(menu: Tk) -> None:
    """
    Open configuration dialog and restart application if user saves.

    Displays the configuration dialog. If the user accepts and saves changes,
    the application is restarted to apply the new configuration.

    Args:
        menu: The main menu Tkinter window (``Tk`` instance).
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
    message = ttk.Label(exit_level, text=t('menu.exit_confirm'), style='Large.TLabel')

    # Buttons: confirm exit = danger, cancel = accent
    close_button = ttk.Button(
        exit_level,
        text=t('menu.yes'),
        command=lambda: _close_application(parent_menu),
        style='Danger.TButton',
        width=UI_STYLE['button_width'],
    )
    abort_button = ttk.Button(
        exit_level,
        text=t('menu.no'),
        command=exit_level.destroy,
        style='Accent.TButton',
        width=UI_STYLE['button_width'],
    )
    
    # Layout
    message.pack(side=TOP, padx=5, pady=UI_STYLE['padding'])
    close_button.pack(side=LEFT, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    abort_button.pack(side=RIGHT, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    setup_arrow_enter_navigation([[close_button, abort_button]])
    close_button.focus_set()
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
