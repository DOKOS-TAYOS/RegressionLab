#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Central configuration file for the RegresionLab project.

This file consolidates all configuration settings for:
- UI Theme and appearance
- Plot styling and fonts
- File paths and output directories
- Environment variable loading

All modules should import configuration from this central file.
"""

import os
from pathlib import Path

# ============================================================================
# ENVIRONMENT VARIABLE LOADING
# ============================================================================

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in the project root (one level up from src/)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed, will use defaults
    pass


def get_env(key: str, default, cast_type=str):
    """
    Get environment variable with type casting and default value.
    
    Args:
        key: Environment variable name
        default: Default value if variable not found
        cast_type: Type to cast the value to (str, int, float, bool)
        
    Returns:
        The environment variable value cast to the specified type, or default
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
    # Line properties for fitted curve
    'line_color': get_env('PLOT_LINE_COLOR', 'black'),
    'line_width': get_env('PLOT_LINE_WIDTH', 1.00, float),
    'line_style': get_env('PLOT_LINE_STYLE', '-'),  # '-' solid, '--' dashed, '-.' dash-dot, ':' dotted
    
    # Marker properties for data points
    'marker_format': get_env('PLOT_MARKER_FORMAT', 'o'),  # 'o' circle, 's' square, '^' triangle, 'd' diamond
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
    'title_size': get_env('FONT_TITLE_SIZE', 'xx-large'),  # 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'
    'title_weight': get_env('FONT_TITLE_WEIGHT', 'semibold'),  # 'normal', 'bold', 'light', 'semibold', 'heavy'
    
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


def setup_fonts():
    """
    Setup and return font properties for plots.
    
    Returns:
        Tuple of (title_font, axis_font) FontProperties objects
    """
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
    
    return fontt, fonta


# ============================================================================
# FILE PATH CONFIGURATION
# ============================================================================

FILE_CONFIG = {
    # Input directory for data files (relative to project root)
    'input_dir': get_env('FILE_INPUT_DIR', 'input'),

    # Output directory for plots (relative to project root)
    'output_dir': get_env('FILE_OUTPUT_DIR', 'output'),
    
    # Filename template (use {} as placeholder for fit name)
    'filename_template': get_env('FILE_FILENAME_TEMPLATE', 'fit_{}.png'),
}


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root (parent of src/)
    """
    return Path(__file__).parent.parent


def ensure_output_directory(output_dir: str = None) -> str:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Optional directory path. If None, uses FILE_CONFIG['output_dir']
        
    Returns:
        The output directory path (absolute path from project root)
        
    Raises:
        OSError: If directory cannot be created
    """
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']
    
    # Make path relative to project root
    project_root = get_project_root()
    full_path = project_root / output_dir
    
    try:
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise OSError(f"No se pudo crear el directorio de salida: {str(e)}")
    
    return str(full_path)


def get_output_path(fit_name: str, output_dir: str = None) -> str:
    """
    Get the full output path for a plot.
    
    Args:
        fit_name: Name of the fit/adjustment (used in filename)
        output_dir: Optional directory path. If None, uses FILE_CONFIG['output_dir']
        
    Returns:
        Full path to the output file
    """
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']
    
    # Ensure output directory exists and get absolute path
    output_path = ensure_output_directory(output_dir)
    
    # Create filename
    filename = FILE_CONFIG['filename_template'].format(fit_name)
    
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

EQUATION_FUNCTION_MAP = {
    'linear_function_with_n': 'fit_linear_function_with_n',
    'linear_function': 'fit_linear_function',
    'ln_function': 'fit_ln_function',
    'quadratic_function_complete': 'fit_quadratic_function_complete',
    'quadratic_function': 'fit_quadratic_function',
    'fourth_power': 'fit_fourth_power',
    'sin_function': 'fit_sin_function',
    'sin_function_with_c': 'fit_sin_function_with_c',
    'cos_function': 'fit_cos_function',
    'cos_function_with_c': 'fit_cos_function_with_c',
    'sinh_function': 'fit_sinh_function',
    'cosh_function': 'fit_cosh_function',
    'inverse_function': 'fit_inverse_function',
    'inverse_square_function': 'fit_inverse_square_function'
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


# ============================================================================
# SPECIAL VALUES AND CONSTANTS
# ============================================================================

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
