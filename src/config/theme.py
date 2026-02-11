"""UI theme, plot style, and font configuration.

All UI appearance is controlled by a single set of env vars. Fonts, sizes,
colors, relief and spacing are unified for consistency. Values are read from
ENV_SCHEMA in config.env (single source of truth for defaults and types).
"""

from typing import Any

from config.env import get_env_from_schema

# Optional tkinter imports (for desktop GUI only, not available in headless environments)
try:
    import tkinter
    import tkinter.font as tkfont
    from tkinter import ttk
    _TKINTER_AVAILABLE = True
except ImportError:
    tkinter = None
    tkfont = None
    ttk = None
    _TKINTER_AVAILABLE = False

# Fallback UI font families if the configured font is not available on this OS
_UI_FONT_FALLBACKS = ('Bahnschrift', 'SF Pro Text', 'Inter')

# -----------------------------------------------------------------------------
# Color conversion helpers (work with or without tkinter)
# -----------------------------------------------------------------------------

def _color_name_to_rgb(color: str) -> tuple[int, int, int] | None:
    """Convert color name to RGB tuple (0-255 range). Works with or without tkinter.
    
    Args:
        color: Color name (e.g., 'navy', 'gray15') or hex string
        
    Returns:
        Tuple of (r, g, b) in 0-255 range, or None if conversion fails
    """
    if not isinstance(color, str) or not color.strip():
        return None
    
    color = color.strip()
    
    # If it's already hex, parse it directly
    if color.startswith('#'):
        try:
            hex_color = color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            elif len(hex_color) == 3:
                r = int(hex_color[0] * 2, 16)
                g = int(hex_color[1] * 2, 16)
                b = int(hex_color[2] * 2, 16)
                return (r, g, b)
        except ValueError:
            pass
    
    # Try tkinter first (if available)
    if _TKINTER_AVAILABLE:
        try:
            root = tkinter.Tk()
            root.withdraw()
            r, g, b = root.winfo_rgb(color)
            root.destroy()
            # winfo_rgb returns 0..65535, convert to 0..255
            return (r // 256, g // 256, b // 256)
        except (tkinter.TclError, Exception):
            pass
    
    # Fallback to matplotlib
    try:
        from matplotlib.colors import to_rgb
        r, g, b = to_rgb(color)
        return (int(r * 255), int(g * 255), int(b * 255))
    except (ValueError, TypeError, ImportError):
        pass
    
    return None


# -----------------------------------------------------------------------------
# Single source: ENV_SCHEMA (env.py) + derived constants (same default look)
# -----------------------------------------------------------------------------

def _darken_bg(color: str) -> str:
    """Return a slightly darker shade for backgrounds (button active, widget hover).
    
    Uses algorithmic color transformation instead of lookup tables.
    
    Args:
        color: Named color string (e.g., 'navy', 'gray15')
        
    Returns:
        Darker shade as hex color string
    """
    rgb = _color_name_to_rgb(color)
    if rgb is None:
        return '#1e1e1e'
    
    r, g, b = rgb
    # Darken by reducing each channel by 15%
    factor = 0.85
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    
    return f'#{r:02x}{g:02x}{b:02x}'


def _lighten_fg(color: str) -> str:
    """Return a slightly lighter shade for foreground (button text when active/pressed).
    
    Uses algorithmic color transformation instead of lookup tables.
    
    Args:
        color: Named color string (e.g., 'snow', 'lime green')
        
    Returns:
        Lighter shade as hex color string
    """
    rgb = _color_name_to_rgb(color)
    if rgb is None:
        return '#ffffff'
    
    r, g, b = rgb
    # Lighten by moving 20% toward white
    factor = 0.20
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    
    return f'#{r:02x}{g:02x}{b:02x}'


def _tooltip_bg_from_ui(ui_bg: str) -> str:
    """Convert UI background to tooltip background: more grayish and slightly lighter.
    
    Uses algorithmic color transformation to desaturate and lighten.
    
    Args:
        ui_bg: UI background color name
        
    Returns:
        Tooltip background as hex color string
    """
    rgb = _color_name_to_rgb(ui_bg)
    if rgb is None:
        return '#4d4d4d'
    
    r, g, b = rgb
    # Desaturate by moving toward average (grayscale) by 60%
    avg = (r + g + b) // 3
    desat_factor = 0.60
    r = int(r + (avg - r) * desat_factor)
    g = int(g + (avg - g) * desat_factor)
    b = int(b + (avg - b) * desat_factor)
    
    # Then lighten by moving 25% toward white
    lighten_factor = 0.25
    r = min(255, int(r + (255 - r) * lighten_factor))
    g = min(255, int(g + (255 - g) * lighten_factor))
    b = min(255, int(b + (255 - b) * lighten_factor))
    
    return f'#{r:02x}{g:02x}{b:02x}'


def _lighten_bg_hex(color: str, factor: float = 0.06) -> str:
    """Return a very slightly lighter shade of color as #rrggbb, calculated from RGB."""
    rgb = _color_name_to_rgb(color)
    if rgb is None:
        return '#2e2e2e'
    
    r, g, b = rgb
    # Move each channel slightly toward white
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f'#{r:02x}{g:02x}{b:02x}'


# Colors (only main knobs; rest derived where used)
_bg = get_env_from_schema('UI_BACKGROUND')
_fg = get_env_from_schema('UI_FOREGROUND')
_btn_bg = get_env_from_schema('UI_BUTTON_BG')
_btn_fg_primary = get_env_from_schema('UI_BUTTON_FG')
_btn_fg_cancel = get_env_from_schema('UI_BUTTON_FG_CANCEL')
_btn_fg_accent2 = get_env_from_schema('UI_BUTTON_FG_ACCENT2')
_text_select_bg = get_env_from_schema('UI_TEXT_SELECT_BG')

# Layout and sizes (fixed or derived)
_border = 8
_relief = 'raised'
_padding = get_env_from_schema('UI_PADDING')
_btn_w = get_env_from_schema('UI_BUTTON_WIDTH')
_btn_wide = int(2.5 * _btn_w)
_spin_w = get_env_from_schema('UI_SPINBOX_WIDTH')
_entry_w = get_env_from_schema('UI_ENTRY_WIDTH')


def _resolve_ui_font_family(preferred: str) -> str:
    """Resolve UI font family: if preferred is not available on this OS, try fallbacks.

    Uses tkinter font.families() if available, otherwise falls back to matplotlib font manager.
    The preferred font is matched exactly (case-insensitive) or as a prefix of a system name
    (e.g. "Palatino" matches "Palatino Linotype" on Windows). Fallbacks use exact match only.

    Returns the first available of: preferred (or a system family that starts with it),
    Bahnschrift, SF Pro Text, Inter; otherwise the preferred string as-is.
    """
    if not (preferred and preferred.strip()):
        preferred = 'sans-serif'
    
    preferred_clean = preferred.strip()
    preferred_lower = preferred_clean.lower()
    available: dict[str, str] = {}
    
    # Try tkinter first (if available)
    if _TKINTER_AVAILABLE:
        try:
            root = tkinter.Tk()
            root.withdraw()
            # Map lowercase name -> actual name as returned by the system
            available = {f.lower(): f for f in tkfont.families()}
            root.destroy()
        except (tkinter.TclError, Exception):
            pass
    
    # Fallback to matplotlib font manager if tkinter not available or failed
    if not available:
        try:
            from matplotlib.font_manager import FontManager
            fm = FontManager()
            # Get all font families
            font_families = set()
            for font in fm.ttflist:
                if font.name:
                    font_families.add(font.name)
            available = {f.lower(): f for f in font_families}
        except (ImportError, Exception):
            pass
    
    # If we still don't have font list, just return preferred
    if not available:
        return preferred_clean
    
    # Preferred: exact match or system name that starts with preferred
    if preferred_lower in available:
        return available[preferred_lower]
    for key, actual_name in available.items():
        # Space (e.g. "Menlo Regular") or hyphen (e.g. "Menlo-Regular") after preferred name
        if key.startswith(preferred_lower + ' ') or key.startswith(preferred_lower + '-'):
            return actual_name
    for key, actual_name in available.items():
        # Any family that starts with preferred name (e.g. "MenloMono" when preferred is "Menlo")
        if len(key) > len(preferred_lower) and key.startswith(preferred_lower):
            return actual_name
    # Fallbacks: exact match only
    for name in _UI_FONT_FALLBACKS:
        if name and name.lower() in available:
            return available[name.lower()]
    return preferred_clean


_font_family = _resolve_ui_font_family(get_env_from_schema('UI_FONT_FAMILY'))
_font_size = get_env_from_schema('UI_FONT_SIZE')
_font_size_large = int(1.25 * _font_size)

# -----------------------------------------------------------------------------
# UI_STYLE: single dict used everywhere (includes aliases for compatibility)
# -----------------------------------------------------------------------------

# Computed once for UI_STYLE (derived from base colors)
_active_bg = _darken_bg(_btn_bg)
_hover_bg = _darken_bg(_bg)
_text_bg = _darken_bg(_bg)
_tooltip_bg = _tooltip_bg_from_ui(_bg)
_field_bg = _lighten_bg_hex(_bg, factor=0.14)

UI_STYLE = {
    # Core colors
    'bg': _bg,
    'fg': _fg,
    'background': _bg,
    'foreground': _fg,
    'button_bg': _btn_bg,
    'active_bg': _active_bg,
    'button_fg_accept': _btn_fg_primary,
    'button_fg_cancel': _btn_fg_cancel,
    'button_fg_accent2': _btn_fg_accent2,
    # Entry/Combobox/Spinbox: very slightly lighter than main bg (calculated from _bg)
    'field_bg': _field_bg,
    # Hover/focus: element bg darkened (entry, combobox, check, radio use _bg)
    'widget_hover_bg': _hover_bg,
    'checkbutton_hover_bg': _hover_bg,
    'combobox_focus_bg': _hover_bg,
    # Text widget (cursor and text = UI foreground)
    'text_bg': _text_bg,
    'text_fg': _fg,
    'text_insert_bg': _fg,
    'text_select_bg': _text_select_bg,
    'text_select_fg': _fg,
    # Tooltip: UI bg grayish+lighter, text = UI fg
    'tooltip_bg': _tooltip_bg,
    'tooltip_fg': _fg,
    'tooltip_border': 'gray40',
    # Layout: fixed relief and border
    'relief': _relief,
    'border_width': _border,
    'button_relief': _relief,
    'button_borderwidth': max(1, min(_border, 4)),
    'padding': _padding,
    'padding_x': _padding,
    'padding_y': _padding,
    # Sizes (wide = 2.5*normal, font large = 1.25*normal)
    'button_width': _btn_w,
    'button_width_wide': _btn_wide,
    'spinbox_width': _spin_w,
    'entry_width': _entry_w,
    # Fonts
    'font_family': _font_family,
    'font_size': _font_size,
    'font_size_large': _font_size_large,
    'entry_fg': _bg,
    'text_font_family': _font_family,
    'text_font_size': _font_size,
    'entry_font_size': _font_size,
}

# Backward compatibility: UI_THEME is the same source
UI_THEME = UI_STYLE

# tk Spinbox options so it matches ttk Combobox (same field_bg, fg, font, relief).
# readonlybackground: needed so readonly state uses theme bg on Windows.
SPINBOX_STYLE: dict[str, Any] = {
    'bg': _field_bg,
    'fg': _fg,
    'readonlybackground': _field_bg,
    'font': (_font_family, _font_size),
    'relief': 'sunken',
    'bd': 2,
    'highlightthickness': 0,
    'insertbackground': _fg,
}

# -----------------------------------------------------------------------------
# Button style presets (tk widgets): same relief/border/font, color by role
# -----------------------------------------------------------------------------

def _tk_button_base() -> dict[str, Any]:
    base = {
        'relief': UI_STYLE['button_relief'],
        'bd': UI_STYLE['button_borderwidth'],
        'highlightthickness': 0,
        'activebackground': UI_STYLE['active_bg'],
        'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
    }
    return base

_BASE_BUTTON = _tk_button_base()

BUTTON_STYLE_PRIMARY = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['button_fg_accept'], 'activeforeground': _lighten_fg(UI_STYLE['button_fg_accept'])}
BUTTON_STYLE_SECONDARY = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['fg'], 'activeforeground': _lighten_fg(UI_STYLE['fg'])}
BUTTON_STYLE_DANGER = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['button_fg_cancel'], 'activeforeground': _lighten_fg(UI_STYLE['button_fg_cancel'])}
BUTTON_STYLE_ACCENT = {**_BASE_BUTTON, 'bg': UI_STYLE['button_bg'], 'fg': UI_STYLE['button_fg_accept'], 'activeforeground': _lighten_fg(UI_STYLE['button_fg_accept'])}

# -----------------------------------------------------------------------------
# Plot config (unchanged)
# -----------------------------------------------------------------------------

PLOT_CONFIG = {
    'figsize': (
        get_env_from_schema('PLOT_FIGSIZE_WIDTH'),
        get_env_from_schema('PLOT_FIGSIZE_HEIGHT'),
    ),
    'dpi': get_env_from_schema('DPI'),
    'show_title': get_env_from_schema('PLOT_SHOW_TITLE'),
    'line_color': get_env_from_schema('PLOT_LINE_COLOR'),
    'line_width': get_env_from_schema('PLOT_LINE_WIDTH'),
    'line_style': get_env_from_schema('PLOT_LINE_STYLE'),
    'marker_format': get_env_from_schema('PLOT_MARKER_FORMAT'),
    'marker_size': get_env_from_schema('PLOT_MARKER_SIZE'),
    'error_color': get_env_from_schema('PLOT_ERROR_COLOR'),
    'marker_face_color': get_env_from_schema('PLOT_MARKER_FACE_COLOR'),
    'marker_edge_color': get_env_from_schema('PLOT_MARKER_EDGE_COLOR'),
}

FONT_CONFIG = {
    'family': get_env_from_schema('FONT_FAMILY'),
    'title_size': get_env_from_schema('FONT_TITLE_SIZE'),
    'title_weight': get_env_from_schema('FONT_TITLE_WEIGHT'),
    'axis_size': get_env_from_schema('FONT_AXIS_SIZE'),
    'axis_style': get_env_from_schema('FONT_AXIS_STYLE'),
    'tick_size': get_env_from_schema('FONT_TICK_SIZE'),
}

_font_cache = None


def get_entry_font() -> tuple[str, int]:
    """
    Get font tuple for ttk Entry and Combobox widgets.

    Returns a font tuple unified with the UI base font configuration.

    Returns:
        Tuple of ``(font_family, font_size)`` from ``UI_STYLE`` configuration.
    """
    return (UI_STYLE['font_family'], UI_STYLE['font_size'])


def _edge_color(bg_color: str, lighter: bool) -> str:
    """
    Return a lighter or darker shade for 3D button highlight/shadow.

    Uses a lookup table to map background colors to appropriate edge colors
    for 3D button effects (highlight for lighter, shadow for darker).

    Args:
        bg_color: Background color name (e.g., ``'navy'``, ``'gray15'``).
        lighter: If ``True``, return lighter shade (highlight); if ``False``,
            darker (shadow).

    Returns:
        Color name string for the edge color (e.g., ``'steel blue'``, ``'gray12'``).
    """
    key = bg_color.lower() if isinstance(bg_color, str) else ''
    if lighter:
        m = {'midnight blue': 'steel blue', 'navy': 'steel blue', 'black': 'gray20', 'gray5': 'gray15', 'gray10': 'gray25', 'gray15': 'gray30', 'gray20': 'gray35'}
    else:
        m = {'midnight blue': 'midnight blue', 'navy': 'midnight blue', 'black': 'black', 'gray5': 'gray3', 'gray10': 'gray8', 'gray15': 'gray10', 'gray20': 'gray12'}
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
    field_bg = UI_STYLE['field_bg']
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

    # Focus highlight: same as active so keyboard-focused control is clearly visible
    focus_bg = UI_STYLE['active_bg']

    def _btn_style(name: str, fg_color: str) -> None:
        active_fg = _lighten_fg(fg_color)
        style.configure(name, background=btn_bg, foreground=fg_color, **btn_common)
        style.map(
            name,
            background=[
                ('active', focus_bg),
                ('pressed', focus_bg),
                ('focus', focus_bg),
            ],
            foreground=[
                ('active', active_fg),
                ('pressed', active_fg),
                ('focus', active_fg),
            ],
            lightcolor=[('pressed', btn_dark)],
            darkcolor=[('pressed', btn_light)],
        )

    _btn_style('TButton', fg)
    _btn_style('Primary.TButton', UI_STYLE['button_fg_accept'])
    _btn_style('Secondary.TButton', fg)
    _btn_style('Danger.TButton', UI_STYLE['button_fg_cancel'])
    _btn_style('Accent.TButton', UI_STYLE['button_fg_accept'])
    _btn_style('Equation.TButton', UI_STYLE['button_fg_accent2'])

    # Entry: same font as rest of UI; field slightly lighter than main bg
    style.configure(
        'TEntry',
        fieldbackground=field_bg,
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

    # Combobox: field slightly lighter than main bg
    style.configure(
        'TCombobox',
        fieldbackground=field_bg,
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
        fieldbackground=[('readonly', field_bg), ('focus', hover_bg)],
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

    # Radiobutton and Checkbutton: same font, hover and focus so current option is visible
    style.configure('TRadiobutton', background=bg, foreground=fg, font=font_normal)
    style.configure('TRadiobutton.Hover', background=hover_bg, foreground=fg, font=font_normal)
    style.map(
        'TRadiobutton',
        background=[('active', bg), ('focus', hover_bg)],
        foreground=[('active', fg), ('focus', fg)],
    )
    style.map(
        'TRadiobutton.Hover',
        background=[('active', hover_bg), ('focus', hover_bg)],
        foreground=[('active', fg), ('focus', fg)],
    )
    style.configure('TCheckbutton', background=bg, foreground=fg, font=font_normal)
    style.configure('TCheckbutton.Hover', background=hover_bg, foreground=fg, font=font_normal)
    style.map(
        'TCheckbutton',
        background=[('active', bg), ('focus', hover_bg)],
        foreground=[('active', fg), ('focus', fg)],
    )
    style.map(
        'TCheckbutton.Hover',
        background=[('active', hover_bg), ('focus', hover_bg)],
        foreground=[('active', fg), ('focus', fg)],
    )

    # Scrollbars
    style.configure('Vertical.TScrollbar', background=bg, troughcolor=bg, arrowcolor=fg)
    style.configure('Horizontal.TScrollbar', background=bg, troughcolor=bg, arrowcolor=fg)

    # Config dialog sections
    style.configure('ConfigSectionHeader.TFrame', background=btn_light)
    style.configure('ConfigSectionHeader.TLabel', background=btn_light, foreground=fg, font=font_bold)
    style.configure('ConfigSectionContent.TFrame', background=bg)
    font_desc = (fam, max(8, int(sz * 0.7)))
    style.configure('ConfigOptionDesc.TLabel', background=bg, foreground=fg, font=font_desc)


def apply_hover_to_children(parent: Any) -> None:
    """
    Bind hover highlight effects to ttk widgets under parent.

    Recursively applies hover effects (style changes on mouse enter/leave)
    to ttk Entry, Combobox, Checkbutton, and Radiobutton widgets within
    the parent widget hierarchy.

    Args:
        parent: Parent Tkinter widget to recursively search for children widgets.
    """
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

    Creates and caches font objects for matplotlib plot titles and axes
    from FONT_CONFIG. Subsequent calls return cached fonts.

    Returns:
        Tuple of ``(title_font, axis_font)`` font objects from ``FONT_CONFIG``.
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
