#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Central configuration file for the RegressionLab project.

This file consolidates all configuration settings for:

    - UI Theme and appearance
    - Plot styling and fonts
    - File paths and output directories
    - Environment variable loading

All modules should import configuration from this central file.
"""

# Standard library
import os
from pathlib import Path
from typing import Any, Optional, Type, Union

# Third-party packages
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# ============================================================================
# ENVIRONMENT VARIABLE LOADING
# ============================================================================


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


# ============================================================================
# UI THEME CONFIGURATION
# ============================================================================

UI_THEME = {
    # Window and widget colors
    'background': get_env('UI_BACKGROUND', 'midnight blue'),
    'foreground': get_env('UI_FOREGROUND', 'snow'),
    'button_fg': get_env('UI_BUTTON_FG', 'lime green'),
    'button_fg_cancel': get_env('UI_BUTTON_FG_CANCEL', 'red2'),
    'button_fg_cyan': get_env('UI_BUTTON_FG_CYAN', 'cyan2'),
    
    # Active (hover/click) colors
    'active_bg': get_env('UI_ACTIVE_BG', 'navy'),
    'active_fg': get_env('UI_ACTIVE_FG', 'snow'),
    
    # Border and spacing
    'border_width': get_env('UI_BORDER_WIDTH', 8, int),
    'relief': get_env('UI_RELIEF', 'ridge'),  # 'flat', 'raised', 'sunken', 'groove', 'ridge'
    'padding_x': get_env('UI_PADDING_X', 8, int),
    'padding_y': get_env('UI_PADDING_Y', 8, int),
    
    # Button properties
    'button_width': get_env('UI_BUTTON_WIDTH', 12, int),
    'button_width_wide': get_env('UI_BUTTON_WIDTH_WIDE', 28, int),
    
    # Font sizes for UI elements
    'font_size': get_env('UI_FONT_SIZE', 16, int),
    'font_size_large': get_env('UI_FONT_SIZE_LARGE', 20, int),
    'font_family': get_env('UI_FONT_FAMILY', 'Menlo'),
    
    # Widget sizes
    'spinbox_width': get_env('UI_SPINBOX_WIDTH', 10, int),
    'entry_width': get_env('UI_ENTRY_WIDTH', 25, int),
}


# UI_STYLE provides a convenient mapping for dialog components
# This maintains backwards compatibility while using the central theme configuration
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
    'button_width': UI_THEME['button_width'],
    'button_width_wide': UI_THEME['button_width_wide'],
    'padding': UI_THEME['padding_x'],
    'font_size': UI_THEME['font_size'],
    'font_size_large': UI_THEME['font_size_large'],
    'font_family': UI_THEME['font_family'],
    'spinbox_width': UI_THEME['spinbox_width'],
    'entry_width': UI_THEME['entry_width']
}


# ============================================================================
# PLOT STYLE CONFIGURATION
# ============================================================================

PLOT_CONFIG = {
    # Figure size (width, height) in inches
    'figsize': (
        get_env('PLOT_FIGSIZE_WIDTH', 12, int),
        get_env('PLOT_FIGSIZE_HEIGHT', 6, int)
    ),
    'dpi': get_env('DPI', 100, int),
    
    # Plot title settings
    'show_title': get_env('PLOT_SHOW_TITLE', False, bool),
    
    # Line properties for fitted curve
    'line_color': get_env('PLOT_LINE_COLOR', 'black'),
    'line_width': get_env('PLOT_LINE_WIDTH', 1.00, float),
    # '-' solid, '--' dashed, '-.' dash-dot, ':' dotted
    'line_style': get_env('PLOT_LINE_STYLE', '-'),
    
    # Marker properties for data points
    # 'o' circle, 's' square, '^' triangle, 'd' diamond
    'marker_format': get_env('PLOT_MARKER_FORMAT', 'o'),
    'marker_size': get_env('PLOT_MARKER_SIZE', 5, int),
    
    # Error bar and marker colors
    'error_color': get_env('PLOT_ERROR_COLOR', 'crimson'),
    'marker_face_color': get_env('PLOT_MARKER_FACE_COLOR', 'crimson'),
    'marker_edge_color': get_env('PLOT_MARKER_EDGE_COLOR', 'crimson'),
}


# ============================================================================
# FONT CONFIGURATION
# ============================================================================

FONT_CONFIG = {
    # Font family: 'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy'
    'family': get_env('FONT_FAMILY', 'serif'),
    
    # Title font properties
    # 'xx-small' through 'xx-large'
    'title_size': get_env('FONT_TITLE_SIZE', 'xx-large'),
    # 'normal', 'bold', 'light', 'semibold', 'heavy'
    'title_weight': get_env('FONT_TITLE_WEIGHT', 'semibold'),
    
    # Axis label font properties
    'axis_size': get_env('FONT_AXIS_SIZE', 30, int),
    'axis_style': get_env('FONT_AXIS_STYLE', 'italic'),  # 'normal', 'italic', 'oblique'
    
    # Tick label font properties (numbers on axes)
    'tick_size': get_env('FONT_TICK_SIZE', 16, int),
    
    # Parameter display font (family, size)
    'param_font': (
        get_env('FONT_PARAM_FAMILY', 'Courier'),
        get_env('FONT_PARAM_SIZE', 10, int)
    ),
}


# Cache for font properties to avoid recreating them on every plot
_font_cache = None


def setup_fonts() -> tuple:
    """
    Setup and return font properties for plots.
    Uses caching to avoid recreating fonts on every call.

    Returns:
        Tuple of (title_font, axis_font) FontProperties objects.
    """
    global _font_cache

    if _font_cache is not None:
        return _font_cache

    from matplotlib.font_manager import FontProperties

    font0 = FontProperties()
    fontt = font0.copy()
    fontt.set_family(FONT_CONFIG['family'])
    fontt.set_size(FONT_CONFIG['title_size'])
    fontt.set_weight(FONT_CONFIG['title_weight'])
    fonta = font0.copy()
    fonta.set_family(FONT_CONFIG['family'])
    fonta.set_size(FONT_CONFIG['axis_size'])
    fonta.set_style(FONT_CONFIG['axis_style'])
    _font_cache = (fontt, fonta)
    return _font_cache


# ============================================================================
# FILE PATH CONFIGURATION
# ============================================================================

# Allowed plot output formats (matplotlib savefig)
PLOT_FORMATS = ('png', 'jpg', 'jpeg', 'pdf')


def _normalize_plot_format(value: str) -> str:
    """Return a valid plot format extension (png, jpg, or pdf)."""
    v = (value or 'png').strip().lower()
    if v in ('jpg', 'jpeg'):
        return 'jpg'
    if v in ('png', 'pdf'):
        return v
    return 'png'


FILE_CONFIG = {
    # Input directory for data files (relative to project root)
    'input_dir': get_env('FILE_INPUT_DIR', 'input'),

    # Output directory for plots (relative to project root)
    'output_dir': get_env('FILE_OUTPUT_DIR', 'output'),
    
    # Filename template (use {} as placeholder for fit name)
    'filename_template': get_env('FILE_FILENAME_TEMPLATE', 'fit_{}.png'),
    
    # Plot output format: png, jpg, or pdf (used when building output path)
    'plot_format': _normalize_plot_format(get_env('FILE_PLOT_FORMAT', 'png')),
}


# ============================================================================
# EXTERNAL LINKS
# ============================================================================

# Donations URL shown in the Help window. If empty, the donations button is hidden.
DONATIONS_URL = get_env('DONATIONS_URL', '').strip()


# ============================================================================
# ENV SCHEMA FOR CONFIGURATION DIALOG
# ============================================================================

ENV_SCHEMA: list[dict[str, Any]] = [
    # Language
    {'key': 'LANGUAGE', 'default': 'es', 'cast_type': str, 'options': ('es', 'en', 'de')},
    # UI theme
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
    # Plot
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
    # Font (plots)
    {'key': 'FONT_FAMILY', 'default': 'serif', 'cast_type': str, 'options': ('serif', 'sans-serif', 'monospace', 'cursive', 'fantasy')},
    {'key': 'FONT_TITLE_SIZE', 'default': 'xx-large', 'cast_type': str, 'options': ('xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large')},
    {'key': 'FONT_TITLE_WEIGHT', 'default': 'semibold', 'cast_type': str, 'options': ('normal', 'bold', 'light', 'semibold', 'heavy')},
    {'key': 'FONT_AXIS_SIZE', 'default': 30, 'cast_type': int},
    {'key': 'FONT_AXIS_STYLE', 'default': 'italic', 'cast_type': str, 'options': ('normal', 'italic', 'oblique')},
    {'key': 'FONT_TICK_SIZE', 'default': 16, 'cast_type': int},
    {'key': 'FONT_PARAM_FAMILY', 'default': 'Courier', 'cast_type': str},
    {'key': 'FONT_PARAM_SIZE', 'default': 10, 'cast_type': int},
    # File paths and output format
    {'key': 'FILE_INPUT_DIR', 'default': 'input', 'cast_type': str},
    {'key': 'FILE_OUTPUT_DIR', 'default': 'output', 'cast_type': str},
    {'key': 'FILE_FILENAME_TEMPLATE', 'default': 'fit_{}.png', 'cast_type': str},
    {'key': 'FILE_PLOT_FORMAT', 'default': 'png', 'cast_type': str, 'options': ('png', 'jpg', 'pdf')},
    # Links
    {'key': 'DONATIONS_URL', 'default': '', 'cast_type': str},
    # Logging
    {'key': 'LOG_LEVEL', 'default': 'INFO', 'cast_type': str, 'options': ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')},
    {'key': 'LOG_FILE', 'default': 'regressionlab.log', 'cast_type': str},
    {'key': 'LOG_CONSOLE', 'default': False, 'cast_type': bool},
]


def get_current_env_values() -> dict[str, str]:
    """
    Return current env values for all keys in ENV_SCHEMA.
    Uses os.getenv so values already loaded from .env are used.
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
    Write a .env file with the given key=value pairs.
    Only includes keys present in ENV_SCHEMA.
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


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root (parent of src/)
    """
    return Path(__file__).parent.parent


def ensure_output_directory(output_dir: Optional[str] = None) -> str:
    """
    Create output directory if it doesn't exist.

    Args:
        output_dir: Optional directory path. If None, uses FILE_CONFIG['output_dir'].

    Returns:
        The output directory path (absolute path from project root).

    Raises:
        OSError: If directory cannot be created.
    """
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']

    project_root = get_project_root()
    full_path = project_root / output_dir

    try:
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Could not create output directory: {e!s}") from e

    return str(full_path)


def get_output_path(fit_name: str, output_dir: Optional[str] = None) -> str:
    """
    Get the full output path for a plot.

    The filename is built from the template; the extension is forced to
    the configured plot format (png, jpg, or pdf) so plots can be saved
    in the chosen format.

    Args:
        fit_name: Name of the fit/adjustment (used in filename).
        output_dir: Optional directory path. If None, uses FILE_CONFIG['output_dir'].

    Returns:
        Full path to the output file.
    """
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']
    
    # Ensure output directory exists and get absolute path
    output_path = ensure_output_directory(output_dir)
    
    # Create base filename from template, then apply configured format
    filename = FILE_CONFIG['filename_template'].format(fit_name)
    base, _ = os.path.splitext(filename)
    fmt = FILE_CONFIG.get('plot_format', 'png')
    filename = f"{base}.{fmt}"
    
    return os.path.join(output_path, filename)


# ============================================================================
# MATHEMATICAL FUNCTION MAPPINGS
# ============================================================================

MATH_FUNCTION_REPLACEMENTS = {
    r'\bln\b': 'np.log',
    r'\bsin\b': 'np.sin',
    r'\bcos\b': 'np.cos',
    r'\btan\b': 'np.tan',
    r'\bsinh\b': 'np.sinh',
    r'\bcosh\b': 'np.cosh',
    r'\btanh\b': 'np.tanh',
    r'\bexp\b': 'np.exp',
    r'\bsqrt\b': 'np.sqrt',
    r'\babs\b': 'np.abs',
    r'\bpi\b': 'np.pi',
    r'\be\b': 'np.e',
}
"""
Mathematical function replacements for custom function evaluation.

These regex patterns convert standard mathematical notation to NumPy functions.
For example: 'ln(x)' becomes 'np.log(x)', 'sin(x)' becomes 'np.sin(x)', etc.

You can extend this dictionary to support additional mathematical functions or notation.
"""

# Order: linear → polynomial/power → log → inverse → trig (sin/cos/tan) → hyperbolic → exp/logistic → special
EQUATION_FUNCTION_MAP = {
    'linear_function_with_n': 'fit_linear_function_with_n',
    'linear_function': 'fit_linear_function',
    'quadratic_function_complete': 'fit_quadratic_function_complete',
    'quadratic_function': 'fit_quadratic_function',
    'fourth_power': 'fit_fourth_power',
    'ln_function': 'fit_ln_function',
    'inverse_function': 'fit_inverse_function',
    'inverse_square_function': 'fit_inverse_square_function',
    'sin_function': 'fit_sin_function',
    'sin_function_with_c': 'fit_sin_function_with_c',
    'cos_function': 'fit_cos_function',
    'cos_function_with_c': 'fit_cos_function_with_c',
    'tan_function': 'fit_tan_function',
    'tan_function_with_c': 'fit_tan_function_with_c',
    'sinh_function': 'fit_sinh_function',
    'cosh_function': 'fit_cosh_function',
    'exponential_function': 'fit_exponential_function',
    'binomial_function': 'fit_binomial_function',
    'gaussian_function': 'fit_gaussian_function',
    'square_pulse_function': 'fit_square_pulse_function',
    'hermite_polynomial_3': 'fit_hermite_polynomial_3',
    'hermite_polynomial_4': 'fit_hermite_polynomial_4',
}
"""
Mapping from equation type names to their corresponding fitting function names.

This dictionary maps user-friendly equation names to the internal function names
used in the fitting_functions module.
"""

AVAILABLE_EQUATION_TYPES = list(EQUATION_FUNCTION_MAP.keys())
"""
List of all available equation types that can be used for fitting.

This list defines all the equation types that the application can test
when applying multiple equation fits to a dataset.
"""

EQUATION_FORMULAS: dict[str, str] = {
    'linear_function_with_n': 'y = mx + n',
    'linear_function': 'y = mx',
    'quadratic_function_complete': 'y = ax² + bx + c',
    'quadratic_function': 'y = ax²',
    'fourth_power': 'y = ax⁴',
    'sin_function': 'y = a·sin(bx)',
    'sin_function_with_c': 'y = a·sin(bx + c)',
    'cos_function': 'y = a·cos(bx)',
    'cos_function_with_c': 'y = a·cos(bx + c)',
    'sinh_function': 'y = a·sinh(bx)',
    'cosh_function': 'y = a·cosh(bx)',
    'ln_function': 'y = a·ln(x)',
    'inverse_function': 'y = a/x',
    'inverse_square_function': 'y = a/x²',
    'gaussian_function': 'y = a·exp(-(x-μ)²/(2σ²))',
    'exponential_function': 'y = a·exp(bx)',
    'binomial_function': 'y = L/(1 + exp(-k(x-x₀)))',
    'tan_function': 'y = a·tan(bx)',
    'tan_function_with_c': 'y = a·tan(bx + c)',
    'square_pulse_function': 'y = a si |x-x₀| ≤ w/2, else 0',
    'hermite_polynomial_3': 'y = Σ cᵢ·Hᵢ(x) (grado 0-3)',
    'hermite_polynomial_4': 'y = Σ cᵢ·Hᵢ(x) (grado 0-4)',
}
"""
Display formulas for each equation type (for tooltips and UI).
"""

EQUATION_PARAM_NAMES: dict[str, list[str]] = {
    'linear_function_with_n': ['n', 'm'],
    'linear_function': ['m'],
    'quadratic_function_complete': ['a', 'b', 'c'],
    'quadratic_function': ['a'],
    'fourth_power': ['a'],
    'sin_function': ['a', 'b'],
    'sin_function_with_c': ['a', 'b', 'c'],
    'cos_function': ['a', 'b'],
    'cos_function_with_c': ['a', 'b', 'c'],
    'sinh_function': ['a', 'b'],
    'cosh_function': ['a', 'b'],
    'ln_function': ['a'],
    'inverse_function': ['a'],
    'inverse_square_function': ['a'],
    'gaussian_function': ['A', 'mu', 'sigma'],
    'exponential_function': ['a', 'b'],
    'binomial_function': ['a', 'b', 'c'],
    'tan_function': ['a', 'b'],
    'tan_function_with_c': ['a', 'b', 'c'],
    'square_pulse_function': ['A', 't0', 'w'],
    'hermite_polynomial_3': ['c0', 'c1', 'c2', 'c3'],
    'hermite_polynomial_4': ['c0', 'c1', 'c2', 'c3', 'c4'],
}
"""
Parameter names per equation type (for initial/bounds UI and overrides).
"""


# ============================================================================
# SPECIAL VALUES AND CONSTANTS
# ============================================================================

__version__ = "0.8.2"
"""Application version. Keep in sync with version in pyproject.toml."""

EXIT_SIGNAL = 'Salir'
"""
Internal signal value used to indicate user wants to exit/cancel an operation.
This constant is used throughout the application for consistency.
The UI should display the translated version using t('dialog.exit_option').
"""


# ============================================================================
# AVAILABLE COLOR OPTIONS (Documentation)
# ============================================================================
"""
Common color names you can use in environment variables:

Basic colors:
- 'white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta'

Extended colors:
- 'orange', 'purple', 'pink', 'brown', 'gray', 'lime', 'teal', 'navy'

Special colors:
- 'crimson', 'coral', 'gold', 'silver', 'ivory', 'snow', 'mint cream'

Blues:
- 'navy', 'royal blue', 'midnight blue', 'sky blue', 'steel blue'

Greens:
- 'lime green', 'forest green', 'sea green', 'dark green', 'olive'

Reds:
- 'crimson', 'firebrick', 'dark red', 'indian red', 'tomato'

You can also use hex colors like '#FF5733' or RGB tuples like (0.5, 0.2, 0.8)
"""
