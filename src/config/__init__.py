"""
Central configuration for the RegressionLab project.

Re-exports all configuration from submodules so that
"from config import UI_STYLE" etc. continue to work.
"""

from .env import (
    DONATIONS_URL,
    ENV_SCHEMA,
    get_current_env_values,
    get_env,
    write_env_file,
)
from .theme import (
    FONT_CONFIG,
    PLOT_CONFIG,
    UI_STYLE,
    UI_THEME,
    setup_fonts,
)
from .paths import (
    FILE_CONFIG,
    PLOT_FORMATS,
    ensure_output_directory,
    get_output_path,
    get_project_root,
)
from .constants import (
    AVAILABLE_EQUATION_TYPES,
    EQUATION_FORMULAS,
    EQUATION_FUNCTION_MAP,
    EQUATION_PARAM_NAMES,
    EXIT_SIGNAL,
    MATH_FUNCTION_REPLACEMENTS,
    __version__,
)

__all__ = [
    'get_env',
    'ENV_SCHEMA',
    'get_current_env_values',
    'write_env_file',
    'DONATIONS_URL',
    'UI_THEME',
    'UI_STYLE',
    'PLOT_CONFIG',
    'FONT_CONFIG',
    'setup_fonts',
    'PLOT_FORMATS',
    'FILE_CONFIG',
    'get_project_root',
    'ensure_output_directory',
    'get_output_path',
    'MATH_FUNCTION_REPLACEMENTS',
    'EQUATION_FUNCTION_MAP',
    'AVAILABLE_EQUATION_TYPES',
    'EQUATION_FORMULAS',
    'EQUATION_PARAM_NAMES',
    '__version__',
    'EXIT_SIGNAL',
]
