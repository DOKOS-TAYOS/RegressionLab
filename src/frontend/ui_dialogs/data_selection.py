"""Data selection dialogs: file type, file name, variables, and data preview."""

from typing import Any, List, Tuple
from tkinter import Tk, Toplevel, StringVar, Text, ttk

from config import DATA_FILE_TYPES, EXIT_SIGNAL, UI_STYLE, apply_hover_to_children, get_entry_font
from frontend.keyboard_nav import bind_enter_to_accept, setup_arrow_enter_navigation
from i18n import t

# Max size for pair-plot image window so it does not resize the desktop
_PAIR_PLOT_MAX_WIDTH = 920
_PAIR_PLOT_MAX_HEIGHT = 720


def _filter_uncertainty_variables(variable_names: List[str]) -> List[str]:
    """
    Filter out uncertainty-paired variables (e.g. keep 'x', drop 'ux' when 'x' exists).

    Returns a list with at most one of each base/uncertainty pair for cleaner selection.
    """
    filtered: List[str] = []
    excluded: set[str] = set()
    for var in variable_names:
        if var in excluded:
            continue
        if var.startswith('u') and len(var) > 1:
            base_var = var[1:]
            if base_var in variable_names:
                excluded.add(var)
                continue
        u_var = f'u{var}'
        if u_var in variable_names:
            excluded.add(u_var)
        filtered.append(var)
    return filtered if filtered else variable_names


def ask_file_type(parent_window: Any) -> str:
    """
    Dialog to ask for data file type.

    Presents radio buttons with file type options (xlsx, csv, txt, Exit).
    User can select one option.

    Args:
        parent_window: Parent Tkinter window

    Returns:
        Selected file type (one of ``config.DATA_FILE_TYPES``, ``EXIT_SIGNAL``,
        or empty string ``''``).
    """
    call_file_level = Toplevel()
    call_file_level.title(t('dialog.data'))

    call_file_level.frame = ttk.Frame(call_file_level, padding=UI_STYLE['border_width'])

    call_file_level.tipo = StringVar()
    call_file_level.label_message = ttk.Label(
        call_file_level.frame,
        text=t('dialog.file_type'),
    )

    file_type_values = tuple(DATA_FILE_TYPES) + (t('dialog.exit_option'),)
    call_file_level.tipo.set(file_type_values[0])
    call_file_level.cancelled = False

    def _on_close_file_type() -> None:
        call_file_level.cancelled = True
        call_file_level.destroy()

    call_file_level.protocol("WM_DELETE_WINDOW", _on_close_file_type)

    call_file_level.radio_frame = ttk.Frame(call_file_level.frame)
    call_file_level.radiobuttons = []
    for i, value in enumerate(file_type_values):
        rb = ttk.Radiobutton(
            call_file_level.radio_frame,
            text=value,
            variable=call_file_level.tipo,
            value=value,
        )
        rb.grid(row=i, column=0, sticky='w', padx=UI_STYLE['padding'], pady=2)
        call_file_level.radiobuttons.append(rb)

    call_file_level.accept_button = ttk.Button(
        call_file_level.frame,
        text=t('dialog.accept'),
        command=call_file_level.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
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

    def _file_type_on_enter(widget: Any, _event: Any) -> bool:
        if widget in call_file_level.radiobuttons:
            widget.invoke()
            return True
        return False

    setup_arrow_enter_navigation(
        [[rb] for rb in call_file_level.radiobuttons] + [[call_file_level.accept_button]],
        on_enter=_file_type_on_enter,
    )
    apply_hover_to_children(call_file_level.frame)
    call_file_level.radiobuttons[0].focus_set()
    call_file_level.resizable(False, False)
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
        parent_window: Parent Tkinter window.
        file_list: List of available file names (without extensions).

    Returns:
        Selected file name (without extension), or empty string if cancelled.
    """
    call_data_level = Toplevel()
    call_data_level.title(t('dialog.data'))
    call_data_level.cancelled = False

    def _on_close_file_name() -> None:
        call_data_level.cancelled = True
        call_data_level.destroy()

    call_data_level.protocol("WM_DELETE_WINDOW", _on_close_file_name)
    call_data_level.frame_custom = ttk.Frame(call_data_level, padding=UI_STYLE['border_width'])
    call_data_level.arch = StringVar()

    call_data_level.label_message = ttk.Label(
        call_data_level.frame_custom,
        text=t('dialog.file_name'),
    )
    call_data_level.name_entry = ttk.Combobox(
        call_data_level.frame_custom,
        textvariable=call_data_level.arch,
        values=file_list,
        state='readonly',
        width=UI_STYLE['entry_width'],
        font=get_entry_font(),
    )
    if file_list:
        call_data_level.name_entry.current(0)

    call_data_level.accept_button = ttk.Button(
        call_data_level.frame_custom,
        text=t('dialog.accept'),
        command=call_data_level.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
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

    bind_enter_to_accept([call_data_level.name_entry], call_data_level.destroy)
    apply_hover_to_children(call_data_level.frame_custom)
    call_data_level.name_entry.focus_set()
    call_data_level.resizable(False, False)
    parent_window.wait_window(call_data_level)

    if getattr(call_data_level, 'cancelled', False):
        return ''
    return call_data_level.arch.get()


def ask_variables(parent_window: Any, variable_names: List[str]) -> Tuple[str, str, str]:
    """
    Dialog to select independent (x) and dependent (y) variables and plot name.

    Args:
        parent_window: Parent Tkinter window.
        variable_names: List of available variable names from the dataset.

    Returns:
        Tuple of ``(x_name, y_name, plot_name)``. Returns ``('', '', '')``
        if user cancels.
    """
    call_var_level = Toplevel()
    call_var_level.title(t('dialog.data'))
    call_var_level.cancelled = False

    def _on_close_variables() -> None:
        call_var_level.cancelled = True
        call_var_level.destroy()

    call_var_level.protocol("WM_DELETE_WINDOW", _on_close_variables)

    call_var_level.frame_custom = ttk.Frame(call_var_level, padding=UI_STYLE['border_width'])

    call_var_level.x_name = StringVar()
    call_var_level.y_name = StringVar()
    call_var_level.graf_name = StringVar()

    call_var_level.label_message = ttk.Label(
        call_var_level.frame_custom,
        text=t('dialog.variable_names'),
        style='LargeBold.TLabel',
    )
    call_var_level.label_message_x = ttk.Label(
        call_var_level.frame_custom,
        text=t('dialog.independent_variable'),
    )

    variable_names = _filter_uncertainty_variables(variable_names)

    call_var_level.x_nom = ttk.Combobox(
        call_var_level.frame_custom,
        textvariable=call_var_level.x_name,
        values=variable_names,
        state='readonly',
        width=UI_STYLE['spinbox_width'],
        font=get_entry_font(),
    )
    if variable_names:
        call_var_level.x_nom.current(0)

    call_var_level.label_message_y = ttk.Label(
        call_var_level.frame_custom,
        text=t('dialog.dependent_variable'),
    )
    call_var_level.y_nom = ttk.Combobox(
        call_var_level.frame_custom,
        textvariable=call_var_level.y_name,
        values=variable_names,
        state='readonly',
        width=UI_STYLE['spinbox_width'],
        font=get_entry_font(),
    )
    if len(variable_names) > 1:
        call_var_level.y_nom.current(1)
    elif variable_names:
        call_var_level.y_nom.current(0)
    call_var_level.accept_button = ttk.Button(
        call_var_level.frame_custom,
        text=t('dialog.accept'),
        command=call_var_level.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )
    call_var_level.label_message_plot = ttk.Label(
        call_var_level.frame_custom,
        text=t('dialog.plot_name'),
    )
    call_var_level.graf_nom = ttk.Entry(
        call_var_level.frame_custom,
        textvariable=call_var_level.graf_name,
        width=UI_STYLE['entry_width'],
        font=get_entry_font(),
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

    bind_enter_to_accept(
        [call_var_level.x_nom, call_var_level.y_nom, call_var_level.graf_nom],
        call_var_level.destroy,
    )
    apply_hover_to_children(call_var_level.frame_custom)
    call_var_level.graf_nom.focus_set()
    call_var_level.resizable(False, False)
    parent_window.wait_window(call_var_level)

    if getattr(call_var_level, 'cancelled', False):
        return ('', '', '')
    return call_var_level.x_name.get(), call_var_level.y_name.get(), call_var_level.graf_name.get()


def ask_multiple_x_variables(
    parent_window: Any, variable_names: List[str], num_vars: int, first_x_name: str
) -> List[str]:
    """
    Dialog to select multiple independent (x) variables for multidimensional fitting.

    Args:
        parent_window: Parent Tkinter window.
        variable_names: List of available variable names from the dataset.
        num_vars: Number of independent variables to select.
        first_x_name: Name of the first x variable already selected.

    Returns:
        List of x variable names. Returns empty list if user cancels.
    """
    call_var_level = Toplevel()
    call_var_level.title(t('dialog.data'))
    call_var_level.cancelled = False

    def _on_close_variables() -> None:
        call_var_level.cancelled = True
        call_var_level.destroy()

    call_var_level.protocol("WM_DELETE_WINDOW", _on_close_variables)

    call_var_level.frame_custom = ttk.Frame(call_var_level, padding=UI_STYLE['border_width'])

    call_var_level.label_message = ttk.Label(
        call_var_level.frame_custom,
        text=t('dialog.select_multiple_x_variables', num=num_vars),
        style='LargeBold.TLabel',
    )

    variable_names = _filter_uncertainty_variables(variable_names)

    # Create comboboxes for each x variable
    x_vars = []
    x_combos = []
    for i in range(num_vars):
        x_var = StringVar()
        if i == 0:
            x_var.set(first_x_name)  # First one is already selected
        x_vars.append(x_var)
        
        label = ttk.Label(
            call_var_level.frame_custom,
            text=t('dialog.independent_variable_index', index=i + 1, index_minus=i),
        )
        combo = ttk.Combobox(
            call_var_level.frame_custom,
            textvariable=x_var,
            values=variable_names,
            state='readonly',
            width=UI_STYLE['spinbox_width'],
            font=get_entry_font(),
        )
        if variable_names and i == 0:
            try:
                combo.current(variable_names.index(first_x_name))
            except ValueError:
                combo.current(0)
        elif variable_names:
            combo.current(min(i, len(variable_names) - 1))
        
        x_combos.append((label, combo))

    call_var_level.accept_button = ttk.Button(
        call_var_level.frame_custom,
        text=t('dialog.accept'),
        command=call_var_level.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )

    call_var_level.frame_custom.grid(column=0, row=0)
    call_var_level.label_message.grid(
        column=0, row=0, columnspan=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )
    
    for i, (label, combo) in enumerate(x_combos):
        label.grid(
            column=0, row=i + 1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
        )
        combo.grid(
            column=1, row=i + 1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
        )
    
    call_var_level.accept_button.grid(
        column=1, row=num_vars + 1, padx=UI_STYLE['padding'], pady=UI_STYLE['padding']
    )

    bind_enter_to_accept([combo for _, combo in x_combos], call_var_level.destroy)
    apply_hover_to_children(call_var_level.frame_custom)
    if x_combos:
        x_combos[0][1].focus_set()
    call_var_level.resizable(False, False)
    parent_window.wait_window(call_var_level)

    if getattr(call_var_level, 'cancelled', False):
        return []
    
    result = [x_var.get() for x_var in x_vars]
    return result if all(result) else []


def _show_image_toplevel(parent: Tk | Toplevel, image_path: str, title: str) -> None:
    """
    Open a Toplevel window showing an image from file.

    Displays an image (e.g. pair plot) in a new window, scaled to fit within
    maximum dimensions. Handles preview PNG files for PDFs and cleans them up
    when the window is closed.

    Args:
        parent: Parent Tkinter window (``Tk`` or ``Toplevel``).
        image_path: Path to the image file to display (e.g., pair plot).
        title: Window title for the image display window.
    """
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

    label = ttk.Label(win, image=photo)
    label.image = photo
    label.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    close_btn = ttk.Button(
        win,
        text=t('dialog.accept'),
        command=_on_close,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )
    close_btn.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
    close_btn.focus_set()
    bind_enter_to_accept([close_btn, win], _on_close)
    win.protocol("WM_DELETE_WINDOW", _on_close)


def show_data_dialog(parent_window: Tk | Toplevel, data: Any) -> None:
    """
    Dialog to display loaded data.

    Args:
        parent_window: Parent Tkinter window (``Tk`` or ``Toplevel``).
        data: DataFrame to display (or string). If DataFrame, converted to
            string for display using ``to_string()`` method.
    """
    if hasattr(data, 'to_string'):
        content = data.to_string()
    else:
        content = str(data)

    watch_data_level = Toplevel()
    watch_data_level.title(t('dialog.show_data_title'))
    watch_data_level.configure(background=UI_STYLE['bg'])
    watch_data_level.minsize(800, 400)
    watch_data_level.resizable(False, False)

    # Data display area: fixed height in lines so only this part is limited; scroll for the rest
    _data_display_lines = 22
    text_frame = ttk.Frame(watch_data_level)
    text_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both')

    scrollbar_y = ttk.Scrollbar(text_frame, orient='vertical')
    scrollbar_y.pack(side='right', fill='y')
    scrollbar_x = ttk.Scrollbar(text_frame, orient='horizontal')
    scrollbar_x.pack(side='bottom', fill='x')

    text_widget = Text(
        text_frame,
        height=_data_display_lines,
        bg=UI_STYLE['text_bg'],
        fg=UI_STYLE['text_fg'],
        font=(UI_STYLE['text_font_family'], UI_STYLE['text_font_size']),
        wrap='none',
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set,
        relief='sunken',
        borderwidth=UI_STYLE['border_width'],
        padx=UI_STYLE['padding'],
        pady=UI_STYLE['padding'],
        insertbackground=UI_STYLE['text_insert_bg'],
        selectbackground=UI_STYLE['text_select_bg'],
        selectforeground=UI_STYLE['text_select_fg']
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

    opts_frame = ttk.Frame(watch_data_level)
    opts_frame.pack(padx=UI_STYLE['padding'], pady=4, fill='x')
    can_show_pairs = hasattr(data, 'columns') and len(getattr(data, 'columns', [])) > 0
    if can_show_pairs:
        pair_btn = ttk.Button(
            opts_frame,
            text=t('dialog.show_pair_plots'),
            command=_open_pair_plots_window,
            style='Primary.TButton',
            width=min(42, max(36, UI_STYLE['button_width_wide'] + 10)),
        )
        pair_btn.pack(anchor='w', pady=4)

    watch_data_level.accept_button = ttk.Button(
        watch_data_level,
        text=t('dialog.accept'),
        command=watch_data_level.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )
    watch_data_level.accept_button.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    bind_enter_to_accept(
        [text_widget, watch_data_level.accept_button],
        watch_data_level.destroy,
    )
    watch_data_level.accept_button.focus_set()
    parent_window.wait_window(watch_data_level)
