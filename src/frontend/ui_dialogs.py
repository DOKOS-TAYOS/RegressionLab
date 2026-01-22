#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI Dialogs module.
Contains all Tkinter dialog windows for user interaction.
"""

from tkinter import Toplevel, Frame, Label, Spinbox, Button, Entry, StringVar, IntVar, Text, Scrollbar, Radiobutton
from tkinter import ttk
from typing import Tuple, List
from config import UI_STYLE, EXIT_SIGNAL
from i18n import t


def ask_file_type(parent_window) -> str:
    """
    Dialog to ask for data file type.
    
    Presents radio buttons with file type options (xlsx, xls, csv, Exit/Salir).
    User can select one option.
    
    Args:
        parent_window: Parent Tkinter window
        
    Returns:
        Selected file type ('csv', 'xls', 'xlsx', EXIT_SIGNAL, or '')
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
    file_type_values = ('xlsx', 'xls', 'csv', t('dialog.exit_option'))
    
    # Set default value
    call_file_level.tipo.set(file_type_values[0])
    
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
    # Label on row 0
    call_file_level.label_message.grid(column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'], sticky='w')
    # Radio buttons frame on row 1
    call_file_level.radio_frame.grid(column=0, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    # Button on row 2
    call_file_level.accept_button.grid(column=0, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    # Set initial focus on the first radiobutton for keyboard navigation
    call_file_level.radiobuttons[0].focus_set()
    
    # Wait for dialog to close before continuing
    parent_window.wait_window(call_file_level)

    # Map translated exit option back to internal EXIT_SIGNAL
    selected_value = call_file_level.tipo.get()
    if selected_value == t('dialog.exit_option'):
        return EXIT_SIGNAL
    return selected_value


def ask_file_name(parent_window, file_list: list) -> str:
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
    call_data_level.label_message.grid(column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_data_level.name_entry.grid(column=1, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_data_level.accept_button.grid(column=0, row=1, columnspan=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    call_data_level.name_entry.focus_set()
    parent_window.wait_window(call_data_level)

    return call_data_level.arch.get()


def ask_variables(parent_window, variable_names: list) -> Tuple[str, str, str]:
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
    call_var_level.label_message_plot.grid(column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_var_level.graf_nom.grid(column=1, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_var_level.label_message.grid(column=0, row=1, columnspan=2, padx=UI_STYLE['padding'], pady=6)
    call_var_level.label_message_x.grid(column=0, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_var_level.x_nom.grid(column=1, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_var_level.label_message_y.grid(column=0, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_var_level.y_nom.grid(column=1, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    call_var_level.accept_button.grid(column=1, row=4, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    call_var_level.x_nom.focus_set()
    parent_window.wait_window(call_var_level)

    return call_var_level.x_name.get(), call_var_level.y_name.get(), call_var_level.graf_name.get()


def show_data_dialog(parent_window, data) -> None:
    """
    Dialog to display loaded data.
    
    Args:
        parent_window: Parent Tkinter window
        data: Data to display
    """
    watch_data_level = Toplevel()
    watch_data_level.title(t('dialog.show_data_title'))
    watch_data_level.configure(background=UI_STYLE['bg'])
    
    # Set minimum window size for better data visibility
    watch_data_level.minsize(800, 600)
    
    # Frame para contener el texto y las scrollbars
    text_frame = Frame(watch_data_level, bg=UI_STYLE['bg'])
    text_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)
    
    # Scrollbar vertical
    scrollbar_y = Scrollbar(text_frame, orient='vertical')
    scrollbar_y.pack(side='right', fill='y')
    
    # Scrollbar horizontal
    scrollbar_x = Scrollbar(text_frame, orient='horizontal')
    scrollbar_x.pack(side='bottom', fill='x')
    
    # Text widget to display the data
    text_widget = Text(
        text_frame,
        bg='gray10',
        fg='lawn green',
        font=('Consolas', 10),  # Monospaced font for better alignment
        wrap='none',  # No wrap to view tabular data correctly
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set,
        relief='sunken',
        borderwidth=2,
        padx=5,
        pady=5,
        insertbackground='lawn green',  # Cursor color
        selectbackground='SeaGreen4',  # Selection color
        selectforeground='white'
    )
    text_widget.pack(side='left', fill='both', expand=True)
    
    # Configure the scrollbars
    scrollbar_y.config(command=text_widget.yview)
    scrollbar_x.config(command=text_widget.xview)
    
    # Insert the data into the Text widget
    text_widget.insert('1.0', data)
    text_widget.config(state='disabled')  # Make the text read-only
    
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


def ask_equation_type(parent_window) -> str:
    """
    Dialog to select fitting equation type.
    
    Displays a grid of buttons for predefined equation types, plus options
    for custom equations and exiting. Each button represents a mathematical
    model that can be fitted to the data.
    
    Args:
        parent_window: Parent Tkinter window
        
    Returns:
        Selected equation type identifier, 'custom' for custom equation, or EXIT_SIGNAL to exit
    """
    # Create dialog window
    equation_level = Toplevel()
    equation_level.title(t('dialog.equation_type'))
    equation_level.selected_equation = ''  # Variable to store the user's selection
    
    # Main frame with styled border
    equation_level.frame_custom = Frame(
        equation_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
    )
    
    # Header label
    equation_level.message = Label(
        equation_level.frame_custom, 
        text=t('dialog.select_equation'), 
        bg=UI_STYLE['bg'], 
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold')
    )
    
    # Common button styling configuration
    btn_config = {
        'width': 20,
        'bg': UI_STYLE['bg'],
        'fg': "gold2",  # Gold color for equation buttons
        'activebackground': UI_STYLE['active_bg'],
        'activeforeground': UI_STYLE['active_fg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size'])
    }
    
    # Define all available equation types with their display text
    # Format: (internal_name, display_text)
    equation_buttons = [
        ('linear_function_with_n', 'y=mx+n'),  # Linear with intercept
        ('linear_function', 'y=mx'),  # Linear through origin
        ('quadratic_function_complete', 'y=cx^2+bx+a'),  # Full quadratic
        ('quadratic_function', 'y=ax^2'),  # Simple quadratic
        ('fourth_power', 'y=ax^4'),  # Fourth power
        ('sin_function', 'y=a sin(bx)'),  # Sinusoidal
        ('sin_function_with_c', 'y=a sin(bx+c)'),  # Sinusoidal with phase
        ('cos_function', 'y=a cos(bx)'),  # Cosinusoidal
        ('cos_function_with_c', 'y=a cos(bx+c)'),  # Cosinusoidal with phase
        ('sinh_function', 'y=a sinh(bx)'),  # Hyperbolic sine
        ('cosh_function', 'y=a cosh(bx)'),  # Hyperbolic cosine
        ('ln_function', 'y=a ln(x)'),  # Logarithmic
        ('inverse_function', 'y=a/x'),  # Inverse (1/x)
        ('inverse_square_function', 'y=a/x^2'),  # Inverse square (1/x^2)
    ]
    # Button click handlers - these set the selection and close the dialog
    def handle_equation_click(eq_type: str) -> None:
        """Handle predefined equation button click."""
        equation_level.selected_equation = eq_type
        equation_level.destroy()
    
    def handle_custom_click() -> None:
        """Handle custom equation button click."""
        equation_level.selected_equation = 'custom'
        equation_level.destroy()
    
    def handle_exit_click() -> None:
        """Handle exit button click."""
        equation_level.selected_equation = EXIT_SIGNAL
        equation_level.destroy()
    
    # Dynamically create buttons for all predefined equations
    # Using setattr to attach buttons as attributes to the window object
    for attr_name, text in equation_buttons:
        setattr(equation_level, attr_name, 
                Button(equation_level.frame_custom, text=text, 
                       command=lambda eq_type=attr_name: handle_equation_click(eq_type), 
                       **btn_config))
    
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

    # Grid layout - organized in rows of 3 buttons for clean appearance
    equation_level.frame_custom.grid(column=0, row=0)
    equation_level.message.grid(column=0, row=0, columnspan=3, padx=UI_STYLE['padding'], pady=6)
    
    # Row 1: Linear functions
    equation_level.linear_function_with_n.grid(column=0, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.linear_function.grid(column=1, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.ln_function.grid(column=2, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    # Row 2: Polynomial functions
    equation_level.quadratic_function_complete.grid(column=0, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.quadratic_function.grid(column=1, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.fourth_power.grid(column=2, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    # Row 3: Sine functions
    equation_level.sin_function.grid(column=0, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.sin_function_with_c.grid(column=1, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.sinh_function.grid(column=2, row=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    # Row 4: Cosine functions
    equation_level.cos_function.grid(column=0, row=4, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.cos_function_with_c.grid(column=1, row=4, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.cosh_function.grid(column=2, row=4, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    # Row 5: Inverse functions
    equation_level.inverse_function.grid(column=0, row=5, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    equation_level.inverse_square_function.grid(column=1, row=5, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    # Row 6: Custom equation button (spans all 3 columns)
    equation_level.custom.grid(column=0, row=6, columnspan=3, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    # Row 7: Exit button (right-aligned in column 2)
    equation_level.accept_button.grid(column=2, row=7, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    equation_level.linear_function_with_n.focus_set()
    parent_window.wait_window(equation_level)
    
    return equation_level.selected_equation


def ask_num_parameters(parent_window) -> int:
    """
    Dialog to ask for number of parameters in a custom function.
    
    Args:
        parent_window: Parent Tkinter window
        
    Returns:
        Selected number of parameters
    """
    num_parameter_level = Toplevel()
    num_parameter_level.title(t('dialog.custom_formula_title'))
    num_parameter_level.numparam = IntVar()
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

    num_parameter_level.frame_custom.grid(column=0, row=0)
    num_parameter_level.message.grid(column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    num_parameter_level.num.grid(column=1, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    num_parameter_level.accept_button.grid(column=1, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    num_parameter_level.num.focus_set()
    parent_window.wait_window(num_parameter_level)

    return num_parameter_level.numparam.get()


def ask_parameter_names(parent_window, num_params: int) -> List[str]:
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
        parameter_asker_leve.name_parame = StringVar()
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

        parameter_asker_leve.frame_custom.grid(column=0, row=0)
        parameter_asker_leve.codes.grid(column=0, row=0, columnspan=2, padx=UI_STYLE['padding'], pady=6)
        parameter_asker_leve.message.grid(column=0, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
        parameter_asker_leve.name_entry.grid(column=1, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
        parameter_asker_leve.accept_button.grid(column=1, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

        parameter_asker_leve.name_entry.focus_set()
        parent_window.wait_window(parameter_asker_leve)

        parameter_name = parameter_asker_leve.name_parame.get()
        parameter_names_list.append(parameter_name)

    return parameter_names_list


def ask_custom_formula(parent_window, parameter_names: List[str]) -> str:
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
    formulator_level.formule = StringVar()
    formulator_level.frame_custom = Frame(
        formulator_level, 
        borderwidth=2, 
        relief="raised", 
        bg=UI_STYLE['bg'], 
        bd=UI_STYLE['border_width']
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
    formulator_level.parametros = Label(
        formulator_level.frame_custom, 
        text=str(parameter_names), 
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

    formulator_level.frame_custom.grid(column=0, row=0)
    formulator_level.codes.grid(column=0, row=0, columnspan=2, padx=UI_STYLE['padding'], pady=6)
    formulator_level.message.grid(column=0, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    formulator_level.name_entry.grid(column=1, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    formulator_level.accept_button.grid(column=1, row=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    formulator_level.name_entry.focus_set()
    parent_window.wait_window(formulator_level)

    return formulator_level.formule.get()


def ask_num_fits(parent_window, min_val: int = 2, max_val: int = 10) -> int:
    """
    Dialog to ask for number of multiple fits.
    
    Args:
        parent_window: Parent Tkinter window
        min_val: Minimum number of fits (default: 2)
        max_val: Maximum number of fits (default: 10)
        
    Returns:
        Selected number of fits
    """
    number_fits_level = Toplevel()
    number_fits_level.title(t('workflow.multiple_fitting_title'))
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

    number_fits_level.frame_custom.grid(column=0, row=0)
    number_fits_level.num_label.grid(column=0, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    number_fits_level.num_x.grid(column=1, row=0, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    number_fits_level.accept_button.grid(column=1, row=1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    number_fits_level.num_x.focus_set()
    parent_window.wait_window(number_fits_level)

    return number_fits_level.num.get()


def show_help_dialog(parent_window) -> None:
    """
    Display help and information dialog about the application.
    
    Shows information about:
    - What each fitting mode does
    - How to navigate the application
    - Where data files should be located
    - Where output plots are saved
    
    Args:
        parent_window: Parent Tkinter window
    """
    help_level = Toplevel()
    help_level.title(t('dialog.help_title'))
    help_level.configure(background=UI_STYLE['bg'])
    help_level.resizable(width=True, height=True)
    
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
        height=25
    )
    help_text.pack(side='left', fill='both', expand=True)
    
    # Configure scrollbar
    scrollbar.config(command=help_text.yview)
    
    # Help content - build dynamically from translations
    help_content = f"""
════════════════════════════════════════════════
    {t('help.title').upper()}
════════════════════════════════════════════════

{t('help.fitting_modes')}
──────────────────────────────────────────────────

{t('help.normal_fitting')}

{t('help.multiple_datasets')}

{t('help.checker_fitting')}

{t('help.total_fitting')}

{t('help.loop_mode')}

{t('help.navigation')}
──────────────────────────────────────────────────

{t('help.navigation_spinbox')}

{t('help.navigation_accept')}

{t('help.data_location')}
──────────────────────────────────────────────────

{t('help.data_input')}

{t('help.data_formats')}

{t('help.output_location')}
──────────────────────────────────────────────────

{t('help.output_plots')}

{t('help.output_logs')}

═════════════════════════════════════════════════
"""
    # Insert content
    help_text.insert('1.0', help_content)
    help_text.config(state='disabled')  # Read-only
    
    # Accept button
    accept_button = Button(
        main_frame,
        text=t('dialog.accept'),
        command=help_level.destroy,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    accept_button.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    
    accept_button.focus_set()
    parent_window.wait_window(help_level)


def create_result_window(fit_name: str, text: str, equation_str: str, output_path: str) -> Toplevel:
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
    from tkinter import PhotoImage
    from config import UI_THEME, FONT_CONFIG
    
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
    
    # Create parameters text widget (selectable)
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
    # Middle: Frame containing parameters (left) and image (right)
    plot_level.middle_frame.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    plot_level.label_parameters.pack(in_=plot_level.middle_frame, side='left', padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    plot_level.image.pack(in_=plot_level.middle_frame, side='left', padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    # Bottom: Accept button
    plot_level.accept_button.pack(padx=UI_THEME['padding_x'], pady=UI_THEME['padding_y'])
    plot_level.accept_button.focus_set()
    
    return plot_level
