"""Equation and parameter dialogs for fitting."""

from typing import Any, Dict, List, Optional, Tuple
from tkinter import (
    Toplevel,
    Frame,
    Label,
    Button,
    Entry,
    StringVar,
    IntVar,
    BooleanVar,
    Spinbox,
    Checkbutton,
    Text,
)

from config import EQUATIONS, EXIT_SIGNAL, UI_STYLE
from i18n import t
from utils import parse_optional_float

from frontend.ui_dialogs.tooltip import bind_tooltip


UNICODE_PARAM_MAP: Dict[str, str] = {
    r"\u03B1": "α",
    r"\u03B2": "β",
    r"\u03B3": "γ",
    r"\u03B4": "δ",
    r"\u03B5": "ε",
    r"\u03B6": "ζ",
    r"\u03B7": "η",
    r"\u03B8": "θ",
    r"\u03BB": "λ",
    r"\u03BC": "μ",
    r"\u03BE": "ξ",
    r"\u03C0": "π",
    r"\u03C1": "ρ",
    r"\u03C3": "σ",
    r"\u03C6": "φ",
    r"\u03C9": "ω",
    r"\u0394": "Δ",
    r"\u03A3": "Σ",
    r"\u03A6": "Φ",
    r"\u03A9": "Ω",
}


def _normalize_unicode_text(text: str) -> str:
    """
    Replace explicit Unicode escape sequences like '\\u03B1' with their
    corresponding Greek letters in arbitrary text (names, formulas, etc.).
    """
    for code, char in UNICODE_PARAM_MAP.items():
        text = text.replace(code, char)
    return text


def _normalize_param_name(name: str) -> str:
    """
    Normalize parameter names replacing explicit Unicode escape sequences
    like '\\u03B1' with their corresponding Greek letters.
    """
    return _normalize_unicode_text(name.strip())


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
    from fitting import get_equation_param_info

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

        Label(frm, text=f"{t('dialog.equation')} {formula}", **lbl_style).grid(
            row=0, column=0, columnspan=5, padx=4, pady=(2, 8), sticky='w'
        )
        Label(frm, text=t('dialog.param_column_name'), **lbl_style).grid(row=1, column=0, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_initial'), **lbl_style).grid(row=1, column=1, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_range_start'), **lbl_style).grid(row=1, column=2, padx=4, pady=2)
        Label(frm, text=t('dialog.param_column_range_end'), **lbl_style).grid(row=1, column=3, padx=4, pady=2)

        initial_entries: List[Entry] = []
        lower_entries: List[Entry] = []
        upper_entries: List[Entry] = []

        for i, pname in enumerate(param_names):
            r = i + 2
            Label(frm, text=pname, **lbl_style).grid(row=r, column=0, padx=4, pady=2, sticky='w')
            e_init = Entry(frm, **entry_style)
            e_init.grid(row=r, column=1, padx=4, pady=2)
            initial_entries.append(e_init)
            e_lo = Entry(frm, **entry_style)
            e_lo.grid(row=r, column=2, padx=4, pady=2)
            lower_entries.append(e_lo)
            e_hi = Entry(frm, **entry_style)
            e_hi.grid(row=r, column=3, padx=4, pady=2)
            upper_entries.append(e_hi)

        def on_accept() -> None:
            initial_guess: List[Optional[float]] = [
                parse_optional_float(e.get()) for e in initial_entries
            ]
            lower_list: List[Optional[float]] = [
                parse_optional_float(e.get()) for e in lower_entries
            ]
            upper_list: List[Optional[float]] = [
                parse_optional_float(e.get()) for e in upper_entries
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
        btn_accept.grid(row=len(param_names) + 2, column=1, columnspan=2, padx=UI_STYLE['padding'], pady=UI_STYLE['padding'])
        param_dlg.resizable(True, False)
        equation_level.wait_window(param_dlg)

    def handle_equation_click(eq_type: str) -> None:
        equation_level.selected_equation = eq_type
        if not configure_params_var.get():
            equation_level.destroy()
            return
        _show_param_dialog(eq_type)
        equation_level.destroy()

    def handle_custom_click() -> None:
        equation_level.selected_equation = 'custom'
        equation_level.destroy()

    def handle_exit_click() -> None:
        equation_level.selected_equation = EXIT_SIGNAL
        equation_level.destroy()

    for attr_name in equation_keys:
        btn_text = t(f'equations.{attr_name}')
        desc = t(f'equations_descriptions.{attr_name}')
        formula = EQUATIONS.get(attr_name, {}).get("formula", "")
        tooltip_text = f"{desc}\n{t('dialog.equation')} {formula}" if formula else desc
        btn = Button(
            equation_level.frame_custom,
            text=btn_text,
            command=lambda eq_type=attr_name: handle_equation_click(eq_type),
            **btn_config
        )
        bind_tooltip(btn, tooltip_text)
        setattr(equation_level, attr_name, btn)

    equation_level.custom = Button(
        equation_level.frame_custom,
        text=t('equations.custom_formula'),
        command=handle_custom_click,
        **btn_config
    )

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
        to=12, # If you want more parameters, change this
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

    Returns:
        List of parameter names
    """
    cod1 = '\\u03B1=α, \\u03B2=β, \\u03B3=γ, \\u03B4=δ, \\u03B5=ε\n'
    cod2 = '\\u03B6=ζ, \\u03B7=η, \\u03B8=θ, \\u03BB=λ, \\u03BC=μ\n'
    cod3 = '\\u03BE=ξ, \\u03C0=π, \\u03C1=ρ, \\u03C3=σ, \\u03C6=φ\n'
    cod4 = '\\u03C9=ω, \\u0394=Δ, \\u03A3=Σ, \\u03A6=Φ, \\u03A9=Ω'
    cod = cod1 + cod2 + cod3 + cod4
    exit_instruction = f'\n"{t("dialog.exit_option")}" {t("dialog.exit_instruction")}'

    parameter_names_list: List[str] = []
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
            text=t('dialog.parameter_name', index=i + 1),
            bg=UI_STYLE['bg'],
            fg=UI_STYLE['fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
        )
        parameter_asker_leve.codes = Text(
            parameter_asker_leve.frame_custom,
            bg=UI_STYLE['bg'],
            fg=UI_STYLE['fg'],
            font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
            height=10,
            width=UI_STYLE['entry_width']*2,
            wrap='word',
            borderwidth=0,
            highlightthickness=0,
        )
        unicode_hint: str = t('dialog.custom_formula_unicode_hint')
        parameter_asker_leve.codes.insert('1.0', cod + exit_instruction + '\n\n' + unicode_hint)
        parameter_asker_leve.codes.config(state='disabled')
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
        raw_name: str = parameter_asker_leve.name_parame.get()
        if not raw_name.strip():
            return [EXIT_SIGNAL]
        parameter_names_list.append(_normalize_param_name(raw_name))

    return parameter_names_list


def ask_custom_formula(parent_window: Any, parameter_names: List[str]) -> str:
    """
    Dialog to ask for custom function formula.

    Returns:
        Formula entered by the user
    """
    cod1 = '\\u03B1=α, \\u03B2=β, \\u03B3=γ, \\u03B4=δ, \\u03B5=ε\n'
    cod2 = '\\u03B6=ζ, \\u03B7=η, \\u03B8=θ, \\u03BB=λ, \\u03BC=μ\n'
    cod3 = '\\u03BE=ξ, \\u03C0=π, \\u03C1=ρ, \\u03C3=σ, \\u03C6=φ\n'
    cod4 = '\\u03C9=ω, \\u0394=Δ, \\u03A3=Σ, \\u03A6=Φ, \\u03A9=Ω'
    cod = cod1 + cod2 + cod3 + cod4
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
    syntax_hint_text = (
        t('dialog.custom_formula_syntax_hint')
        + '\n'
        + t('dialog.custom_formula_unicode_hint')
        + '\n'
        + t('dialog.formula_example')
    )
    formulator_level.syntax_hint = Text(
        formulator_level.frame_custom,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
        height=3,
        width=UI_STYLE['entry_width'] + 10,
        wrap='word',
        borderwidth=0,
        highlightthickness=0,
    )
    formulator_level.syntax_hint.insert('1.0', syntax_hint_text)
    formulator_level.syntax_hint.config(state='disabled')
    formulator_level.message = Label(
        formulator_level.frame_custom,
        text='y(x)= ',
        width=8,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size'])
    )
    formulator_level.codes = Text(
        formulator_level.frame_custom,
        bg=UI_STYLE['bg'],
        fg=UI_STYLE['fg'],
        font=(UI_STYLE['font_family'], UI_STYLE['font_size']),
        height=8,
        width=UI_STYLE['entry_width'] + 10,
        wrap='word',
        borderwidth=0,
        highlightthickness=0,
    )
    formulator_level.codes.insert('1.0', cod + exit_instruction)
    formulator_level.codes.config(state='disabled')
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
    user_formula: str = _normalize_unicode_text(formulator_level.formule.get())
    return user_formula


def ask_num_fits(parent_window: Any, min_val: int = 2, max_val: int = 10) -> Optional[int]:
    """
    Dialog to ask for number of multiple fits.

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
