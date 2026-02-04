#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI Dialogs module.
Contains all Tkinter dialog windows for user interaction.
"""

# Standard library
import re
import webbrowser
from typing import Any, List, Optional, Tuple, Union
from tkinter import (
    Tk,
    Toplevel,
    Frame,
    Label,
    Spinbox,
    Button,
    Entry,
    StringVar,
    IntVar,
    BooleanVar,
    Text,
    Scrollbar,
    Radiobutton,
    PhotoImage,
    Checkbutton,
    Canvas,
    ttk,
)

# Local imports
from config import (
    DONATIONS_URL,
    ENV_SCHEMA,
    EQUATION_FORMULAS,
    EXIT_SIGNAL,
    UI_STYLE,
    UI_THEME,
    get_current_env_values,
    get_project_root,
    write_env_file,
)
from i18n import t


def _bind_tooltip(widget: Any, text: str, delay_ms: int = 500) -> None:
    """
    Bind a tooltip to a widget: show after delay on Enter, hide on Leave.
    """
    tooltip_window: Optional[Toplevel] = None
    after_id: Optional[str] = None

    def show_tooltip() -> None:
        nonlocal tooltip_window
        if tooltip_window is not None:
            return
        tooltip_window = Toplevel(widget)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.wm_geometry("+0+0")
        label = Label(
            tooltip_window,
            text=text,
            justify="left",
            bg="#ffffcc",
            fg="black",
            relief="solid",
            borderwidth=1,
            font=(UI_STYLE['font_family'], max(8, UI_STYLE['font_size'] - 2)),
            padx=6,
            pady=4,
        )
        label.pack()
        # Position near cursor/widget
        widget.update_idletasks()
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip() -> None:
        nonlocal tooltip_window, after_id
        if after_id is not None:
            widget.after_cancel(after_id)
            after_id = None
        if tooltip_window is not None:
            tooltip_window.destroy()
            tooltip_window = None

    def on_enter(_event: Any) -> None:
        nonlocal after_id
        after_id = widget.after(delay_ms, show_tooltip)

    def on_leave(_event: Any) -> None:
        hide_tooltip()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def ask_file_type(parent_window: Any) -> str:
    """
    Dialog to ask for data file type.
    
    Presents radio buttons with file type options (xlsx, csv, txt, Exit/Salir).
    User can select one option.
    
    Args:
        parent_window: Parent Tkinter window
        
    Returns:
        Selected file type ('csv', 'xlsx', 'txt', EXIT_SIGNAL, or '')
    """
    # Create dialog window
    call_file_level = Toplevel()
    call_file_level.title(t('dialog.data'))
    
    # Main frame with styled border
    call_file_level.frame = Frame(
        call_file_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    
    # StringVar to hold the selected file type
    call_file_level.tipo = StringVar()
    
    # Label prompting user for file type
    call_file_level.label_message = Label(
        call_file_level.frame, 
        text=t('dialog.file_type'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    
    # Build values tuple with translated exit option
    file_type_values = ('xlsx', 'csv', 'txt', t('dialog.exit_option'))
    
    # Set default value
    call_file_level.tipo.set(file_type_values[0])
    call_file_level.cancelled = False

    def _on_close_file_type() -> None:
        call_file_level.cancelled = True
        call_file_level.destroy()

    call_file_level.protocol("WM_DELETE_WINDOW", _on_close_file_type)
    
    # Create a frame to contain the radiobuttons
    call_file_level.radio_frame = Frame(
        call_file_level.frame,
        bg=UI_STYLE['bg']
    )
    
    # Create radiobuttons for each file type option
    call_file_level.radiobuttons = []
    for i, value in enumerate(file_type_values):
        rb = Radiobutton(
            call_file_level.radio_frame,
            text=value,
            variable=call_file_level.tipo,
            value=value,
            bg=UI_STYLE['bg'],
            fg=UI_STYLE['fg'],
            activebackground=UI_STYLE['active_bg'],
            activeforeground=UI_STYLE['active_fg'],
            selectcolor=UI_STYLE['bg'],  # Background color when selected
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        rb.grid(row=i, column=0, sticky='w', padx=UI_STYLE['padding'], pady=2)
        call_file_level.radiobuttons.append(rb)
    
    # Accept button closes the dialog
    call_file_level.accept_button = Button(
        call_file_level.frame, 
        text=t('dialog.accept'), 
        command=call_file_level.destroy,  # Close dialog on click
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    # Grid layout: frame at (0,0)
    call_file_level.frame.grid(column=0, row=0)
    call_file_level.label_message.grid(
        column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'], sticky='w'
    )
    call_file_level.radio_frame.grid(
        column=0, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_file_level.accept_button.grid(
        column=0, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )

    # Set initial focus on the first radiobutton for keyboard navigation
    call_file_level.radiobuttons[0].focus_set()
    
    # Wait for dialog to close before continuing
    parent_window.wait_window(call_file_level)

    if getattr(call_file_level, 'cancelled', False):
        return EXIT_SIGNAL
    # Map translated exit option back to internal EXIT_SIGNAL
    selected_value = call_file_level.tipo.get()
    if selected_value == t('dialog.exit_option'):
        return EXIT_SIGNAL
    return selected_value


def ask_file_name(parent_window: Any, file_list: List[str]) -> str:
    """
    Dialog to select a specific file from the list.
    
    Args:
        parent_window: Parent Tkinter window
        file_list: List of available file names
        
    Returns:
        Selected file name (without extension)
    """
    call_data_level = Toplevel()
    call_data_level.title(t('dialog.data'))
    call_data_level.cancelled = False

    def _on_close_file_name() -> None:
        call_data_level.cancelled = True
        call_data_level.destroy()

    call_data_level.protocol("WM_DELETE_WINDOW", _on_close_file_name)
    call_data_level.frame_custom = Frame(
        call_data_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    call_data_level.arch = StringVar()

    call_data_level.label_message = Label(
        call_data_level.frame_custom, 
        text=t('dialog.file_name'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    call_data_level.name_entry = ttk.Combobox(
        call_data_level.frame_custom, 
        textvariable=call_data_level.arch, 
        values=file_list, 
        state='readonly', 
        width=UI_STYLE['entry_width'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    # Set the first item as default if list is not empty
    if file_list:
        call_data_level.name_entry.current(0)
    
    call_data_level.accept_button = Button(
        call_data_level.frame_custom, 
        text=t('dialog.accept'), 
        command=call_data_level.destroy, 
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    call_data_level.frame_custom.grid(column=0, row=0)
    call_data_level.label_message.grid(
        column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_data_level.name_entry.grid(
        column=1, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_data_level.accept_button.grid(
        column=0, row=1, columnspan=2,
        padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )

    call_data_level.name_entry.focus_set()
    parent_window.wait_window(call_data_level)

    if getattr(call_data_level, 'cancelled', False):
        return ''
    return call_data_level.arch.get()


def ask_variables(parent_window: Any, variable_names: List[str]) -> Tuple[str, str, str]:
    """
    Dialog to select independent (x) and dependent (y) variables and plot name.
    
    Presents a form to select x and y variables from the dataset columns,
    and allows the user to enter a custom plot name. The dialog filters out
    uncertainty columns (those starting with 'u') to avoid confusion.
    
    Args:
        parent_window: Parent Tkinter window
        variable_names: List of available variable names from the dataset
        
    Returns:
        Tuple of (x_name, y_name, plot_name)
    """
    # Create dialog window
    call_var_level = Toplevel()
    call_var_level.title(t('dialog.data'))
    call_var_level.cancelled = False

    def _on_close_variables() -> None:
        call_var_level.cancelled = True
        call_var_level.destroy()

    call_var_level.protocol("WM_DELETE_WINDOW", _on_close_variables)
    
    # Main frame with styled border
    call_var_level.frame_custom = Frame(
        call_var_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    
    # Variables to hold user selections
    call_var_level.x_name = StringVar()
    call_var_level.y_name = StringVar()
    call_var_level.graf_name = StringVar()

    # Header label
    call_var_level.label_message = Label(
        call_var_level.frame_custom, 
        text=t('dialog.variable_names'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold')
    )
    
    # Label for X variable selection
    call_var_level.label_message_x = Label(
        call_var_level.frame_custom, 
        text=t('dialog.independent_variable'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    # Filter variable names to remove uncertainty columns
    # The application expects uncertainty columns to be named 'u<varname>'
    # For example, if 'x' exists with uncertainty 'ux', we only show 'x' in the selection
    filtered_variable_names = []
    excluded_vars = set()
    
    for var in variable_names:
        # Skip if already marked for exclusion
        if var in excluded_vars:
            continue
            
        # If this variable starts with 'u', check if base variable exists
        if var.startswith('u') and len(var) > 1:
            base_var = var[1:]  # Remove 'u' prefix
            if base_var in variable_names:
                # This is an uncertainty column for an existing base variable
                # Exclude it from the selection (user selects the base, uncertainty is automatic)
                excluded_vars.add(var)
                continue
        
        # If adding 'u' prefix would create a conflict, mark that for exclusion
        u_var = f'u{var}'
        if u_var in variable_names:
            # This base variable has a corresponding uncertainty column
            # Mark the uncertainty column for exclusion
            excluded_vars.add(u_var)
        
        # This variable is safe to include
        filtered_variable_names.append(var)
    
    # Use filtered list if it's not empty, otherwise fall back to original
    if filtered_variable_names:
        variable_names = filtered_variable_names


    call_var_level.x_nom = ttk.Combobox(
        call_var_level.frame_custom, 
        textvariable=call_var_level.x_name, 
        values=variable_names, 
        state='readonly', 
        width=UI_STYLE['spinbox_width'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    # Set the first variable as default for X
    if variable_names:
        call_var_level.x_nom.current(0)
    
    call_var_level.label_message_y = Label(
        call_var_level.frame_custom, 
        text=t('dialog.dependent_variable'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    call_var_level.y_nom = ttk.Combobox(
        call_var_level.frame_custom, 
        textvariable=call_var_level.y_name, 
        values=variable_names, 
        state='readonly', 
        width=UI_STYLE['spinbox_width'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    # Set the second variable as default for Y if available
    if len(variable_names) > 1:
        call_var_level.y_nom.current(1)
    elif variable_names:
        call_var_level.y_nom.current(0)
    call_var_level.accept_button = Button(
        call_var_level.frame_custom, 
        text=t('dialog.accept'), 
        command=call_var_level.destroy, 
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    call_var_level.label_message_plot = Label(
        call_var_level.frame_custom, 
        text=t('dialog.plot_name'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    call_var_level.graf_nom = Entry(
        call_var_level.frame_custom, 
        textvariable=call_var_level.graf_name,  
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        width=UI_STYLE['entry_width'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    call_var_level.frame_custom.grid(column=0, row=0)
    call_var_level.label_message_plot.grid(
        column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_var_level.graf_nom.grid(
        column=1, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_var_level.label_message.grid(
        column=0, row=1, columnspan=2, padx=UI_STYLE['padding'], pady=6
    )
    call_var_level.label_message_x.grid(
        column=0, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_var_level.x_nom.grid(
        column=1, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_var_level.label_message_y.grid(
        column=0, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_var_level.y_nom.grid(
        column=1, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    call_var_level.accept_button.grid(
        column=1, row=4, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )

    call_var_level.x_nom.focus_set()
    parent_window.wait_window(call_var_level)

    if getattr(call_var_level, 'cancelled', False):
        return ('', '', '')
    return call_var_level.x_name.get(), call_var_level.y_name.get(), call_var_level.graf_name.get()


# Max size for pair-plot image window so it does not resize the desktop
_PAIR_PLOT_MAX_WIDTH = 920
_PAIR_PLOT_MAX_HEIGHT = 720


def _show_image_toplevel(parent: Tk | Toplevel, image_path: str, title: str) -> None:
    """Open a Toplevel window showing an image from file (e.g. pair plot), scaled to fit max size."""
    try:
        from PIL import Image, ImageTk
    except ImportError:
        return
    try:
        img = Image.open(image_path).convert('RGB')
    except OSError:
        return
    w, h = img.size
    if w > _PAIR_PLOT_MAX_WIDTH or h > _PAIR_PLOT_MAX_HEIGHT:
        ratio = min(_PAIR_PLOT_MAX_WIDTH / w, _PAIR_PLOT_MAX_HEIGHT / h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    win = Toplevel(parent)
    win.title(title)
    win.configure(background=UI_STYLE['bg'])
    win.resizable(False, False)
    photo = ImageTk.PhotoImage(img)
    label = Label(win, image=photo, bg=UI_STYLE['bg'])
    label.image = photo
    label.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    Button(
        win,
        text=t('dialog.accept'),
        command=win.destroy,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
    ).pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])


def show_data_dialog(parent_window: Tk | Toplevel, data: Any) -> None:
    """
    Dialog to display loaded data.

    Args:
        parent_window: Parent Tkinter window.
        data: DataFrame to display (or string). If DataFrame, converted to string for display.
    """
    if hasattr(data, 'to_string'):
        content = data.to_string()
    else:
        content = str(data)

    watch_data_level = Toplevel()
    watch_data_level.title(t('dialog.show_data_title'))
    watch_data_level.configure(background=UI_STYLE['bg'])
    watch_data_level.minsize(800, 600)

    text_frame = Frame(watch_data_level, bg=UI_STYLE['bg'])
    text_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)

    scrollbar_y = Scrollbar(text_frame, orient='vertical')
    scrollbar_y.pack(side='right', fill='y')
    scrollbar_x = Scrollbar(text_frame, orient='horizontal')
    scrollbar_x.pack(side='bottom', fill='x')

    text_widget = Text(
        text_frame,
        bg='gray10',
        fg='lawn green',
        font=('Consolas', 10),
        wrap='none',
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set,
        relief='sunken',
        borderwidth=2,
        padx=5,
        pady=5,
        insertbackground='lawn green',
        selectbackground='SeaGreen4',
        selectforeground='white'
    )
    text_widget.pack(side='left', fill='both', expand=True)
    scrollbar_y.config(command=text_widget.yview)
    scrollbar_x.config(command=text_widget.xview)
    text_widget.insert('1.0', content)
    text_widget.config(state='disabled')  # Make the text read-only

    def _open_pair_plots_window() -> None:
        from config import get_output_path
        from loaders.data_loader import get_variable_names
        from plotting.plot_utils import create_pair_plots
        try:
            variables = get_variable_names(data, filter_uncertainty=True)
            if not variables:
                return
            output_path = get_output_path('pair_plot')
            create_pair_plots(data, variables, output_path=output_path)
            _show_image_toplevel(watch_data_level, output_path, t('dialog.pair_plots_title'))
        except Exception:
            pass

    opts_frame = Frame(watch_data_level, bg=UI_STYLE['bg'])
    opts_frame.pack(padx=UI_STYLE['padding'], pady=4, fill='x')
    can_show_pairs = hasattr(data, 'columns') and len(getattr(data, 'columns', [])) > 0
    if can_show_pairs:
        pair_btn = Button(
            opts_frame,
            text=t('dialog.show_pair_plots'),
            command=_open_pair_plots_window,
            width=min(42, max(36, UI_STYLE['button_width_wide'] + 10)),
            bg=UI_STYLE['bg'],
            fg=UI_STYLE['button_fg_accept'],
            activebackground=UI_STYLE['active_bg'],
            activeforeground=UI_STYLE['active_fg'],
            font=(UI_STYLE['font_family'], UI_STYLE.get('font_size_large', UI_STYLE['font_size'])),
        )
        pair_btn.pack(anchor='w', pady=4)

    watch_data_level.accept_button = Button(
        watch_data_level,
        text=t('dialog.accept'),
        command=watch_data_level.destroy,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    watch_data_level.accept_button.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    watch_data_level.accept_button.focus_set()
    parent_window.wait_window(watch_data_level)


def _parse_opt_float(s: str) -> Optional[float]:
    """Parse string to float; empty or invalid returns None."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def ask_equation_type(
    parent_window: Any,
) -> Tuple[str, Optional[List[Optional[float]]], Optional[Tuple[List[Optional[float]], List[Optional[float]]]]]:
    """
    Dialog to select fitting equation type.

    Optionally allows configuring initial values and bounds per parameter.
    Displays a grid of buttons for predefined equation types, plus options
    for custom equations and exiting.

    Args:
        parent_window: Parent Tkinter window

    Returns:
        Tuple of (equation_type, user_initial_guess, user_bounds).
        user_initial_guess and user_bounds are None when not configured.
    """
    from fitting.fitting_utils import get_equation_param_info

    equation_level = Toplevel()
    equation_level.title(t('dialog.equation_type'))
    equation_level.selected_equation = ''
    equation_level.user_initial_guess: Optional[List[Optional[float]]] = None
    equation_level.user_bounds: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None

    def _on_close_equation_type() -> None:
        equation_level.selected_equation = EXIT_SIGNAL
        equation_level.destroy()

    equation_level.protocol("WM_DELETE_WINDOW", _on_close_equation_type)

    equation_level.frame_custom = Frame(
        equation_level,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )

    equation_level.message = Label(
        equation_level.frame_custom,
        text=t('dialog.select_equation'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold')
    )

    configure_params_var: BooleanVar = BooleanVar(value=False)
    equation_level.configure_params_cb = Checkbutton(
        equation_level.frame_custom,
        text=t('dialog.configure_initial_params'),
        variable=configure_params_var,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        selectcolor=UI_STYLE['bg'],
        activebackground=UI_STYLE['bg'],
        activeforeground=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
    )

    btn_config = {
        'width': 32,
        'bg': UI_STYLE['bg'],
        'fg': "gold2",
        'activebackground': UI_STYLE['active_bg'],
        'activeforeground': UI_STYLE['active_fg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size'])
    }

    equation_keys = [
        'linear_function_with_n', 'linear_function', 'quadratic_function_complete',
        'quadratic_function', 'fourth_power', 'ln_function',
        'inverse_function', 'inverse_square_function', 'sin_function',
        'sin_function_with_c', 'cos_function', 'cos_function_with_c',
        'tan_function', 'tan_function_with_c', 'sinh_function',
        'cosh_function', 'exponential_function', 'binomial_function',
        'gaussian_function', 'square_pulse_function', 'hermite_polynomial_3',
        'hermite_polynomial_4',
    ]

    def _show_param_dialog(eq_type: str) -> None:
        param_info = get_equation_param_info(eq_type)
        if not param_info:
            equation_level.destroy()
            return
        param_names, formula = param_info
        n_params = len(param_names)

        param_dlg = Toplevel(equation_level)
        param_dlg.title(t('dialog.param_config_title'))
        param_dlg.transient(equation_level)
        param_dlg.grab_set()

        frm = Frame(param_dlg, bg=UI_STYLE['bg'], bd=UI_STYLE['border_width'])
        frm.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'], fill='both', expand=True)

        lbl_style = {
            'bg': UI_STYLE['bg'],
            'fg': UI_STYLE['fg'],
            'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
        }
        entry_style = {
            'width': 12,
            'fg': UI_STYLE['entry_fg'],
            'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
        }

        # Header row
        Label(frm, text=t('dialog.param_column_equation'), **lbl_style).grid(row=0, column=0, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_name'), **lbl_style).grid(row=0, column=1, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_initial'), **lbl_style).grid(row=0, column=2, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_range_start'), **lbl_style).grid(row=0, column=3, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_range_end'), **lbl_style).grid(row=0, column=4, padx=4, pady=2)

        initial_entries: List[Entry] = []
        lower_entries: List[Entry] = []
        upper_entries: List[Entry] = []

        for i, pname in enumerate(param_names):
            r = i + 1
            Label(frm, text=formula, **lbl_style).grid(row=r, column=0, padx=4, pady=2, sticky='w')
            Label(frm, text=pname, **lbl_style).grid(row=r, column=1, padx=4, pady=2, sticky='w')
            e_init = Entry(frm, **entry_style)
            e_init.grid(row=r, column=2, padx=4, pady=2)
            initial_entries.append(e_init)
            e_lo = Entry(frm, **entry_style)
            e_lo.grid(row=r, column=3, padx=4, pady=2)
            lower_entries.append(e_lo)
            e_hi = Entry(frm, **entry_style)
            e_hi.grid(row=r, column=4, padx=4, pady=2)
            upper_entries.append(e_hi)

        def on_accept() -> None:
            initial_guess: List[Optional[float]] = [
                _parse_opt_float(e.get()) for e in initial_entries
            ]
            lower_list: List[Optional[float]] = [
                _parse_opt_float(e.get()) for e in lower_entries
            ]
            upper_list: List[Optional[float]] = [
                _parse_opt_float(e.get()) for e in upper_entries
            ]
            equation_level.user_initial_guess = initial_guess
            equation_level.user_bounds = (lower_list, upper_list)
            param_dlg.destroy()

        btn_accept = Button(
            frm,
            text=t('dialog.accept'),
            command=on_accept,
            width=UI_STYLE['button_width'],
            bg=UI_STYLE['bg'],
            fg=UI_STYLE['button_fg_accept'],
            activebackground=UI_STYLE['active_bg'],
            activeforeground=UI_STYLE['active_fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
        )
        btn_accept.grid(row=len(param_names) + 1, column=2, columnspan=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
        param_dlg.resizable(True, False)
        equation_level.wait_window(param_dlg)

    def handle_equation_click(eq_type: str) -> None:
        """Handle predefined equation button click."""
        equation_level.selected_equation = eq_type
        if not configure_params_var.get():
            equation_level.destroy()
            return
        _show_param_dialog(eq_type)
        equation_level.destroy()

    def handle_custom_click() -> None:
        """Handle custom equation button click."""
        equation_level.selected_equation = 'custom'
        equation_level.destroy()

    def handle_exit_click() -> None:
        """Handle exit button click."""
        equation_level.selected_equation = EXIT_SIGNAL
        equation_level.destroy()

    for attr_name in equation_keys:
        btn_text = t(f'equations.{attr_name}')
        desc = t(f'equations_descriptions.{attr_name}')
        formula = EQUATION_FORMULAS.get(attr_name, '')
        tooltip_text = f"{desc}\n{t('dialog.equation')} {formula}" if formula else desc
        btn = Button(
            equation_level.frame_custom,
            text=btn_text,
            command=lambda eq_type=attr_name: handle_equation_click(eq_type),
            **btn_config
        )
        _bind_tooltip(btn, tooltip_text)
        setattr(equation_level, attr_name, btn)
    
    # Custom equation button
    equation_level.custom = Button(
        equation_level.frame_custom, 
        text=t('equations.custom_formula'), 
        command=handle_custom_click, 
        **btn_config
    )
    
    # Exit button with different styling
    equation_level.accept_button = Button(
        equation_level.frame_custom, 
        text=t('dialog.exit_option'), 
        command=handle_exit_click, 
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_cancel'], 
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    # Grid layout: row 0 message, row 1 checkbox, then equation buttons (3 cols), custom, exit
    equation_level.frame_custom.grid(column=0, row=0)
    equation_level.message.grid(
        column=0, row=0, columnspan=3, padx=UI_STYLE['padding'], pady=6
    )
    equation_level.configure_params_cb.grid(
        column=0, row=1, columnspan=3, padx=UI_STYLE['padding'], pady=4, sticky='w'
    )
    _pad = UI_STYLE['padding']
    _start_row = 2
    for i, attr_name in enumerate(equation_keys):
        getattr(equation_level, attr_name).grid(
            column=i % 3, row=_start_row + i // 3, padx=_pad, pady=_pad
        )
    _last_row = _start_row + (len(equation_keys) + 2) // 3
    equation_level.custom.grid(column=0, row=_last_row, columnspan=3, padx=_pad, pady=_pad)
    equation_level.accept_button.grid(column=2, row=_last_row + 1, padx=_pad, pady=_pad)

    equation_level.linear_function_with_n.focus_set()
    parent_window.wait_window(equation_level)

    return (
        equation_level.selected_equation,
        getattr(equation_level, 'user_initial_guess', None),
        getattr(equation_level, 'user_bounds', None),
    )


def ask_num_parameters(parent_window: Any) -> Optional[int]:
    """
    Dialog to ask for number of parameters in a custom function.
    
    Args:
        parent_window: Parent Tkinter window
        
    Returns:
        Selected number of parameters, or None if the user closed the window with X.
    """
    num_parameter_level = Toplevel()
    num_parameter_level.title(t('dialog.custom_formula_title'))
    num_parameter_level.cancelled = False
    num_parameter_level.numparam = IntVar()

    def _on_close_num_parameters() -> None:
        num_parameter_level.cancelled = True
        num_parameter_level.destroy()

    num_parameter_level.protocol("WM_DELETE_WINDOW", _on_close_num_parameters)
    num_parameter_level.frame_custom = Frame(
        num_parameter_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    num_parameter_level.message = Label(
        num_parameter_level.frame_custom, 
        text=t('dialog.num_parameters'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    num_parameter_level.num = Spinbox(
        num_parameter_level.frame_custom, 
        textvariable=num_parameter_level.numparam, 
        from_=1, 
        to=12, 
        wrap=True, 
        state='readonly', 
        width=UI_STYLE['spinbox_width'],
        fg=UI_STYLE['entry_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    num_parameter_level.accept_button = Button(
        num_parameter_level.frame_custom, 
        text=t('dialog.accept'), 
        command=num_parameter_level.destroy, 
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    _pad = UI_STYLE['padding']
    num_parameter_level.frame_custom.grid(column=0, row=0)
    num_parameter_level.message.grid(column=0, row=0, padx=_pad, pady=_pad)
    num_parameter_level.num.grid(column=1, row=0, padx=_pad, pady=_pad)
    num_parameter_level.accept_button.grid(column=1, row=1, padx=_pad, pady=_pad)

    num_parameter_level.num.focus_set()
    parent_window.wait_window(num_parameter_level)

    if getattr(num_parameter_level, 'cancelled', False):
        return None
    return num_parameter_level.numparam.get()


def ask_parameter_names(parent_window: Any, num_params: int) -> List[str]:
    """
    Dialog to ask for parameter names in a custom function.
    
    Args:
        parent_window: Parent Tkinter window
        num_params: Number of parameters to request
        
    Returns:
        List of parameter names
    """
    # Unicode codes for Greek letters
    cod1 = '\\u03B1=α, \\u03B2=β, \\u03B3=γ\n\\u03B4=δ, \\u03B5=ε, \\u03B6=ζ\n\\u03B7=η'
    cod2 = ', \\u03B8=θ, \\u03BB=λ\n\\u03BC=μ, \\u03BE=ξ, \\u03C0=π\n\\u03C1=ρ, \\u03C3=σ'
    cod3 = ', \\u03C6=φ\n\\u03C9=ω, \\u0394=Δ, \\u03A3=Σ\n\\u03A6=Φ, \\u03A9=Ω, \\u03B1=α'
    cod = cod1 + cod2 + cod3
    
    # Create exit instruction text with translation
    exit_instruction = f'\n"{t("dialog.exit_option")}" {t("dialog.exit_instruction")}'

    parameter_names_list = []
    for i in range(num_params):
        parameter_asker_leve = Toplevel()
        parameter_asker_leve.title(t('dialog.parameter_names_title'))
        parameter_asker_leve.cancelled = False
        parameter_asker_leve.name_parame = StringVar()

        def _on_close_param(w: Any = parameter_asker_leve) -> None:
            w.cancelled = True
            w.destroy()

        parameter_asker_leve.protocol("WM_DELETE_WINDOW", lambda w=parameter_asker_leve: _on_close_param(w))
        parameter_asker_leve.frame_custom = Frame(
            parameter_asker_leve, 
            borderwidth=2, 
            relief="raised", 
            bg=UI_STYLE['bg'], 
            bd=UI_STYLE['border_width']
        )
        parameter_asker_leve.message = Label(
            parameter_asker_leve.frame_custom, 
            text=t('dialog.parameter_name', index=i+1), 
            bg=UI_STYLE['bg'], 
            fg=UI_STYLE['fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        parameter_asker_leve.codes = Label(
            parameter_asker_leve.frame_custom, 
            text=cod+exit_instruction, 
            bg=UI_STYLE['bg'], 
            fg=UI_STYLE['fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        parameter_asker_leve.name_entry = Entry(
            parameter_asker_leve.frame_custom, 
            textvariable=parameter_asker_leve.name_parame,  
            bg=UI_STYLE['bg'], 
            fg=UI_STYLE['fg'],
            width=UI_STYLE['entry_width'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        parameter_asker_leve.accept_button = Button(
            parameter_asker_leve.frame_custom, 
            text=t('dialog.accept'), 
            command=parameter_asker_leve.destroy, 
            width=UI_STYLE['button_width'], 
            bg=UI_STYLE['bg'], 
            fg=UI_STYLE['button_fg_accept'],
            activebackground=UI_STYLE['active_bg'], 
            activeforeground=UI_STYLE['active_fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )

        _pad = UI_STYLE['padding']
        parameter_asker_leve.frame_custom.grid(column=0, row=0)
        parameter_asker_leve.codes.grid(
            column=0, row=0, columnspan=2, padx=_pad, pady=6
        )
        parameter_asker_leve.message.grid(column=0, row=1, padx=_pad, pady=_pad)
        parameter_asker_leve.name_entry.grid(column=1, row=1, padx=_pad, pady=_pad)
        parameter_asker_leve.accept_button.grid(column=1, row=2, padx=_pad, pady=_pad)

        parameter_asker_leve.name_entry.focus_set()
        parent_window.wait_window(parameter_asker_leve)

        if getattr(parameter_asker_leve, 'cancelled', False):
            return [EXIT_SIGNAL]
        parameter_name = parameter_asker_leve.name_parame.get()
        parameter_names_list.append(parameter_name)

    return parameter_names_list


def ask_custom_formula(parent_window: Any, parameter_names: List[str]) -> str:
    """
    Dialog to ask for custom function formula.
    
    Args:
        parent_window: Parent Tkinter window
        parameter_names: List of parameter names
        
    Returns:
        Formula entered by the user
    """
    # Unicode codes for Greek letters
    cod1 = '\\u03B1=α, \\u03B2=β, \\u03B3=γ\n\\u03B4=δ, \\u03B5=ε, \\u03B6=ζ\n\\u03B7=η'
    cod2 = ', \\u03B8=θ, \\u03BB=λ\n\\u03BC=μ, \\u03BE=ξ, \\u03C0=π\n\\u03C1=ρ, \\u03C3=σ'
    cod3 = ', \\u03C6=φ\n\\u03C9=ω, \\u0394=Δ, \\u03A3=Σ\n\\u03A6=Φ, \\u03A9=Ω, \\u03B1=α'
    cod = cod1 + cod2 + cod3
    
    # Create exit instruction text with translation
    exit_instruction = f'\n"{t("dialog.exit_option")}" {t("dialog.exit_instruction")}'

    formulator_level = Toplevel()
    formulator_level.title(t('dialog.custom_formula_title'))
    formulator_level.cancelled = False
    formulator_level.formule = StringVar()

    def _on_close_formula() -> None:
        formulator_level.cancelled = True
        formulator_level.destroy()

    formulator_level.protocol("WM_DELETE_WINDOW", _on_close_formula)
    formulator_level.frame_custom = Frame(
        formulator_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    syntax_hint_text = t('dialog.custom_formula_syntax_hint') + '\n' + t('dialog.formula_example')
    formulator_level.syntax_hint = Label(
        formulator_level.frame_custom,
        text=syntax_hint_text,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    formulator_level.message = Label(
        formulator_level.frame_custom, 
        text='y(x)= ', 
        width=8, 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    formulator_level.codes = Label(
        formulator_level.frame_custom, 
        text=cod+exit_instruction, 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    params_display = t('dialog.parameters_defined', params=', '.join(parameter_names))
    formulator_level.parametros = Label(
        formulator_level.frame_custom,
        text=params_display,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    formulator_level.name_entry = Entry(
        formulator_level.frame_custom, 
        textvariable=formulator_level.formule,  
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        width=UI_STYLE['entry_width'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    formulator_level.accept_button = Button(
        formulator_level.frame_custom, 
        text=t('dialog.accept'), 
        command=formulator_level.destroy, 
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    _pad = UI_STYLE['padding']
    formulator_level.frame_custom.grid(column=0, row=0)
    formulator_level.syntax_hint.grid(
        column=0, row=0, columnspan=2, padx=_pad, pady=(6, 0)
    )
    formulator_level.codes.grid(
        column=0, row=1, columnspan=2, padx=_pad, pady=6
    )
    formulator_level.parametros.grid(
        column=0, row=2, columnspan=2, padx=_pad, pady=_pad
    )
    formulator_level.message.grid(column=0, row=3, padx=_pad, pady=_pad)
    formulator_level.name_entry.grid(column=1, row=3, padx=_pad, pady=_pad)
    formulator_level.accept_button.grid(column=1, row=4, padx=_pad, pady=_pad)

    formulator_level.name_entry.focus_set()
    parent_window.wait_window(formulator_level)

    if getattr(formulator_level, 'cancelled', False):
        return EXIT_SIGNAL
    return formulator_level.formule.get()


def ask_num_fits(parent_window: Any, min_val: int = 2, max_val: int = 10) -> Optional[int]:
    """
    Dialog to ask for number of multiple fits.
    
    Args:
        parent_window: Parent Tkinter window
        min_val: Minimum number of fits (default: 2)
        max_val: Maximum number of fits (default: 10)
        
    Returns:
        Selected number of fits, or None if the user closed the window with X.
    """
    number_fits_level = Toplevel()
    number_fits_level.title(t('workflow.multiple_fitting_title'))
    number_fits_level.cancelled = False

    def _on_close_num_fits() -> None:
        number_fits_level.cancelled = True
        number_fits_level.destroy()

    number_fits_level.protocol("WM_DELETE_WINDOW", _on_close_num_fits)
    number_fits_level.frame_custom = Frame(
        number_fits_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    number_fits_level.num = IntVar()
    number_fits_level.num_label = Label(
        number_fits_level.frame_custom, 
        text=t('dialog.num_fits'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    number_fits_level.num_x = Spinbox(
        number_fits_level.frame_custom, 
        textvariable=number_fits_level.num, 
        from_=min_val, 
        to=max_val, 
        wrap=True, 
        state='readonly', 
        width=UI_STYLE['spinbox_width'],
        fg=UI_STYLE['entry_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    number_fits_level.accept_button = Button(
        number_fits_level.frame_custom, 
        text=t('dialog.accept'), 
        command=number_fits_level.destroy, 
        width=UI_STYLE['button_width'], 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'], 
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    _pad = UI_STYLE['padding']
    number_fits_level.frame_custom.grid(column=0, row=0)
    number_fits_level.num_label.grid(column=0, row=0, padx=_pad, pady=_pad)
    number_fits_level.num_x.grid(column=1, row=0, padx=_pad, pady=_pad)
    number_fits_level.accept_button.grid(column=1, row=1, padx=_pad, pady=_pad)

    number_fits_level.num_x.focus_set()
    parent_window.wait_window(number_fits_level)

    if getattr(number_fits_level, 'cancelled', False):
        return None
    return number_fits_level.num.get()


def show_help_dialog(parent_window: Tk | Toplevel) -> None:
    """
    Display help and information dialog about the application.
    
    Shows information about:

        - Application objective and purpose
        - Key advantages and features
        - What each fitting mode does
        - How to navigate the application
        - Where data files should be located
        - Where output plots are saved
    
    Args:
        parent_window: Parent Tkinter window
    """
    def remove_markdown_bold(text: str) -> str:
        """Remove Markdown bold markers (**) from text for Tkinter display."""
        return re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    help_level = Toplevel()
    help_level.title(t('dialog.help_title'))
    help_level.configure(background=UI_STYLE['bg'])
    help_level.resizable(width=True, height=True)
    
    # Keep the dialog readable without taking the whole screen
    screen_width = help_level.winfo_screenwidth()
    screen_height = help_level.winfo_screenheight()
    dialog_width = min(900, int(screen_width * 0.7))
    dialog_height = min(650, int(screen_height * 0.7))
    offset_x = max(0, (screen_width - dialog_width) // 2)
    offset_y = max(0, (screen_height - dialog_height) // 2)
    help_level.geometry(f"{dialog_width}x{dialog_height}+{offset_x}+{offset_y}")
    
    # Main frame
    main_frame = Frame(
        help_level,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )
    main_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)
    
    # Frame for text and scrollbar
    text_frame = Frame(main_frame, bg=UI_STYLE['bg'])
    text_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)
    
    # Scrollbar
    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side='right', fill='y')
    
    # Text widget to display help content
    help_text = Text(
        text_frame,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
        wrap='word',
        yscrollcommand=scrollbar.set,
        width=80,
        height=22
    )
    help_text.pack(side='left', fill='both', expand=True)
    
    # Configure scrollbar
    scrollbar.config(command=help_text.yview)
    
    # Help content - build dynamically from translations
    # Remove markdown bold markers for Tkinter display
    help_content = f"""
════════════════════════════════════════════════
    {remove_markdown_bold(t('help.title')).upper()}
════════════════════════════════════════════════

{remove_markdown_bold(t('help.objective_title'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.objective_description'))}

{remove_markdown_bold(t('help.advantages_title'))}
──────────────────────────────────────────────────

{('\n\n').join([remove_markdown_bold(t(f'help.advantage_{i}')) for i in range(1, 10)])}

{remove_markdown_bold(t('help.fitting_modes'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.normal_fitting'))}

{remove_markdown_bold(t('help.multiple_datasets'))}

{remove_markdown_bold(t('help.checker_fitting'))}

{remove_markdown_bold(t('help.total_fitting'))}

{remove_markdown_bold(t('help.loop_mode'))}

{remove_markdown_bold(t('help.data_format_title'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.data_format_named'))}

{remove_markdown_bold(t('help.data_format_u_prefix'))}

{remove_markdown_bold(t('help.data_format_non_negative'))}

{remove_markdown_bold(t('help.data_location'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.data_input'))}

{remove_markdown_bold(t('help.data_formats'))}

{remove_markdown_bold(t('help.output_location'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.output_plots'))}

{remove_markdown_bold(t('help.output_logs'))}

{remove_markdown_bold(t('help.stats_title'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.r_squared_desc'))}
{remove_markdown_bold(t('help.r_squared_formula'))}

{remove_markdown_bold(t('help.chi_squared_desc'))}
{remove_markdown_bold(t('help.chi_squared_formula'))}

{remove_markdown_bold(t('help.reduced_chi_squared_desc'))}
{remove_markdown_bold(t('help.reduced_chi_squared_formula'))}

{remove_markdown_bold(t('help.dof_desc'))}
{remove_markdown_bold(t('help.dof_formula'))}

{remove_markdown_bold(t('help.param_ci_95_desc'))}
{remove_markdown_bold(t('help.param_ci_95_formula'))}

═════════════════════════════════════════════════
"""
    # Insert content
    help_text.insert('1.0', help_content)
    help_text.config(state='disabled')  # Read-only
    
    # Button frame: Donations (if URL set) + Accept
    button_frame = Frame(main_frame, bg=UI_STYLE['bg'])
    button_frame.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    if DONATIONS_URL:
        donations_button = Button(
            button_frame,
            text=t('dialog.donations'),
            command=lambda: webbrowser.open(DONATIONS_URL),
            width=UI_STYLE['button_width_wide'],
            bg=UI_STYLE['bg'],
            fg=UI_STYLE['button_fg_accept'],
            activebackground=UI_STYLE['active_bg'],
            activeforeground=UI_STYLE['active_fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        donations_button.pack(side='left', padx=(0, UI_STYLE['padding']))
    
    accept_button = Button(
        button_frame,
        text=t('dialog.accept'),
        command=help_level.destroy,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    accept_button.pack(side='left')
    
    accept_button.focus_set()
    parent_window.wait_window(help_level)


def _config_section_for_key(key: str) -> str:
    """Return section key for grouping env vars in config dialog."""
    if key == 'LANGUAGE':
        return 'language'
    if key.startswith('UI_'):
        return 'ui'
    if key.startswith('PLOT_') or key == 'DPI':
        return 'plot'
    if key.startswith('FONT_'):
        return 'font'
    if key.startswith('FILE_'):
        return 'paths'
    if key == 'DONATIONS_URL':
        return 'links'
    if key.startswith('LOG_'):
        return 'logging'
    return 'other'


def show_config_dialog(parent_window: Any) -> bool:
    """
    Show configuration dialog to edit .env fields.
    Pre-fills with current env values (or defaults). On Accept, writes .env
    and returns True so the caller can restart the app. On Cancel returns False.

    Args:
        parent_window: Parent Tkinter window.

    Returns:
        True if user accepted and .env was written (caller should restart).
        False if user cancelled.
    """
    config_level = Toplevel(parent_window)
    config_level.title(t('config.title'))
    config_level.configure(background=UI_STYLE['bg'])
    config_level.transient(parent_window)
    config_level.grab_set()

    current = get_current_env_values()
    result_var: List[bool] = [False]

    # Scrollable area: Canvas + Scrollbar + inner Frame
    main_frame = Frame(
        config_level,
        borderwidth=2,
        relief='raised',
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width'],
    )
    main_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)

    canvas = Canvas(
        main_frame,
        bg=UI_STYLE['bg'],
        highlightthickness=0,
    )
    scrollbar = Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    inner = Frame(canvas, bg=UI_STYLE['bg'])

    inner.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all')),
    )
    canvas_window = canvas.create_window((0, 0), window=inner, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_frame_configure(_event: Any) -> None:
        canvas.configure(scrollregion=canvas.bbox('all'))

    def _on_canvas_configure(event: Any) -> None:
        canvas.itemconfig(canvas_window, width=event.width)

    inner.bind('<Configure>', _on_frame_configure)
    canvas.bind('<Configure>', _on_canvas_configure)

    def _on_mousewheel(event: Any) -> str:
        """Scroll canvas with mouse wheel (Windows: delta; Linux: Button4/5)."""
        if hasattr(event, 'delta') and event.delta != 0:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        elif event.num == 5:
            canvas.yview_scroll(1, 'units')
        elif event.num == 4:
            canvas.yview_scroll(-1, 'units')
        return 'break'

    canvas.bind('<MouseWheel>', _on_mousewheel)
    inner.bind('<MouseWheel>', _on_mousewheel)
    inner.bind('<Button-4>', _on_mousewheel)
    inner.bind('<Button-5>', _on_mousewheel)

    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)

    lbl_style = {
        'bg': UI_STYLE['bg'],
        'fg': UI_STYLE['fg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
    }
    desc_style = {
        'bg': UI_STYLE['bg'],
        'fg': UI_STYLE['fg'],
        'font': (UI_STYLE['font_family'], max(8, UI_STYLE['font_size'] - 2)),
    }
    entry_style = {
        'width': UI_STYLE['entry_width'],
        'fg': UI_STYLE['entry_fg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
    }

    entries: dict[str, Tuple[str, Union[BooleanVar, StringVar]]] = {}
    row_index = 0
    last_section: Optional[str] = None

    # All keys in ENV_SCHEMA are shown (language, UI, plot, font, paths including FILE_PLOT_FORMAT, links, logging)
    for item in ENV_SCHEMA:
        key = item['key']
        default = item['default']
        cast_type = item['cast_type']
        section = _config_section_for_key(key)

        if section != last_section:
            section_label = Label(
                inner,
                text=t(f'config.section_{section}'),
                bg=UI_STYLE['bg'],
                fg=UI_STYLE['fg'],
                font=(UI_STYLE['font_family'], UI_STYLE['font_size'], 'bold'),
            )
            section_label.grid(row=row_index, column=0, columnspan=2, sticky='w', padx=4, pady=(12, 4))
            row_index += 1
            last_section = section

        label_text = t(f'config.label_{key}')
        Label(inner, text=label_text, **lbl_style).grid(row=row_index, column=0, sticky='w', padx=4, pady=2)
        desc_text = t(f'config.desc_{key}')
        desc_lbl = Label(inner, text=desc_text, **desc_style, wraplength=400, justify='left')
        desc_lbl.grid(row=row_index + 1, column=0, columnspan=2, sticky='w', padx=12, pady=(0, 6))
        row_index += 2

        if cast_type == bool:
            var = BooleanVar(value=current.get(key, 'false').lower() in ('true', '1', 'yes'))
            cb = Checkbutton(inner, variable=var, **lbl_style, selectcolor=UI_STYLE['bg'])
            cb.grid(row=row_index, column=0, columnspan=2, sticky='w', padx=4, pady=2)
            entries[key] = ('check', var)
        else:
            raw_val = current.get(key, str(default))
            opts = item.get('options')
            if opts:
                # Ensure initial value is in the dropdown (e.g. env may have lowercase)
                opts_list = list(opts)
                if raw_val in opts_list:
                    sv = StringVar(value=raw_val)
                else:
                    normalized = str(raw_val).upper() if key == 'LOG_LEVEL' else str(raw_val).lower()
                    sv = StringVar(value=normalized if normalized in opts_list else str(default))
                combo = ttk.Combobox(
                    inner,
                    textvariable=sv,
                    values=opts_list,
                    state='readonly',
                    width=entry_style['width'],
                )
                combo.grid(row=row_index, column=0, columnspan=2, sticky='ew', padx=4, pady=2)
                entries[key] = ('entry', sv)
            else:
                sv = StringVar(value=current.get(key, str(default)))
                ent = Entry(inner, textvariable=sv, **entry_style)
                ent.grid(row=row_index, column=0, columnspan=2, sticky='ew', padx=4, pady=2)
                entries[key] = ('entry', sv)
        row_index += 1

    inner.columnconfigure(0, weight=1)

    def on_accept() -> None:
        values: dict[str, str] = {}
        for item in ENV_SCHEMA:
            key = item['key']
            cast_type = item['cast_type']
            default = item['default']
            w = entries.get(key)
            if w is None:
                continue
            if cast_type == bool:
                _, var = w
                values[key] = 'true' if var.get() else 'false'
            else:
                _, sv = w
                raw = sv.get().strip()
                if not raw:
                    values[key] = str(default)
                else:
                    try:
                        if cast_type == int:
                            int(raw)
                        elif cast_type == float:
                            float(raw)
                    except ValueError:
                        values[key] = str(default)
                    else:
                        values[key] = raw
        env_path = get_project_root() / '.env'
        try:
            write_env_file(env_path, values)
            result_var[0] = True
        except OSError:
            from tkinter import messagebox
            messagebox.showerror(
                t('error.critical_error'),
                t('config.save_error', path=str(env_path)),
            )
            return
        config_level.destroy()

    def on_cancel() -> None:
        config_level.destroy()

    btn_frame = Frame(config_level, bg=UI_STYLE['bg'])
    btn_frame.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    Button(
        btn_frame,
        text=t('dialog.accept'),
        command=on_accept,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
    ).pack(side='left', padx=(0, UI_STYLE['padding']))

    Button(
        btn_frame,
        text=t('dialog.cancel'),
        command=on_cancel,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_cancel'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
    ).pack(side='left')

    screen_width = config_level.winfo_screenwidth()
    screen_height = config_level.winfo_screenheight()
    dialog_width = min(760, int(screen_width * 0.58))
    dialog_height = min(800, int(screen_height * 0.85))
    config_level.geometry(f'{dialog_width}x{dialog_height}+{max(0, (screen_width - dialog_width) // 2)}+{max(0, (screen_height - dialog_height) // 2)}')
    config_level.resizable(True, True)

    config_level.protocol('WM_DELETE_WINDOW', on_cancel)
    parent_window.wait_window(config_level)
    return result_var[0]


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
    
    # Load image
    plot_level.imagen = PhotoImage(file=output_path)
    
    # Create equation text widget (selectable)
    # Calculate width based on equation length
    equation_width = len(equation_str) + 2  # Add small padding
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
    plot_level.equation_text.config(state='disabled')  # Read-only but still selectable
    
    # Create parameters text widget (selectable, now includes R²)
    # Count lines and calculate width based on longest line
    text_lines = text.split('\n')
    num_lines = len(text_lines)
    max_line_length = max(len(line) for line in text_lines) if text_lines else 0
    param_width = max_line_length + 2  # Add small padding
    # Create a frame to hold parameters and image side by side
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
    plot_level.label_parameters.config(state='disabled')  # Read-only but still selectable
    

    
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
    
    # Top: Equation
    plot_level.equation_text.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    # Middle: Frame containing parameters (left, now includes R²) and image (right)
    plot_level.middle_frame.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    _px, _py = UI_THEME['padding_x'], UI_THEME['padding_y']
    plot_level.label_parameters.pack(
        in_=plot_level.middle_frame, side='left', padx=_px, pady=_py
    )
    plot_level.image.pack(
        in_=plot_level.middle_frame, side='left', padx=_px, pady=_py
    )
    # Bottom: Accept button
    plot_level.accept_button.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    plot_level.accept_button.focus_set()
    
    return plot_level
