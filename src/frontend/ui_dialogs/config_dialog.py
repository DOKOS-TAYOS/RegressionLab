"""Configuration dialog for editing .env settings."""

from typing import Any, List, Tuple, Union
from tkinter import (
    Toplevel,
    Frame,
    Label,
    Button,
    Entry,
    StringVar,
    BooleanVar,
    Canvas,
    Scrollbar,
    Checkbutton,
    ttk,
)

from config import (
    ENV_SCHEMA,
    UI_STYLE,
    get_current_env_values,
    get_project_root,
    write_env_file,
)
from i18n import t

_CONFIG_COLLAPSED = '\u25b6'
_CONFIG_EXPANDED = '\u25bc'


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


def _build_config_sections() -> List[Tuple[str, List[dict]]]:
    """Group ENV_SCHEMA items by section, preserving order of first occurrence."""
    order: List[str] = []
    sections_dict: dict[str, List[dict]] = {}
    for item in ENV_SCHEMA:
        section = _config_section_for_key(item['key'])
        if section not in sections_dict:
            sections_dict[section] = []
            order.append(section)
        sections_dict[section].append(item)
    return [(sec, sections_dict[sec]) for sec in order]


def show_config_dialog(parent_window: Any) -> bool:
    """
    Show configuration dialog to edit .env fields.
    Pre-fills with current env values (or defaults). On Accept, writes .env
    and returns True so the caller can restart the app. On Cancel returns False.

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
        if hasattr(event, 'delta') and event.delta != 0:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        elif event.num == 5:
            canvas.yview_scroll(1, 'units')
        elif event.num == 4:
            canvas.yview_scroll(-1, 'units')
        return 'break'

    def _bind_mousewheel_recursive(widget: Any) -> None:
        widget.bind('<MouseWheel>', _on_mousewheel)
        widget.bind('<Button-4>', _on_mousewheel)
        widget.bind('<Button-5>', _on_mousewheel)
        for child in widget.winfo_children():
            _bind_mousewheel_recursive(child)

    canvas.bind('<MouseWheel>', _on_mousewheel)
    canvas.bind('<Button-4>', _on_mousewheel)
    canvas.bind('<Button-5>', _on_mousewheel)
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
    config_desc_labels: List[Label] = []
    row_index = 0
    section_header_style = {
        'bg': UI_STYLE['bg'],
        'fg': UI_STYLE['fg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size'], 'bold'),
    }

    for section, section_items in _build_config_sections():
        header_frame = Frame(inner, bg=UI_STYLE['bg'], cursor='hand2')
        arrow_var = StringVar(value=_CONFIG_COLLAPSED)
        arrow_lbl = Label(header_frame, textvariable=arrow_var, **section_header_style)
        arrow_lbl.pack(side='left', padx=(0, 4))
        title_lbl = Label(header_frame, text=t(f'config.section_{section}'), **section_header_style)
        title_lbl.pack(side='left')
        header_frame.grid(row=row_index, column=0, columnspan=2, sticky='w', padx=4, pady=(12, 4))
        row_index += 1

        section_frame = Frame(inner, bg=UI_STYLE['bg'])
        section_frame.grid(row=row_index, column=0, columnspan=2, sticky='ew', padx=0, pady=0)
        section_frame.grid_remove()
        row_index += 1

        sub_row = 0
        for item in section_items:
            key = item['key']
            default = item['default']
            cast_type = item['cast_type']

            label_text = t(f'config.label_{key}')
            Label(section_frame, text=label_text, **lbl_style).grid(
                row=sub_row, column=0, sticky='w', padx=4, pady=2
            )
            desc_text = t(f'config.desc_{key}')
            desc_lbl = Label(
                section_frame, text=desc_text, **desc_style, wraplength=600, justify='left'
            )
            desc_lbl.grid(row=sub_row + 1, column=0, columnspan=2, sticky='w', padx=12, pady=(0, 6))
            config_desc_labels.append(desc_lbl)
            sub_row += 2

            if cast_type == bool:
                var = BooleanVar(value=current.get(key, 'false').lower() in ('true', '1', 'yes'))
                cb = Checkbutton(
                    section_frame, variable=var, **lbl_style, selectcolor=UI_STYLE['bg']
                )
                cb.grid(row=sub_row, column=0, columnspan=2, sticky='w', padx=4, pady=2)
                entries[key] = ('check', var)
            else:
                raw_val = current.get(key, str(default))
                opts = item.get('options')
                if opts:
                    opts_list = list(opts)
                    if raw_val in opts_list:
                        sv = StringVar(value=raw_val)
                    else:
                        normalized = (
                            str(raw_val).upper()
                            if key == 'LOG_LEVEL'
                            else str(raw_val).lower()
                        )
                        sv = StringVar(
                            value=normalized if normalized in opts_list else str(default)
                        )
                    combo = ttk.Combobox(
                        section_frame,
                        textvariable=sv,
                        values=opts_list,
                        state='readonly',
                        width=entry_style['width'],
                        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
                    )
                    combo.grid(row=sub_row, column=0, columnspan=2, sticky='ew', padx=4, pady=2)
                    entries[key] = ('entry', sv)
                else:
                    sv = StringVar(value=current.get(key, str(default)))
                    ent = Entry(section_frame, textvariable=sv, **entry_style)
                    ent.grid(row=sub_row, column=0, columnspan=2, sticky='ew', padx=4, pady=2)
                    entries[key] = ('entry', sv)
            sub_row += 1

        section_frame.columnconfigure(0, weight=1)

        def _make_toggle(
            content: Frame,
            arrow: StringVar,
            header_fr: Frame,
            arrow_label: Label,
            title_label: Label,
        ) -> None:
            def toggle() -> None:
                if content.winfo_viewable():
                    content.grid_remove()
                    arrow.set(_CONFIG_COLLAPSED)
                else:
                    content.grid()
                    arrow.set(_CONFIG_EXPANDED)
                config_level.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox('all'))
                config_level.after_idle(
                    lambda: canvas.configure(scrollregion=canvas.bbox('all'))
                )

            for w in (header_fr, arrow_label, title_label):
                w.bind('<Button-1>', lambda e: toggle())

        _make_toggle(section_frame, arrow_var, header_frame, arrow_lbl, title_lbl)

    inner.columnconfigure(0, weight=1)
    _bind_mousewheel_recursive(inner)

    def _update_config_wraplength(_e: Any = None) -> None:
        w = inner.winfo_width()
        if w > 80:
            wrap = max(120, w - 48)
            for lbl in config_desc_labels:
                lbl.configure(wraplength=wrap)

    inner.bind('<Configure>', _update_config_wraplength)

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
    config_level.update_idletasks()
    _update_config_wraplength()

    config_level.protocol('WM_DELETE_WINDOW', on_cancel)
    parent_window.wait_window(config_level)
    return result_var[0]
