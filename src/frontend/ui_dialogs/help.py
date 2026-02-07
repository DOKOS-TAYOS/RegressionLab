"""Help dialog and text utilities for Tkinter display."""

import re
import webbrowser
from tkinter import Tk, Toplevel, Frame, Button, Scrollbar, Text

from config import DONATIONS_URL, UI_STYLE
from i18n import t


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
        parent_window: Parent Tkinter window (Tk or Toplevel).

    Returns:
        None.
    """
    help_level = Toplevel()
    help_level.title(t('dialog.help_title'))
    help_level.configure(background=UI_STYLE['bg'])
    help_level.resizable(width=True, height=True)

    screen_width = help_level.winfo_screenwidth()
    screen_height = help_level.winfo_screenheight()
    dialog_width = min(900, int(screen_width * 0.7))
    dialog_height = min(650, int(screen_height * 0.7))
    offset_x = max(0, (screen_width - dialog_width) // 2)
    offset_y = max(0, (screen_height - dialog_height) // 2)
    help_level.geometry(f"{dialog_width}x{dialog_height}+{offset_x}+{offset_y}")

    main_frame = Frame(
        help_level,
        borderwidth=2,
        relief="raised",
        bg=UI_STYLE['bg'],
        bd=UI_STYLE['border_width']
    )
    main_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)

    text_frame = Frame(main_frame, bg=UI_STYLE['bg'])
    text_frame.pack(padx=UI_STYLE['padding'], pady=6, fill='both', expand=True)

    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side='right', fill='y')

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
    scrollbar.config(command=help_text.yview)

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

{remove_markdown_bold(t('help.custom_functions_title'))}
──────────────────────────────────────────────────

{remove_markdown_bold(t('help.custom_functions_how'))}

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

{remove_markdown_bold(t('help.rmse_desc'))}
{remove_markdown_bold(t('help.rmse_formula'))}

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
    help_text.insert('1.0', help_content)
    help_text.config(state='disabled')

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
