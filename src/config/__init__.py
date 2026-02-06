"""
Central configuration for the RegressionLab project.

Re-exports all configuration from submodules so that
"from config import UI_STYLE" etc. continue to work.
"""

from .env import (
    DEFAULT_LOG_FILE,
    DEFAULT_LOG_LEVEL,
    DONATIONS_URL,
    ENV_SCHEMA,
    get_current_env_values,
    get_env,
    initialize_and_validate_config,
    validate_all_env_values,
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
    ensure_output_directory,
    get_output_path,
    get_project_root,
)
from .constants import (
    AVAILABLE_EQUATION_TYPES,
    DATA_FILE_TYPES,
    EQUATIONS,
    EXIT_SIGNAL,
    MATH_FUNCTION_REPLACEMENTS,
    DEFAULT_LANGUAGE as _DEFAULT_LANG,
    LANGUAGE_ALIASES,
    SUPPORTED_LANGUAGE_CODES,
    __version__,
)

__all__ = [
    # From env
    'DEFAULT_LOG_FILE',
    'DEFAULT_LOG_LEVEL',
    'DONATIONS_URL',
    'ENV_SCHEMA',
    'get_current_env_values',
    'get_env',
    'initialize_and_validate_config',
    'validate_all_env_values',
    'write_env_file',
    # From theme
    'FONT_CONFIG',
    'PLOT_CONFIG',
    'UI_STYLE',
    'UI_THEME',
    'setup_fonts',
    # From paths
    'FILE_CONFIG',
    'ensure_output_directory',
    'get_output_path',
    'get_project_root',
    # From constants
    'AVAILABLE_EQUATION_TYPES',
    'DATA_FILE_TYPES',
    'EQUATIONS',
    'EXIT_SIGNAL',
    'MATH_FUNCTION_REPLACEMENTS',
    '_DEFAULT_LANG',
    'LANGUAGE_ALIASES',
    'SUPPORTED_LANGUAGE_CODES',
    '__version__',
]
