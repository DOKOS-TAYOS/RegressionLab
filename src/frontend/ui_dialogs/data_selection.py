"""Data selection dialogs: file type, file name, variables, and data preview."""

from typing import Any, List, Tuple
from tkinter import Tk, Toplevel, Frame, Label, Button, Entry, StringVar, Radiobutton, Scrollbar, Text, ttk

from config import DATA_FILE_TYPES, EXIT_SIGNAL, UI_STYLE
from i18n import t

# Max size for pair-plot image window so it does not resize the desktop
_PAIR_PLOT_MAX_WIDTH = 920
_PAIR_PLOT_MAX_HEIGHT = 720


def ask_file_type(parent_window: Any) -> str:
    """
    Dialog to ask for data file type.

    Presents radio buttons with file type options (xlsx, csv, txt, Exit/Salir).
    User can select one option.

    Args:
        parent_window: Parent Tkinter window

    Returns:
        Selected file type (one of config.DATA_FILE_TYPES, EXIT_SIGNAL, or '')
    """
    call_file_level = Toplevel()
    call_file_level.title(t('dialog.data'))

    call_file_level.frame = Frame(
        call_file_level,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )

    call_file_level.tipo = StringVar()
    call_file_level.label_message = Label(
        call_file_level.frame,
        text=t('dialog.file_type'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    file_type_values = tuple(DATA_FILE_TYPES) + (t('dialog.exit_option'),)
    call_file_level.tipo.set(file_type_values[0])
    call_file_level.cancelled = False

    def _on_close_file_type() -> None:
        call_file_level.cancelled = True
        call_file_level.destroy()

    call_file_level.protocol("WM_DELETE_WINDOW", _on_close_file_type)

    call_file_level.radio_frame = Frame(call_file_level.frame, bg=UI_STYLE['bg'])
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
            selectcolor=UI_STYLE['bg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        rb.grid(row=i, column=0, sticky='w', padx=UI_STYLE['padding'], pady=2)
        call_file_level.radiobuttons.append(rb)

    call_file_level.accept_button = Button(
        call_file_level.frame,
        text=t('dialog.accept'),
        command=call_file_level.destroy,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

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

    call_file_level.radiobuttons[0].focus_set()
    parent_window.wait_window(call_file_level)

    if getattr(call_file_level, 'cancelled', False):
        return EXIT_SIGNAL
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

    Args:
        parent_window: Parent Tkinter window
        variable_names: List of available variable names from the dataset

    Returns:
        Tuple of (x_name, y_name, plot_name)
    """
    call_var_level = Toplevel()
    call_var_level.title(t('dialog.data'))
    call_var_level.cancelled = False

    def _on_close_variables() -> None:
        call_var_level.cancelled = True
        call_var_level.destroy()

    call_var_level.protocol("WM_DELETE_WINDOW", _on_close_variables)

    call_var_level.frame_custom = Frame(
        call_var_level,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )

    call_var_level.x_name = StringVar()
    call_var_level.y_name = StringVar()
    call_var_level.graf_name = StringVar()

    call_var_level.label_message = Label(
        call_var_level.frame_custom,
        text=t('dialog.variable_names'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size_large'], 'bold')
    )
    call_var_level.label_message_x = Label(
        call_var_level.frame_custom,
        text=t('dialog.independent_variable'),
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )

    filtered_variable_names = []
    excluded_vars = set()
    for var in variable_names:
        if var in excluded_vars:
            continue
        if var.startswith('u') and len(var) > 1:
            base_var = var[1:]
            if base_var in variable_names:
                excluded_vars.add(var)
                continue
        u_var = f'u{var}'
        if u_var in variable_names:
            excluded_vars.add(u_var)
        filtered_variable_names.append(var)

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


def _show_image_toplevel(parent: Tk | Toplevel, image_path: str, title: str) -> None:
    """Open a Toplevel window showing an image from file (e.g. pair plot), scaled to fit max size."""
    from pathlib import Path

    from frontend.image_utils import (
        load_image_scaled,
        plot_display_path,
        preview_path_to_remove_after_display,
    )

    display_path = plot_display_path(image_path)
    preview_to_remove = preview_path_to_remove_after_display(display_path, image_path)
    photo = load_image_scaled(
        display_path, _PAIR_PLOT_MAX_WIDTH, _PAIR_PLOT_MAX_HEIGHT
    )
    if not photo:
        return
    win = Toplevel(parent)
    win.title(title)
    win.configure(background=UI_STYLE['bg'])
    win.resizable(False, False)

    def _on_close() -> None:
        if preview_to_remove:
            try:
                Path(preview_to_remove).unlink(missing_ok=True)
            except OSError:
                pass
        win.destroy()

    label = Label(win, image=photo, bg=UI_STYLE['bg'])
    label.image = photo
    label.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    Button(
        win,
        text=t('dialog.accept'),
        command=_on_close,
        width=UI_STYLE['button_width'],
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['button_fg_accept'],
        activebackground=UI_STYLE['active_bg'],
        activeforeground=UI_STYLE['active_fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
    ).pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    win.protocol("WM_DELETE_WINDOW", _on_close)


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
    text_widget.config(state='disabled')

    def _open_pair_plots_window() -> None:
        from config import get_output_path
        from loaders import get_variable_names
        from plotting import create_pair_plots
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
