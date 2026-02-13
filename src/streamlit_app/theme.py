"""Streamlit UI theme from config (same rules as tkinter app).

Uses config.theme.UI_STYLE when available (env + theme.py). Converts color
names to hex for CSS via matplotlib. Fallback to config.env only if theme
cannot be imported (e.g. headless without tkinter).
"""

from typing import Any

from config import get_env_from_schema, lighten_hex, muted_from_hex

# Tk/X11 names that matplotlib may not recognize -> hex or matplotlib name
_TK_COLOR_ALIASES: dict[str, str] = {
    'lime green': 'limegreen',
    'red2': '#ee3b3b',
    'steel blue': 'steelblue',
    'gray40': '#666666',
}


def _color_to_hex(value: str) -> str:
    """Convert color (hex or name) to #rrggbb. No tkinter dependency."""
    if not value or not isinstance(value, str):
        return '#cccccc'
    raw = value.strip()
    if raw.startswith('#'):
        if len(raw) == 7 and all(c in '0123456789abcdefABCDEF' for c in raw[1:]):
            return raw
        if len(raw) == 4:
            return f'#{raw[1]*2}{raw[2]*2}{raw[3]*2}'
        return raw
    try:
        from matplotlib.colors import to_hex
        name = _TK_COLOR_ALIASES.get(raw.lower(), raw)
        return to_hex(name)
    except (ValueError, TypeError, ImportError):
        return _TK_COLOR_ALIASES.get(raw.lower(), '#cccccc')


def _theme_from_ui_style(style: dict[str, Any]) -> dict[str, Any]:
    """Build streamlit theme dict from config.theme.UI_STYLE (hex for CSS)."""
    fg_hex = _color_to_hex(style.get('fg', style.get('foreground', '#CCCCCC')))
    bg_hex = _color_to_hex(style.get('bg', style.get('background', '#181818')))
    return {
        'background': bg_hex,
        'sidebar_bg': lighten_hex(bg_hex, factor=0.08),
        'foreground': fg_hex,
        'muted': muted_from_hex(fg_hex),
        'button_bg': _color_to_hex(style.get('button_bg', '#1F1F1F')),
        'button_fg_primary': _color_to_hex(style.get('button_fg_accept', 'lime green')),
        'button_fg_cancel': _color_to_hex(style.get('button_fg_cancel', 'red2')),
        'accent2': _color_to_hex(style.get('button_fg_accent2', 'yellow')),
        'font_size': int(style.get('font_size', 18)),
        'font_family': str(style.get('font_family', 'Bahnschrift')),
        'padding': int(style.get('padding', style.get('padding_x', 8))),
    }


def _theme_from_env() -> dict[str, Any]:
    """Build streamlit theme dict from config.env only (fallback without theme.py)."""
    fg_hex = _color_to_hex(get_env_from_schema('UI_FOREGROUND'))
    bg_hex = _color_to_hex(get_env_from_schema('UI_BACKGROUND'))
    return {
        'background': bg_hex,
        'sidebar_bg': lighten_hex(bg_hex, factor=0.08),
        'foreground': fg_hex,
        'muted': muted_from_hex(fg_hex),
        'button_bg': _color_to_hex(get_env_from_schema('UI_BUTTON_BG')),
        'button_fg_primary': _color_to_hex(get_env_from_schema('UI_BUTTON_FG')),
        'button_fg_cancel': _color_to_hex(get_env_from_schema('UI_BUTTON_FG_CANCEL')),
        'accent2': _color_to_hex(get_env_from_schema('UI_BUTTON_FG_ACCENT2')),
        'font_size': int(get_env_from_schema('UI_FONT_SIZE')),
        'font_family': str(get_env_from_schema('UI_FONT_FAMILY')),
        'padding': int(get_env_from_schema('UI_PADDING')),
    }


def get_streamlit_theme() -> dict[str, Any]:
    """
    Theme dict from config: prefers config.theme.UI_STYLE (env + paths + theme),
    fallback to config.env when theme cannot be imported (e.g. headless).

    Returns dict with hex colors and font settings for Streamlit CSS.
    """
    try:
        from config import UI_STYLE
        return _theme_from_ui_style(UI_STYLE)
    except (ImportError, Exception):
        return _theme_from_env()


def get_main_css(theme: dict[str, Any]) -> str:
    """Generate global Streamlit CSS using theme (same visual rules as tkinter)."""
    bg = theme['background']
    sidebar_bg = theme.get('sidebar_bg', lighten_hex(bg, factor=0.08))
    fg = theme['foreground']
    primary = theme['button_fg_primary']
    accent2 = theme['accent2']
    btn_bg = theme['button_bg']
    ff = theme['font_family']
    pad = theme['padding']
    muted = theme.get('muted', muted_from_hex(fg))

    return f"""
    <style>
    /* Main app: same bg/fg as tkinter */
    .stApp {{
        background-color: {bg};
    }}
    [data-testid="stAppViewContainer"] {{
        background-color: {bg};
    }}
    [data-testid="stHeader"] {{
        background-color: {bg};
    }}
    p, span, label, .stMarkdown {{
        color: {fg};
    }}
    h1, h2, h3 {{
        color: {fg};
        font-family: {ff}, sans-serif;
    }}
    /* Sidebar: slightly lighter than main area */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}
    section[data-testid="stSidebar"] .stMarkdown {{
        color: {fg};
    }}
    /* Primary accent (headings, version badge) = button_fg_primary / accent2 */
    .sidebar-brand h2, .main-title {{
        color: {primary};
        font-family: {ff}, sans-serif;
    }}
    .version-badge {{
        background: linear-gradient(135deg, {primary} 0%, {accent2} 100%);
        color: {bg};
    }}
    .sidebar-section {{
        color: {muted};
    }}
    /* Buttons: same roles as tkinter Primary */
    .stButton > button {{
        background-color: {btn_bg};
        color: {primary};
        border-radius: 8px;
        font-weight: 500;
        padding: {pad}px 1rem;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }}
    [data-testid="stSidebar"] .stButton > button {{
        border-radius: 8px;
    }}
    </style>
    """
