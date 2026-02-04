"""Environment variable loading and .env schema."""

import os
from pathlib import Path
from typing import Any, Type, Union

try:
    from dotenv import load_dotenv
    # Project root: __file__ is src/config/env.py -> parent=config, parent.parent=src, parent.parent.parent=project root
    _env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass


def get_env(
    key: str,
    default: Any,
    cast_type: Type[Union[str, int, float, bool]] = str
) -> Union[str, int, float, bool]:
    """
    Get environment variable with type casting and default value.

    Args:
        key: Environment variable name.
        default: Default value if variable not found.
        cast_type: Type to cast the value to (str, int, float, bool).

    Returns:
        The environment variable value cast to the specified type, or default.
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        if cast_type == bool:
            return value.lower() in ('true', '1', 'yes')
        return cast_type(value)
    except (ValueError, TypeError):
        return default


ENV_SCHEMA: list[dict[str, Any]] = [
    {'key': 'LANGUAGE', 'default': 'es', 'cast_type': str, 'options': ('es', 'en', 'de')},
    {'key': 'UI_BACKGROUND', 'default': 'midnight blue', 'cast_type': str},
    {'key': 'UI_FOREGROUND', 'default': 'snow', 'cast_type': str},
    {'key': 'UI_BUTTON_FG', 'default': 'lime green', 'cast_type': str},
    {'key': 'UI_BUTTON_FG_CANCEL', 'default': 'red2', 'cast_type': str},
    {'key': 'UI_BUTTON_FG_CYAN', 'default': 'cyan2', 'cast_type': str},
    {'key': 'UI_ACTIVE_BG', 'default': 'navy', 'cast_type': str},
    {'key': 'UI_ACTIVE_FG', 'default': 'snow', 'cast_type': str},
    {'key': 'UI_BORDER_WIDTH', 'default': 8, 'cast_type': int},
    {'key': 'UI_RELIEF', 'default': 'ridge', 'cast_type': str, 'options': ('flat', 'raised', 'sunken', 'groove', 'ridge')},
    {'key': 'UI_PADDING_X', 'default': 8, 'cast_type': int},
    {'key': 'UI_PADDING_Y', 'default': 8, 'cast_type': int},
    {'key': 'UI_BUTTON_WIDTH', 'default': 12, 'cast_type': int},
    {'key': 'UI_BUTTON_WIDTH_WIDE', 'default': 28, 'cast_type': int},
    {'key': 'UI_FONT_SIZE', 'default': 16, 'cast_type': int},
    {'key': 'UI_FONT_SIZE_LARGE', 'default': 20, 'cast_type': int},
    {'key': 'UI_FONT_FAMILY', 'default': 'Menlo', 'cast_type': str},
    {'key': 'UI_SPINBOX_WIDTH', 'default': 10, 'cast_type': int},
    {'key': 'UI_ENTRY_WIDTH', 'default': 25, 'cast_type': int},
    {'key': 'PLOT_FIGSIZE_WIDTH', 'default': 12, 'cast_type': int},
    {'key': 'PLOT_FIGSIZE_HEIGHT', 'default': 6, 'cast_type': int},
    {'key': 'DPI', 'default': 100, 'cast_type': int},
    {'key': 'PLOT_SHOW_TITLE', 'default': False, 'cast_type': bool},
    {'key': 'PLOT_LINE_COLOR', 'default': 'black', 'cast_type': str},
    {'key': 'PLOT_LINE_WIDTH', 'default': 1.0, 'cast_type': float},
    {'key': 'PLOT_LINE_STYLE', 'default': '-', 'cast_type': str, 'options': ('-', '--', '-.', ':')},
    {'key': 'PLOT_MARKER_FORMAT', 'default': 'o', 'cast_type': str, 'options': ('o', 's', '^', 'd', '*')},
    {'key': 'PLOT_MARKER_SIZE', 'default': 5, 'cast_type': int},
    {'key': 'PLOT_ERROR_COLOR', 'default': 'crimson', 'cast_type': str},
    {'key': 'PLOT_MARKER_FACE_COLOR', 'default': 'crimson', 'cast_type': str},
    {'key': 'PLOT_MARKER_EDGE_COLOR', 'default': 'crimson', 'cast_type': str},
    {'key': 'FONT_FAMILY', 'default': 'serif', 'cast_type': str, 'options': ('serif', 'sans-serif', 'monospace', 'cursive', 'fantasy')},
    {'key': 'FONT_TITLE_SIZE', 'default': 'xx-large', 'cast_type': str, 'options': ('xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large')},
    {'key': 'FONT_TITLE_WEIGHT', 'default': 'semibold', 'cast_type': str, 'options': ('normal', 'bold', 'light', 'semibold', 'heavy')},
    {'key': 'FONT_AXIS_SIZE', 'default': 30, 'cast_type': int},
    {'key': 'FONT_AXIS_STYLE', 'default': 'italic', 'cast_type': str, 'options': ('normal', 'italic', 'oblique')},
    {'key': 'FONT_TICK_SIZE', 'default': 16, 'cast_type': int},
    {'key': 'FONT_PARAM_FAMILY', 'default': 'Courier', 'cast_type': str},
    {'key': 'FONT_PARAM_SIZE', 'default': 10, 'cast_type': int},
    {'key': 'FILE_INPUT_DIR', 'default': 'input', 'cast_type': str},
    {'key': 'FILE_OUTPUT_DIR', 'default': 'output', 'cast_type': str},
    {'key': 'FILE_FILENAME_TEMPLATE', 'default': 'fit_{}.png', 'cast_type': str},
    {'key': 'FILE_PLOT_FORMAT', 'default': 'png', 'cast_type': str, 'options': ('png', 'jpg', 'pdf')},
    {'key': 'DONATIONS_URL', 'default': '', 'cast_type': str},
    {'key': 'LOG_LEVEL', 'default': 'INFO', 'cast_type': str, 'options': ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')},
    {'key': 'LOG_FILE', 'default': 'regressionlab.log', 'cast_type': str},
    {'key': 'LOG_CONSOLE', 'default': False, 'cast_type': bool},
]


def get_current_env_values() -> dict[str, str]:
    """Return current env values for all keys in ENV_SCHEMA."""
    result: dict[str, str] = {}
    for item in ENV_SCHEMA:
        key = item['key']
        default = item['default']
        cast_type = item['cast_type']
        val = get_env(key, default, cast_type)
        if cast_type == bool:
            result[key] = 'true' if val else 'false'
        else:
            result[key] = str(val)
    return result


def write_env_file(env_path: Path, values: dict[str, str]) -> None:
    """Write a .env file with the given key=value pairs. Only includes keys present in ENV_SCHEMA."""
    lines = [
        '# RegressionLab Configuration - generated by the application',
        '# Edit this file or use the configuration dialog from the main menu.',
        '',
    ]
    for item in ENV_SCHEMA:
        key = item['key']
        if key not in values:
            continue
        value = values[key].strip()
        if ' ' in value or '#' in value or '\n' in value:
            value = f'"{value}"'
        lines.append(f'{key}={value}')
    env_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


DONATIONS_URL = get_env('DONATIONS_URL', '').strip()
