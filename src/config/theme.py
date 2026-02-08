"""UI theme, plot style, and font configuration.

All UI appearance is controlled by a single set of env vars. Fonts, sizes,
colors, relief and spacing are unified for consistency.
"""

import tkinter
from typing import Any

from tkinter import ttk

from config.env import get_env

# -----------------------------------------------------------------------------
# Single source: read only the unified env vars
# -----------------------------------------------------------------------------

# Colors: main palette
_UI_BG = get_env('UI_BACKGROUND', 'midnight blue')
_UI_FG = get_env('UI_FOREGROUND', 'snow')
_UI_BTN_BG = get_env('UI_BUTTON_BG', 'gray20')
_UI_ACTIVE_BG = get_env('UI_ACTIVE_BG', 'navy')
_UI_ACTIVE_FG = get_env('UI_ACTIVE_FG', 'snow')
# Button text colors (by role)
_UI_BTN_FG_PRIMARY = get_env('UI_BUTTON_FG', 'lime green')
_UI_BTN_FG_CANCEL = get_env('UI_BUTTON_FG_CANCEL', 'red2')
_UI_BTN_FG_ACCENT = get_env('UI_BUTTON_FG_CYAN', 'cyan2')
_UI_BTN_FG_ACCENT2 = get_env('UI_BUTTON_FG_ACCENT2', 'yellow')
# Hover/focus: one value for all widgets
_UI_HOVER_BG = get_env('UI_WIDGET_HOVER_BG', 'gray25')
# Text widget (data preview)
_UI_TEXT_BG = get_env('UI_TEXT_BG', 'gray15')
_UI_TEXT_FG = get_env('UI_TEXT_FG', 'light cyan')
_UI_TEXT_INSERT_BG = get_env('UI_TEXT_INSERT_BG', 'spring green')
_UI_TEXT_SELECT_BG = get_env('UI_TEXT_SELECT_BG', 'steel blue')
_UI_TEXT_SELECT_FG = get_env('UI_TEXT_SELECT_FG', 'white')
# Tooltip
_UI_TOOLTIP_BG = get_env('UI_TOOLTIP_BG', '#fffacd')
_UI_TOOLTIP_FG = get_env('UI_TOOLTIP_FG', 'black')
_UI_TOOLTIP_BORDER = get_env('UI_TOOLTIP_BORDER', 'gray40')

# Layout: unified relief and border for frames and buttons
_UI_RELIEF = get_env('UI_RELIEF', 'ridge')
_UI_BORDER = get_env('UI_BORDER_WIDTH', 8, int)
_UI_PADDING = get_env('UI_PADDING', 8, int)

# Sizes
_UI_BTN_W = get_env('UI_BUTTON_WIDTH', 12, int)
_UI_BTN_WIDE = get_env('UI_BUTTON_WIDTH_WIDE', 28, int)
_UI_SPIN_W = get_env('UI_SPINBOX_WIDTH', 10, int)
_UI_ENTRY_W = get_env('UI_ENTRY_WIDTH', 25, int)

# Fonts: one family, two sizes (base and large)
_UI_FONT_FAMILY = get_env('UI_FONT_FAMILY', 'Menlo')
_UI_FONT_SIZE = get_env('UI_FONT_SIZE', 16, int)
_UI_FONT_SIZE_LARGE = get_env('UI_FONT_SIZE_LARGE', 20, int)

# -----------------------------------------------------------------------------
# UI_STYLE: single dict used everywhere (includes aliases for compatibility)
# -----------------------------------------------------------------------------

UI_STYLE = {
    # Core colors
    'bg': _UI_BG,
    'fg': _UI_FG,
    'background': _UI_BG,
    'foreground': _UI_FG,
    'button_bg': _UI_BTN_BG,
    'active_bg': _UI_ACTIVE_BG,
    'active_fg': _UI_ACTIVE_FG,
    'button_fg_accept': _UI_BTN_FG_PRIMARY,
    'button_fg_cancel': _UI_BTN_FG_CANCEL,
    'button_fg_cyan': _UI_BTN_FG_ACCENT,
    'button_fg_accent2': _UI_BTN_FG_ACCENT2,
    # Hover/focus: same for entry, combobox, check, radio
    'widget_hover_bg': _UI_HOVER_BG,
    'checkbutton_hover_bg': _UI_HOVER_BG,
    'combobox_focus_bg': _UI_HOVER_BG,
    # Text widget
    'text_bg': _UI_TEXT_BG,
    'text_fg': _UI_TEXT_FG,
    'text_insert_bg': _UI_TEXT_INSERT_BG,
    'text_select_bg': _UI_TEXT_SELECT_BG,
    'text_select_fg': _UI_TEXT_SELECT_FG,
    # Tooltip
    'tooltip_bg': _UI_TOOLTIP_BG,
    'tooltip_fg': _UI_TOOLTIP_FG,
    'tooltip_border': _UI_TOOLTIP_BORDER,
    # Layout: one relief and border for all
    'relief': _UI_RELIEF,
    'border_width': _UI_BORDER,
    'button_relief': _UI_RELIEF,
    'button_borderwidth': max(1, min(_UI_BORDER, 4)),
    'padding': _UI_PADDING,
    'padding_x': _UI_PADDING,
    'padding_y': _UI_PADDING,
    # Sizes
    'button_width': _UI_BTN_W,
    'button_width_wide': _UI_BTN_WIDE,
    'spinbox_width': _UI_SPIN_W,
    'entry_width': _UI_ENTRY_W,
    # Fonts: unified (entry and text use base size)
    'font_family': _UI_FONT_FAMILY,
    'font_size': _UI_FONT_SIZE,
    'font_size_large': _UI_FONT_SIZE_LARGE,
    'entry_fg': _UI_BG,
    'text_font_family': _UI_FONT_FAMILY,
    'text_font_size': _UI_FONT_SIZE,
    'entry_font_size': _UI_FONT_SIZE,
}

# Backward compatibility: UI_THEME is the same source
UI_THEME = UI_STYLE

# -----------------------------------------------------------------------------
# Button style presets (tk widgets): same relief/border/font, color by role
# -----------------------------------------------------------------------------

_BASE_BUTTON = {
    'relief': UI_STYLE['button_relief'],
    'bd': UI_STYLE['button_borderwidth'],
    'highlightthickness': 0,
    'activebackground': UI_STYLE['active_bg'],
    'activeforeground': UI_STYLE['active_fg'],
    'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
}

BUTTON_STYLE_PRIMARY = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['button_fg_accept']}
BUTTON_STYLE_SECONDARY = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['fg']}
BUTTON_STYLE_DANGER = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['button_fg_cancel']}
BUTTON_STYLE_ACCENT = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['button_fg_cyan']}

# -----------------------------------------------------------------------------
# Plot config (unchanged)
# -----------------------------------------------------------------------------

PLOT_CONFIG = {
    'figsize': (
        get_env('PLOT_FIGSIZE_WIDTH', 12, int),
        get_env('PLOT_FIGSIZE_HEIGHT', 6, int)
    ),
    'dpi': get_env('DPI', 100, int),
    'show_title': get_env('PLOT_SHOW_TITLE', False, bool),
    'line_color': get_env('PLOT_LINE_COLOR', 'black'),
    'line_width': get_env('PLOT_LINE_WIDTH', 1.00, float),
    'line_style': get_env('PLOT_LINE_STYLE', '-'),
    'marker_format': get_env('PLOT_MARKER_FORMAT', 'o'),
    'marker_size': get_env('PLOT_MARKER_SIZE', 5, int),
    'error_color': get_env('PLOT_ERROR_COLOR', 'crimson'),
    'marker_face_color': get_env('PLOT_MARKER_FACE_COLOR', 'crimson'),
    'marker_edge_color': get_env('PLOT_MARKER_EDGE_COLOR', 'crimson'),
}

FONT_CONFIG = {
    'family': get_env('FONT_FAMILY', 'serif'),
    'title_size': get_env('FONT_TITLE_SIZE', 'xx-large'),
    'title_weight': get_env('FONT_TITLE_WEIGHT', 'semibold'),
    'axis_size': get_env('FONT_AXIS_SIZE', 30, int),
    'axis_style': get_env('FONT_AXIS_STYLE', 'italic'),
    'tick_size': get_env('FONT_TICK_SIZE', 16, int)
}

_font_cache = None


def get_entry_font() -> tuple[str, int]:
    """Font tuple for ttk Entry and Combobox (unified with UI base font)."""
    return (UI_STYLE['font_family'], UI_STYLE['font_size'])


def _edge_color(bg_color: str, lighter: bool) -> str:
    """Return a lighter or darker shade for 3D button highlight/shadow."""
    key = bg_color.lower() if isinstance(bg_color, str) else ''
    if lighter:
        m = {'midnight blue': 'steel blue', 'navy': 'steel blue', 'gray15': 'gray30', 'gray20': 'gray35'}
    else:
        m = {'midnight blue': 'midnight blue', 'navy': 'midnight blue', 'gray15': 'gray10', 'gray20': 'gray12'}
    return m.get(key, 'steel blue' if lighter else 'gray12')


def configure_ttk_styles(root: Any) -> None:
    """
    Configure ttk styles from the unified UI_STYLE. Call once after creating
    the Tk root. Uses 'clam' theme for consistent field colors.
    """
    style = ttk.Style(root)
    for theme_name in ('clam', 'alt', 'classic'):
        try:
            style.theme_use(theme_name)
            break
        except tkinter.TclError:
            continue

    fam = UI_STYLE['font_family']
    sz = UI_STYLE['font_size']
    sz_l = UI_STYLE['font_size_large']
    font_normal = (fam, sz)
    font_large = (fam, sz_l)
    font_bold = (fam, sz, 'bold')
    font_large_bold = (fam, sz_l, 'bold')

    bg = UI_STYLE['bg']
    fg = UI_STYLE['fg']
    btn_bg = UI_STYLE['button_bg']
    hover_bg = UI_STYLE['widget_hover_bg']
    btn_light = _edge_color(btn_bg, True)
    btn_dark = _edge_color(btn_bg, False)

    style.configure('TFrame', background=bg)
    style.configure('TLabel', background=bg, foreground=fg, font=font_normal)
    style.configure('Bold.TLabel', background=bg, foreground=fg, font=font_bold)
    style.configure('Large.TLabel', background=bg, foreground=fg, font=font_large)
    style.configure('LargeBold.TLabel', background=bg, foreground=fg, font=font_large_bold)
    style.configure(
        'Tooltip.TLabel',
        background=UI_STYLE['tooltip_bg'],
        foreground=UI_STYLE['tooltip_fg'],
        font=(fam, max(8, sz - 2)),
        padding=(6, 4),
    )
    style.configure('Raised.TFrame', background=btn_light)

    pad = (UI_STYLE['padding'], UI_STYLE['padding'])
    btn_common = {'font': font_normal, 'padding': pad, 'lightcolor': btn_light, 'darkcolor': btn_dark}

    def _btn_style(name: str, fg_color: str) -> None:
        style.configure(name, background=btn_bg, foreground=fg_color, **btn_common)
        style.map(
            name,
            background=[('active', UI_STYLE['active_bg']), ('pressed', UI_STYLE['active_bg'])],
            foreground=[('active', UI_STYLE['active_fg']), ('pressed', UI_STYLE['active_fg'])],
            lightcolor=[('pressed', btn_dark)],
            darkcolor=[('pressed', btn_light)],
        )

    _btn_style('TButton', fg)
    _btn_style('Primary.TButton', UI_STYLE['button_fg_accept'])
    _btn_style('Secondary.TButton', fg)
    _btn_style('Danger.TButton', UI_STYLE['button_fg_cancel'])
    _btn_style('Accent.TButton', UI_STYLE['button_fg_cyan'])
    _btn_style('Equation.TButton', UI_STYLE['button_fg_accent2'])

    # Entry: same font as rest of UI
    style.configure(
        'TEntry',
        fieldbackground=bg,
        foreground=fg,
        font=font_normal,
        padding=UI_STYLE['padding'],
    )
    style.configure(
        'TEntry.Hover',
        fieldbackground=hover_bg,
        foreground=fg,
        font=font_normal,
        padding=UI_STYLE['padding'],
    )

    # Combobox
    style.configure(
        'TCombobox',
        fieldbackground=bg,
        foreground=fg,
        background=bg,
        arrowcolor=fg,
        font=font_normal,
        padding=UI_STYLE['padding'],
    )
    style.configure(
        'TCombobox.Hover',
        fieldbackground=hover_bg,
        foreground=fg,
        background=bg,
        arrowcolor=fg,
        font=font_normal,
        padding=UI_STYLE['padding'],
    )
    style.map(
        'TCombobox',
        fieldbackground=[('readonly', bg), ('focus', hover_bg)],
        foreground=[('readonly', fg)],
        background=[('focus', bg)],
        arrowcolor=[('focus', fg), ('readonly', fg)],
    )
    style.map(
        'TCombobox.Hover',
        fieldbackground=[('readonly', hover_bg), ('focus', hover_bg)],
        foreground=[('readonly', fg)],
        background=[('focus', bg)],
        arrowcolor=[('focus', fg), ('readonly', fg)],
    )

    # Radiobutton and Checkbutton: same font and hover
    style.configure('TRadiobutton', background=bg, foreground=fg, font=font_normal)
    style.configure('TRadiobutton.Hover', background=hover_bg, foreground=fg, font=font_normal)
    style.map('TRadiobutton', background=[('active', bg)], foreground=[('active', fg)])
    style.map('TRadiobutton.Hover', background=[('active', hover_bg)], foreground=[('active', fg)])
    style.configure('TCheckbutton', background=bg, foreground=fg, font=font_normal)
    style.configure('TCheckbutton.Hover', background=hover_bg, foreground=fg, font=font_normal)
    style.map('TCheckbutton', background=[('active', bg)], foreground=[('active', fg)])
    style.map('TCheckbutton.Hover', background=[('active', hover_bg)], foreground=[('active', fg)])

    # Scrollbars
    style.configure('Vertical.TScrollbar', background=bg, troughcolor=bg, arrowcolor=fg)
    style.configure('Horizontal.TScrollbar', background=bg, troughcolor=bg, arrowcolor=fg)

    # Config dialog sections
    style.configure('ConfigSectionHeader.TFrame', background=btn_light)
    style.configure('ConfigSectionHeader.TLabel', background=btn_light, foreground=fg, font=font_bold)
    style.configure('ConfigSectionContent.TFrame', background=bg)


def apply_hover_to_children(parent: Any) -> None:
    """Bind hover highlight to ttk Entry, Combobox, Checkbutton, Radiobutton under parent."""
    for w in parent.winfo_children():
        apply_hover_to_children(w)
        cls = w.winfo_class()
        if cls not in ('TEntry', 'TCombobox', 'TCheckbutton', 'TRadiobutton'):
            continue
        hover_style = cls + '.Hover'
        normal_style = w.cget('style') or cls

        def _on_enter(ev: Any, widget: Any = w, norm: str = normal_style, hov: str = hover_style) -> None:
            widget.configure(style=hov)

        def _on_leave(ev: Any, widget: Any = w, norm: str = normal_style, hov: str = hover_style) -> None:
            widget.configure(style=norm)

        w.bind('<Enter>', _on_enter)
        w.bind('<Leave>', _on_leave)


def setup_fonts() -> tuple[Any, Any]:
    """
    Configure and cache font properties for plot titles and axes.
    Returns (title_font, axis_font) from FONT_CONFIG.
    """
    global _font_cache
    if _font_cache is not None:
        return _font_cache

    from matplotlib.font_manager import FontProperties

    try:
        from utils import get_logger
        logger = get_logger(__name__)
    except ImportError:
        logger = None

    def _set_font_property(setter_method: Any, value: Any, property_name: str, default_value: Any) -> None:
        try:
            setter_method(value)
        except (ValueError, KeyError) as e:
            if logger:
                logger.warning(
                    f"Invalid {property_name} '{value}': {e}. Using default '{default_value}'."
                )
            setter_method(default_value)

    font0 = FontProperties()
    fontt = font0.copy()
    fonta = font0.copy()

    _set_font_property(fontt.set_family, FONT_CONFIG['family'], 'font family', 'serif')
    _set_font_property(fontt.set_size, FONT_CONFIG['title_size'], 'title size', 'xx-large')
    _set_font_property(fontt.set_weight, FONT_CONFIG['title_weight'], 'title weight', 'semibold')
    _set_font_property(fonta.set_family, FONT_CONFIG['family'], 'font family', 'serif')
    _set_font_property(fonta.set_size, FONT_CONFIG['axis_size'], 'axis size', 30)
    _set_font_property(fonta.set_style, FONT_CONFIG['axis_style'], 'axis style', 'italic')

    _font_cache = (fontt, fonta)
    return _font_cache
