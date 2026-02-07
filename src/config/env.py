"""Environment variable loading and .env schema."""

import os
from pathlib import Path
from typing import Any, Type, Union

# Type for env schema cast_type (str, int, float, bool)
_EnvCastType = Type[Union[str, int, float, bool]]

from config.constants import (
    LANGUAGE_ALIASES,
    SUPPORTED_LANGUAGE_CODES,
    VALID_LANGUAGE_INPUTS,
)

try:
    from dotenv import load_dotenv
    # Project root: __file__ is src/config/env.py -> parent=config, parent.parent=src, parent.parent.parent=project root
    _env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass


def _validate_env_value(
    key: str,
    value: Any,
    schema_item: dict[str, Any]
) -> tuple[bool, Any]:
    """
    Validate an environment variable value according to its schema.

    Args:
        key: Environment variable name.
        value: The value to validate (already cast to the correct type).
        schema_item: Schema item from ENV_SCHEMA containing validation rules.

    Returns:
        Tuple of (is_valid, corrected_value). If valid, corrected_value is the
        original value. If invalid, corrected_value is the default.
    """
    default = schema_item['default']
    cast_type = schema_item['cast_type']

    # Check if value is None
    if value is None:
        return False, default

    # Special validation for LANGUAGE
    if key == 'LANGUAGE' and cast_type == str:
        try:
            str_value = str(value).strip()
            lang_lower = str_value.lower()
            if lang_lower not in VALID_LANGUAGE_INPUTS:
                return False, default
            # Normalize to canonical code
            normalized = LANGUAGE_ALIASES.get(lang_lower, lang_lower)
            return True, normalized
        except (AttributeError, TypeError, ValueError):
            return False, default

    # Special validation for LOG_LEVEL
    if key == 'LOG_LEVEL' and cast_type == str:
        try:
            str_value = str(value).strip()
            if str_value.upper() not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
                return False, default
            return True, str_value.upper()
        except (AttributeError, TypeError, ValueError):
            return False, default

    # Validate options if specified
    if 'options' in schema_item:
        options = schema_item['options']
        try:
            if cast_type == str:
                if str(value).lower() not in [opt.lower() for opt in options]:
                    return False, default
            else:
                if value not in options:
                    return False, default
        except (AttributeError, TypeError, ValueError):
            return False, default

    # Validate integer ranges
    if cast_type == int:
        try:
            int_value = int(value)
        except (TypeError, ValueError, OverflowError):
            return False, default
            
        # Define validation rules for integer fields
        size_fields = {
            'UI_BORDER_WIDTH', 'UI_PADDING_X', 'UI_PADDING_Y',
            'UI_BUTTON_WIDTH', 'UI_BUTTON_WIDTH_WIDE',
            'UI_FONT_SIZE', 'UI_FONT_SIZE_LARGE',
            'UI_SPINBOX_WIDTH', 'UI_ENTRY_WIDTH',
            'UI_TEXT_FONT_SIZE',
            'PLOT_FIGSIZE_WIDTH', 'PLOT_FIGSIZE_HEIGHT',
            'PLOT_MARKER_SIZE',
            'FONT_AXIS_SIZE', 'FONT_TICK_SIZE'
        }
        
        if key in size_fields:
            # All size fields must be positive
            if int_value <= 0:
                return False, default
            
            # Apply specific upper bounds
            if 'FONT' in key or key.endswith('_SIZE'):
                if int_value > 200:
                    return False, default
            elif 'WIDTH' in key or 'HEIGHT' in key:
                if int_value > 1000:
                    return False, default
        
        # Special validation for DPI
        if key == 'DPI':
            if int_value < 50 or int_value > 1000:
                return False, default

    # Validate float ranges
    elif cast_type == float:
        try:
            float_value = float(value)
        except (TypeError, ValueError, OverflowError):
            return False, default
            
        # Validate line width
        if key == 'PLOT_LINE_WIDTH':
            if float_value <= 0 or float_value > 20:
                return False, default

    # Validate strings
    elif cast_type == str:
        try:
            str_value = str(value).strip()
        except (AttributeError, TypeError):
            return False, default
            
        # Optional fields that can be empty
        optional_fields = {'DONATIONS_URL'}
        
        # Require non-empty strings for all other fields
        if not str_value and key not in optional_fields:
            return False, default

    return True, value


def _was_value_corrected(
    key: str,
    current_value: Any,
    cast_type: _EnvCastType,
    schema_item: dict[str, Any]
) -> bool:
    """
    Check if an environment value was corrected during validation.

    Args:
        key: Environment variable name.
        current_value: The validated/corrected value.
        cast_type: Type to cast the value to.
        schema_item: Schema definition for this environment variable.

    Returns:
        True if the original value was invalid or different from current_value.
    """
    original_value = os.getenv(key)
    
    # If no original value exists, it wasn't corrected (just defaulted)
    if original_value is None:
        return False

    # Try to cast and validate the original value
    try:
        if cast_type == bool:
            original_casted = original_value.lower() in ('true', '1', 'yes')
        else:
            original_casted = cast_type(original_value)
    except (ValueError, TypeError):
        # Casting failed, so it was corrected
        return True

    # Check if validation would have failed or changed the value
    is_valid, validated_value = _validate_env_value(key, original_casted, schema_item)
    return not is_valid or validated_value != current_value


# Logging defaults (single source of truth for ENV_SCHEMA and utils.logger)
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_FILE = 'regressionlab.log'

ENV_SCHEMA: list[dict[str, Any]] = [
    {'key': 'LANGUAGE', 'default': 'es', 'cast_type': str, 'options': SUPPORTED_LANGUAGE_CODES},
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
    {'key': 'UI_TEXT_BG', 'default': 'gray15', 'cast_type': str},
    {'key': 'UI_TEXT_FG', 'default': 'light cyan', 'cast_type': str},
    {'key': 'UI_TEXT_FONT_FAMILY', 'default': 'Consolas', 'cast_type': str},
    {'key': 'UI_TEXT_FONT_SIZE', 'default': 11, 'cast_type': int},
    {'key': 'UI_TEXT_INSERT_BG', 'default': 'spring green', 'cast_type': str},
    {'key': 'UI_TEXT_SELECT_BG', 'default': 'steel blue', 'cast_type': str},
    {'key': 'UI_TEXT_SELECT_FG', 'default': 'white', 'cast_type': str},
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
    {'key': 'FILE_INPUT_DIR', 'default': 'input', 'cast_type': str},
    {'key': 'FILE_OUTPUT_DIR', 'default': 'output', 'cast_type': str},
    {'key': 'FILE_FILENAME_TEMPLATE', 'default': 'fit_{}.png', 'cast_type': str},
    {'key': 'FILE_PLOT_FORMAT', 'default': 'png', 'cast_type': str, 'options': ('png', 'jpg', 'pdf')},
    {'key': 'DONATIONS_URL', 'default': '', 'cast_type': str},
    {'key': 'LOG_LEVEL', 'default': DEFAULT_LOG_LEVEL, 'cast_type': str, 'options': ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')},
    {'key': 'LOG_FILE', 'default': DEFAULT_LOG_FILE, 'cast_type': str},
    {'key': 'LOG_CONSOLE', 'default': False, 'cast_type': bool},
]

# O(1) lookup by key for get_env and related functions
_ENV_SCHEMA_BY_KEY: dict[str, dict[str, Any]] = {item['key']: item for item in ENV_SCHEMA}


def get_env(
    key: str,
    default: Any,
    cast_type: Type[Union[str, int, float, bool]] = str
) -> Union[str, int, float, bool]:
    """
    Get environment variable with type casting, validation, and default value.

    This function validates the value according to ENV_SCHEMA rules. If validation
    fails, the default value is returned.

    Args:
        key: Environment variable name.
        default: Default value if variable not found or invalid.
        cast_type: Type to cast the value to (str, int, float, bool).

    Returns:
        The environment variable value cast to the specified type, validated,
        or default if invalid or missing.
    """
    value = os.getenv(key)
    if value is None:
        return default

    schema_item = _ENV_SCHEMA_BY_KEY.get(key)

    # If no schema found, use basic casting without validation
    if schema_item is None:
        try:
            if cast_type == bool:
                return value.lower() in ('true', '1', 'yes')
            return cast_type(value)
        except (ValueError, TypeError):
            return default

    # Cast the value first
    try:
        if cast_type == bool:
            casted_value = value.lower() in ('true', '1', 'yes')
        else:
            casted_value = cast_type(value)
    except (ValueError, TypeError):
        return default

    # Validate the casted value
    _, corrected_value = _validate_env_value(key, casted_value, schema_item)
    return corrected_value


def validate_all_env_values() -> dict[str, tuple[Any, bool]]:
    """
    Validate all environment values according to ENV_SCHEMA and return
    validation results.

    This function checks all environment variables defined in ENV_SCHEMA,
    validates them, and returns information about which values were corrected.

    Returns:
        Dictionary mapping environment keys to tuples of (corrected_value, was_corrected).
        was_corrected is True if the value was invalid and had to be corrected.

    Example:
        >>> results = validate_all_env_values()
        >>> results["LANGUAGE"]
        ('es', False)  # Value was valid
        >>> results["DPI"]
        (100, True)  # Value was invalid and corrected to default
    """
    results: dict[str, tuple[Any, bool]] = {}
    
    for item in ENV_SCHEMA:
        key = item['key']
        default = item['default']
        cast_type = item['cast_type']

        # Get validated current value
        current_value = get_env(key, default, cast_type)

        # Determine if the original value was corrected
        was_corrected = _was_value_corrected(key, current_value, cast_type, item)
        
        results[key] = (current_value, was_corrected)

    return results


def get_current_env_values() -> dict[str, str]:
    """
    Collect current environment values for all keys defined in ``ENV_SCHEMA``.

    Values are read using :func:`get_env` so casting, defaults and boolean
    handling are applied consistently. Booleans are converted to the strings
    ``"true"`` or ``"false"`` so they can be written back to ``.env`` files
    without ambiguity.

    Returns:
        Dictionary mapping environment keys to their string representation.

    Example:
        >>> values = get_current_env_values()
        >>> values["LANGUAGE"]
        'es'
    """
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
    """
    Write a ``.env`` file with the given key=value pairs.

    Only keys present in :data:`ENV_SCHEMA` are written, and values are quoted
    when they contain spaces, ``#`` or line breaks so they remain parseable by
    ``dotenv`` and similar tools.

    Args:
        env_path: Destination path for the ``.env`` file.
        values: Mapping from environment keys to their desired string values.

    Example:
        >>> from pathlib import Path
        >>> write_env_file(Path(".env"), {"LANGUAGE": "en", "LOG_LEVEL": "DEBUG"})
    """
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


def initialize_and_validate_config() -> None:
    """
    Initialize configuration and validate all environment values.

    This function should be called at application startup to ensure all
    configuration values are valid. Invalid values are automatically corrected
    to their defaults, and warnings are logged if any corrections were made.

    Example:
        >>> initialize_and_validate_config()
        # All config values are now validated and corrected if needed
    """
    try:
        from utils import get_logger
        logger = get_logger(__name__)
    except ImportError:
        # Logger not available, skip logging
        logger = None

    validation_results = validate_all_env_values()
    corrected_keys = [key for key, (_, was_corrected) in validation_results.items() if was_corrected]

    if corrected_keys and logger:
        logger.warning(
            f"Found {len(corrected_keys)} invalid environment variable(s) that were corrected to defaults: "
            f"{', '.join(corrected_keys)}"
        )
        for key in corrected_keys:
            original = os.getenv(key, '<missing>')
            corrected = validation_results[key][0]
            logger.info(f"  {key}: '{original}' -> '{corrected}' (default)")


DONATIONS_URL = get_env('DONATIONS_URL', '').strip()
