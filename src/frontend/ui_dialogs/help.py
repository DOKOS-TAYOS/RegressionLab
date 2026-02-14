"""Help dialog and text utilities for Tkinter display."""

import re
import webbrowser
from typing import Any, List, Tuple
from tkinter import Tk, Toplevel, Frame, Canvas, StringVar, ttk

from config import DONATIONS_URL, UI_STYLE, apply_hover_to_children
from frontend.keyboard_nav import bind_enter_to_accept
from frontend.window_utils import place_window_centered
from i18n import t


_HELP_COLLAPSED = '\u25b6'
_HELP_EXPANDED = '\u25bc'

# (section_key for header + t('help.section_*')), (content keys for body)
_HELP_SECTIONS: List[Tuple[str, List[str]]] = [
    ('objective', ['objective_title', 'objective_description']),
    (
        'advantages',
        ['advantages_title'] + [f'advantage_{i}' for i in range(1, 10)],
    ),
    (
        'fitting_modes',
        [
            'fitting_modes',
            'normal_fitting',
            'multiple_datasets',
            'checker_fitting',
            'total_fitting',
            'view_data',
            'loop_mode',
        ],
    ),
    (
        'view_data_options',
        [
            'view_data_options_title',
            'view_data_pair_plots',
            'view_data_transform',
            'view_data_clean',
            'view_data_save',
        ],
    ),
    ('custom_functions', ['custom_functions_title', 'custom_functions_how']),
    (
        'data_format',
        [
            'data_format_title',
            'data_format_named',
            'data_format_u_prefix',
            'data_format_non_negative',
        ],
    ),
    ('data_location', ['data_location', 'data_input', 'data_formats']),
    ('output_location', ['output_location', 'output_plots', 'output_logs']),
    ('updates', ['updates_title', 'updates_description', 'updates_configure']),
    (
        'stats',
        [
            'stats_title',
            'r_squared_desc',
            'r_squared_formula',
            'rmse_desc',
            'rmse_formula',
            'chi_squared_desc',
            'chi_squared_formula',
            'reduced_chi_squared_desc',
            'reduced_chi_squared_formula',
            'dof_desc',
            'dof_formula',
            'param_ci_95_desc',
            'param_ci_95_formula',
        ],
    ),
]


def remove_markdown_bold(text: str) -> str:
    """Remove Markdown bold markers (**) from text for Tkinter display.

    Only strips ** when the content between them has no asterisk, so
    exponentiation in code (e.g. ``x**2``) is preserved.

    Args:
        text: String that may contain Markdown bold markers.

    Returns:
        String with ``**...**`` removed (content preserved).
    """
    return re.sub(r'\*\*([^*]*)\*\*', r'\1', text)


def _help_section_content(content_keys: List[str]) -> str:
    """
    Build section body text from locale translation keys.

    Joins translated content from multiple locale keys, removing Markdown
    bold markers for Tkinter display.

    Args:
        content_keys: List of locale keys (e.g., ``['advantage_1', 'advantage_2']``).

    Returns:
        Formatted section body text with double newlines (``'\\n\\n'``) between items.
    """
    return '\n\n'.join(
        remove_markdown_bold(t(f'help.{k}')) for k in content_keys
    )


# Transform and clean option keys for the data view help (order matches UI)
# Excludes intro keys that repeat the section name
_VIEW_DATA_TRANSFORM_KEYS: List[str] = [
    'view_data_transform_fft',
    'view_data_transform_fft_magnitude',
    'view_data_transform_ifft',
    'view_data_transform_dct',
    'view_data_transform_idct',
    'view_data_transform_log',
    'view_data_transform_log10',
    'view_data_transform_exp',
    'view_data_transform_sqrt',
    'view_data_transform_square',
    'view_data_transform_standardize',
    'view_data_transform_normalize',
    'view_data_transform_hilbert',
    'view_data_transform_ihilbert',
    'view_data_transform_envelope',
    'view_data_transform_laplace',
    'view_data_transform_ilaplace',
    'view_data_transform_cepstrum',
    'view_data_transform_hadamard',
    'view_data_transform_ihadamard',
]
_VIEW_DATA_CLEAN_KEYS: List[str] = [
    'view_data_clean_drop_na',
    'view_data_clean_drop_duplicates',
    'view_data_clean_fill_na_mean',
    'view_data_clean_fill_na_median',
    'view_data_clean_fill_na_zero',
    'view_data_clean_remove_outliers_iqr',
    'view_data_clean_remove_outliers_zscore',
]


def show_data_view_help_dialog(parent_window: Tk | Toplevel) -> None:
    """
    Display help dialog for the Watch Data window (transform, clean, save options).

    Shows collapsible sections: pair plots, transform (with each option detailed),
    clean (with each option detailed), and save. Used when the user clicks Help
    in the data view.

    Args:
        parent_window: Parent Tkinter window (the data view Toplevel).
    """
    win = Toplevel(parent_window)
    win.title(t('dialog.help_title'))
    win.configure(background=UI_STYLE['bg'])
    win.transient(parent_window)
    win.protocol("WM_DELETE_WINDOW", win.destroy)

    place_window_centered(win, 900, 650, max_width_ratio=0.7, max_height_ratio=0.7)
    win.resizable(True, True)

    main_frame = ttk.Frame(win, padding=UI_STYLE['border_width'])
    main_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)

    hint_lbl = ttk.Label(
        main_frame,
        text=t('help.sections_hint'),
        justify='left',
    )
    hint_lbl.pack(anchor='w', padx=4, pady=(0, 6))

    canvas = Canvas(
        main_frame,
        bg=UI_STYLE['bg'],
        highlightthickness=0,
    )
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    inner = ttk.Frame(canvas)

    def _on_frame_configure(_event: Any) -> None:
        canvas.configure(scrollregion=canvas.bbox('all'))

    def _on_canvas_configure(event: Any) -> None:
        canvas.itemconfig(canvas_window, width=event.width)

    inner.bind('<Configure>', _on_frame_configure)
    canvas.bind('<Configure>', _on_canvas_configure)

    canvas_window = canvas.create_window((0, 0), window=inner, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

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

    content_labels: List[ttk.Label] = []
    first_section_ref: List[Tuple[Any, Any, int]] = []
    row_index = 0

    collapsible_sections: List[Tuple[str, List[str]]] = [
        ('view_data_pair_plots_header', ['view_data_pair_plots_body']),
        ('view_data_transform_header', _VIEW_DATA_TRANSFORM_KEYS),
        ('view_data_clean_header', _VIEW_DATA_CLEAN_KEYS),
        ('view_data_save_header', ['view_data_save_body']),
    ]

    for header_key, content_keys in collapsible_sections:
        header_frame = ttk.Frame(inner, style='ConfigSectionHeader.TFrame')
        header_frame.bind('<Enter>', lambda e: header_frame.configure(cursor='hand2'))
        header_frame.bind('<Leave>', lambda e: header_frame.configure(cursor=''))
        arrow_var = StringVar(value=_HELP_COLLAPSED)
        arrow_lbl = ttk.Label(
            header_frame,
            textvariable=arrow_var,
            style='ConfigSectionHeader.TLabel',
        )
        arrow_lbl.pack(side='left', padx=(10, 6), pady=8)
        header_text = remove_markdown_bold(t(f'help.{header_key}')).strip()
        title_lbl = ttk.Label(
            header_frame,
            text=header_text,
            style='ConfigSectionHeader.TLabel',
        )
        title_lbl.pack(side='left', pady=8)
        header_frame.grid(
            row=row_index,
            column=0,
            columnspan=2,
            sticky='ew',
            padx=0,
            pady=(14, 0),
        )
        row_index += 1

        content_wrapper = ttk.Frame(inner, style='ConfigSectionContent.TFrame')
        content_wrapper.grid(
            row=row_index,
            column=0,
            columnspan=2,
            sticky='ew',
            padx=0,
            pady=0,
        )
        content_wrapper.grid_remove()
        if not first_section_ref:
            first_section_ref.append((content_wrapper, arrow_var, row_index))
        row_index += 1

        accent_line = Frame(
            content_wrapper,
            width=4,
            bg=UI_STYLE['widget_hover_bg'],
            highlightthickness=0,
        )
        accent_line.pack(side='left', fill='y')
        accent_line.pack_propagate(False)
        section_frame = ttk.Frame(content_wrapper)
        section_frame.pack(
            side='left', fill='both', expand=True, padx=(6, 0), pady=(4, 12)
        )

        body_text = _help_section_content(content_keys)
        body_lbl = ttk.Label(
            section_frame,
            text=body_text,
            wraplength=700,
            justify='left',
        )
        body_lbl.pack(anchor='w', padx=4, pady=4)
        content_labels.append(body_lbl)

        def _make_toggle(
            content: ttk.Frame,
            arrow: StringVar,
            header_fr: ttk.Frame,
            arrow_label: ttk.Label,
            title_label: ttk.Label,
        ) -> None:
            def toggle() -> None:
                if content.winfo_viewable():
                    content.grid_remove()
                    arrow.set(_HELP_COLLAPSED)
                else:
                    content.grid()
                    arrow.set(_HELP_EXPANDED)
                win.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox('all'))
                win.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox('all')))

            for w in (header_fr, arrow_label, title_label):
                w.bind('<Button-1>', lambda e: toggle())

        _make_toggle(content_wrapper, arrow_var, header_frame, arrow_lbl, title_lbl)

    if first_section_ref:
        first_content, first_arrow, first_row = first_section_ref[0]
        first_content.grid(
            row=first_row,
            column=0,
            columnspan=2,
            sticky='ew',
            padx=0,
            pady=0,
        )
        first_arrow.set(_HELP_EXPANDED)

    inner.columnconfigure(0, weight=1)
    _bind_mousewheel_recursive(inner)
    apply_hover_to_children(inner)

    def _update_wraplength(_e: Any = None) -> None:
        w = inner.winfo_width()
        if w > 80:
            wrap = max(120, w - 48)
            for lbl in content_labels:
                lbl.configure(wraplength=wrap)

    inner.bind('<Configure>', _update_wraplength)

    button_frame = ttk.Frame(win)
    button_frame.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    accept_btn = ttk.Button(
        button_frame,
        text=t('dialog.accept'),
        command=win.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )
    accept_btn.pack(side='left')
    bind_enter_to_accept([accept_btn], win.destroy)
    win.bind("<Return>", lambda e: win.destroy())
    win.bind("<KP_Enter>", lambda e: win.destroy())
    accept_btn.focus_set()
    win.grab_set()
    win.update_idletasks()
    _update_wraplength()
    parent_window.wait_window(win)


def show_help_dialog(parent_window: Tk | Toplevel) -> None:
    """
    Display help and information dialog about the application.

    Shows information in collapsible sections (like the config dialog):
    objective, advantages, fitting modes, custom functions, data format,
    data location, output location, and statistics.

    Args:
        parent_window: Parent Tkinter window (``Tk`` or ``Toplevel``).
    """
    help_level = Toplevel()
    help_level.title(t('dialog.help_title'))
    help_level.configure(background=UI_STYLE['bg'])
    help_level.grab_set()
    help_level.protocol("WM_DELETE_WINDOW", help_level.destroy)
    help_level.resizable(width=False, height=False)
    place_window_centered(help_level, 900, 650, max_width_ratio=0.7, max_height_ratio=0.7)

    main_frame = ttk.Frame(help_level, padding=UI_STYLE['border_width'])
    main_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)

    hint_lbl = ttk.Label(
        main_frame,
        text=t('help.sections_hint'),
        justify='left',
    )
    hint_lbl.pack(anchor='w', padx=4, pady=(0, 6))

    canvas = Canvas(
        main_frame,
        bg=UI_STYLE['bg'],
        highlightthickness=0,
    )
    scrollbar = ttk.Scrollbar(
        main_frame, orient='vertical', command=canvas.yview
    )
    inner = ttk.Frame(canvas)

    def _on_frame_configure(_event: Any) -> None:
        canvas.configure(scrollregion=canvas.bbox('all'))

    def _on_canvas_configure(event: Any) -> None:
        canvas.itemconfig(canvas_window, width=event.width)

    inner.bind('<Configure>', _on_frame_configure)
    canvas.bind('<Configure>', _on_canvas_configure)

    canvas_window = canvas.create_window((0, 0), window=inner, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

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

    content_labels: List[ttk.Label] = []
    first_section_ref: List[Tuple[Any, Any, int]] = []
    row_index = 0

    for section_key, content_keys in _HELP_SECTIONS:
        header_frame = ttk.Frame(inner, style='ConfigSectionHeader.TFrame')
        header_frame.bind(
            '<Enter>', lambda e: header_frame.configure(cursor='hand2')
        )
        header_frame.bind('<Leave>', lambda e: header_frame.configure(cursor=''))
        arrow_var = StringVar(value=_HELP_COLLAPSED)
        arrow_lbl = ttk.Label(
            header_frame,
            textvariable=arrow_var,
            style='ConfigSectionHeader.TLabel',
        )
        arrow_lbl.pack(side='left', padx=(10, 6), pady=8)
        header_text = remove_markdown_bold(t(f'help.{content_keys[0]}')).strip()
        title_lbl = ttk.Label(
            header_frame,
            text=header_text,
            style='ConfigSectionHeader.TLabel',
        )
        title_lbl.pack(side='left', pady=8)
        header_frame.grid(
            row=row_index,
            column=0,
            columnspan=2,
            sticky='ew',
            padx=0,
            pady=(14, 0),
        )
        row_index += 1

        content_wrapper = ttk.Frame(
            inner, style='ConfigSectionContent.TFrame'
        )
        content_wrapper.grid(
            row=row_index,
            column=0,
            columnspan=2,
            sticky='ew',
            padx=0,
            pady=0,
        )
        content_wrapper.grid_remove()
        if not first_section_ref:
            first_section_ref.append((content_wrapper, arrow_var, row_index))
        row_index += 1

        accent_line = Frame(
            content_wrapper,
            width=4,
            bg=UI_STYLE['widget_hover_bg'],
            highlightthickness=0,
        )
        accent_line.pack(side='left', fill='y')
        accent_line.pack_propagate(False)
        section_frame = ttk.Frame(content_wrapper)
        section_frame.pack(
            side='left', fill='both', expand=True, padx=(6, 0), pady=(4, 12)
        )

        body_text = _help_section_content(content_keys[1:])
        body_lbl = ttk.Label(
            section_frame,
            text=body_text,
            wraplength=600,
            justify='left',
        )
        body_lbl.pack(anchor='w', padx=4, pady=4)
        content_labels.append(body_lbl)

        section_frame.columnconfigure(0, weight=1)

        def _make_toggle(
            content: ttk.Frame,
            arrow: StringVar,
            header_fr: ttk.Frame,
            arrow_label: ttk.Label,
            title_label: ttk.Label,
        ) -> None:
            def toggle() -> None:
                if content.winfo_viewable():
                    content.grid_remove()
                    arrow.set(_HELP_COLLAPSED)
                else:
                    content.grid()
                    arrow.set(_HELP_EXPANDED)
                help_level.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox('all'))
                help_level.after_idle(
                    lambda: canvas.configure(scrollregion=canvas.bbox('all'))
                )

            for w in (header_fr, arrow_label, title_label):
                w.bind('<Button-1>', lambda e: toggle())

        _make_toggle(
            content_wrapper, arrow_var, header_frame, arrow_lbl, title_lbl
        )

    if first_section_ref:
        first_content, first_arrow, first_row = first_section_ref[0]
        first_content.grid(
            row=first_row,
            column=0,
            columnspan=2,
            sticky='ew',
            padx=0,
            pady=0,
        )
        first_arrow.set(_HELP_EXPANDED)

    inner.columnconfigure(0, weight=1)
    _bind_mousewheel_recursive(inner)

    def _on_arrow_scroll(event: Any) -> str:
        if event.keysym == 'Up':
            canvas.yview_scroll(-3, 'units')
        elif event.keysym == 'Down':
            canvas.yview_scroll(3, 'units')
        return 'break'

    def _bind_arrow_scroll_recursive(widget: Any) -> None:
        widget.bind('<Up>', _on_arrow_scroll)
        widget.bind('<Down>', _on_arrow_scroll)
        for child in widget.winfo_children():
            _bind_arrow_scroll_recursive(child)

    canvas.bind('<Up>', _on_arrow_scroll)
    canvas.bind('<Down>', _on_arrow_scroll)
    _bind_arrow_scroll_recursive(inner)

    apply_hover_to_children(inner)

    def _update_help_wraplength(_e: Any = None) -> None:
        w = inner.winfo_width()
        if w > 80:
            wrap = max(120, w - 48)
            for lbl in content_labels:
                lbl.configure(wraplength=wrap)

    inner.bind('<Configure>', _update_help_wraplength)

    button_frame = ttk.Frame(help_level)
    button_frame.pack(padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])

    if DONATIONS_URL:
        donations_button = ttk.Button(
            button_frame,
            text=t('dialog.donations'),
            command=lambda: webbrowser.open(DONATIONS_URL),
            style='Primary.TButton',
            width=UI_STYLE['button_width_wide'],
        )
        donations_button.pack(side='left', padx=(0, UI_STYLE['padding']))

    accept_button = ttk.Button(
        button_frame,
        text=t('dialog.accept'),
        command=help_level.destroy,
        style='Primary.TButton',
        width=UI_STYLE['button_width'],
    )
    accept_button.pack(side='left')

    bind_enter_to_accept([accept_button], help_level.destroy)
    help_level.bind("<Return>", lambda e: help_level.destroy())
    help_level.bind("<KP_Enter>", lambda e: help_level.destroy())
    accept_button.focus_set()
    help_level.update_idletasks()
    _update_help_wraplength()
    parent_window.wait_window(help_level)
