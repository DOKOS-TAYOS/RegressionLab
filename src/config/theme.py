"""UI theme, plot style, and font configuration."""

from typing import Any

from config.env import get_env

UI_THEME = {
    'background': get_env('UI_BACKGROUND', 'midnight blue'),
    'foreground': get_env('UI_FOREGROUND', 'snow'),
    'button_fg': get_env('UI_BUTTON_FG', 'lime green'),
    'button_fg_cancel': get_env('UI_BUTTON_FG_CANCEL', 'red2'),
    'button_fg_cyan': get_env('UI_BUTTON_FG_CYAN', 'cyan2'),
    'active_bg': get_env('UI_ACTIVE_BG', 'navy'),
    'active_fg': get_env('UI_ACTIVE_FG', 'snow'),
    'border_width': get_env('UI_BORDER_WIDTH', 8, int),
    'relief': get_env('UI_RELIEF', 'ridge'),
    'button_relief': get_env('UI_BUTTON_RELIEF', 'ridge'),
    'button_borderwidth': get_env('UI_BUTTON_BORDERWIDTH', 2, int),
    'padding_x': get_env('UI_PADDING_X', 8, int),
    'padding_y': get_env('UI_PADDING_Y', 8, int),
    'button_width': get_env('UI_BUTTON_WIDTH', 12, int),
    'button_width_wide': get_env('UI_BUTTON_WIDTH_WIDE', 28, int),
    'font_size': get_env('UI_FONT_SIZE', 16, int),
    'font_size_large': get_env('UI_FONT_SIZE_LARGE', 20, int),
    'font_family': get_env('UI_FONT_FAMILY', 'Menlo'),
    'spinbox_width': get_env('UI_SPINBOX_WIDTH', 10, int),
    'entry_width': get_env('UI_ENTRY_WIDTH', 25, int),
    'text_bg': get_env('UI_TEXT_BG', 'gray15'),
    'text_fg': get_env('UI_TEXT_FG', 'light cyan'),
    'text_font_family': get_env('UI_TEXT_FONT_FAMILY', 'Consolas'),
    'text_font_size': get_env('UI_TEXT_FONT_SIZE', 11, int),
    'text_insert_bg': get_env('UI_TEXT_INSERT_BG', 'spring green'),
    'text_select_bg': get_env('UI_TEXT_SELECT_BG', 'steel blue'),
    'text_select_fg': get_env('UI_TEXT_SELECT_FG', 'white'),
}

UI_STYLE = {
    'bg': UI_THEME['background'],
    'fg': UI_THEME['foreground'],
    'button_fg_accept': UI_THEME['button_fg'],
    'button_fg_cancel': UI_THEME['button_fg_cancel'],
    'button_fg_cyan': UI_THEME['button_fg_cyan'],
    'active_bg': UI_THEME['active_bg'],
    'active_fg': UI_THEME['active_fg'],
    'entry_fg': UI_THEME['background'],
    'border_width': UI_THEME['border_width'],
    'button_relief': UI_THEME['button_relief'],
    'button_borderwidth': UI_THEME['button_borderwidth'],
    'button_width': UI_THEME['button_width'],
    'button_width_wide': UI_THEME['button_width_wide'],
    'padding': UI_THEME['padding_x'],
    'font_size': UI_THEME['font_size'],
    'font_size_large': UI_THEME['font_size_large'],
    'font_family': UI_THEME['font_family'],
    'spinbox_width': UI_THEME['spinbox_width'],
    'entry_width': UI_THEME['entry_width'],
    'text_bg': UI_THEME['text_bg'],
    'text_fg': UI_THEME['text_fg'],
    'text_font_family': UI_THEME['text_font_family'],
    'text_font_size': UI_THEME['text_font_size'],
    'text_insert_bg': UI_THEME['text_insert_bg'],
    'text_select_bg': UI_THEME['text_select_bg'],
    'text_select_fg': UI_THEME['text_select_fg'],
}

# Button style presets: borders and relief for visibility; different roles use different colors.
_BASE_BUTTON = {
    'relief': UI_STYLE['button_relief'],
    'bd': UI_STYLE['button_borderwidth'],
    'highlightthickness': 0,
    'activebackground': UI_STYLE['active_bg'],
    'activeforeground': UI_STYLE['active_fg'],
    'font': (UI_STYLE['font_family'], UI_STYLE['font_size']),
}
BUTTON_STYLE_PRIMARY = {
    **_BASE_BUTTON,
    'bg': UI_STYLE['bg'],
    'fg': UI_STYLE['button_fg_accept'],
}
BUTTON_STYLE_SECONDARY = {
    **_BASE_BUTTON,
    'bg': UI_STYLE['bg'],
    'fg': UI_STYLE['fg'],
}
BUTTON_STYLE_DANGER = {
    **_BASE_BUTTON,
    'bg': UI_STYLE['bg'],
    'fg': UI_STYLE['button_fg_cancel'],
}
BUTTON_STYLE_ACCENT = {
    **_BASE_BUTTON,
    'bg': UI_STYLE['bg'],
    'fg': UI_STYLE['button_fg_cyan'],
}

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


def setup_fonts() -> tuple[Any, Any]:
    """
    Configure and cache font properties for plot titles and axes.

    This function reads values from :data:`FONT_CONFIG`, builds the
    corresponding :class:`matplotlib.font_manager.FontProperties` objects
    and caches them so subsequent calls are inexpensive.

    If any font property is incompatible with Matplotlib, it falls back to
    safe defaults and logs a warning.

    Returns:
        Tuple ``(title_font, axis_font)`` with font properties for titles and axes.
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
    
    def _set_font_property(setter_method, value, property_name, default_value):
        """Set a font property with error handling; fall back to default on failure.

        Args:
            setter_method: Method to call to set the property (e.g. set_family).
            value: Value to set.
            property_name: Name of the property (for log messages).
            default_value: Fallback value if setting fails.
        """
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
    
    # Configure title font
    _set_font_property(fontt.set_family, FONT_CONFIG['family'], 'font family', 'serif')
    _set_font_property(fontt.set_size, FONT_CONFIG['title_size'], 'title size', 'xx-large')
    _set_font_property(fontt.set_weight, FONT_CONFIG['title_weight'], 'title weight', 'semibold')
    
    # Configure axis font
    _set_font_property(fonta.set_family, FONT_CONFIG['family'], 'font family', 'serif')
    _set_font_property(fonta.set_size, FONT_CONFIG['axis_size'], 'axis size', 30)
    _set_font_property(fonta.set_style, FONT_CONFIG['axis_style'], 'axis style', 'italic')
    
    _font_cache = (fontt, fonta)
    return _font_cache
