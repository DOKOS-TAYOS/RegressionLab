"""
Utils module.
Contains utility functions including exceptions, logging, and validation.
"""

from .exceptions import (
    RegressionLabError,
    DataLoadError,
    DataValidationError,
    FileNotFoundError,
    InvalidFileTypeError,
    FittingError,
    EquationError,
    ConfigurationError,
    ValidationError,
)
from .logger import (
    ColoredFormatter,
    get_log_level_from_env,
    get_log_file_from_env,
    should_log_to_console,
    setup_logging,
    get_logger,
    log_function_call,
    log_exception,
)
from .validators import (
    validate_dataframe,
    validate_data_format,
    validate_file_path,
    validate_file_type,
    validate_parameter_names,
    parse_optional_float,
    validate_fitting_data,
)

__all__ = [
    'RegressionLabError',
    'DataLoadError',
    'DataValidationError',
    'FileNotFoundError',
    'InvalidFileTypeError',
    'FittingError',
    'EquationError',
    'ConfigurationError',
    'ValidationError',
    'ColoredFormatter',
    'get_log_level_from_env',
    'get_log_file_from_env',
    'should_log_to_console',
    'setup_logging',
    'get_logger',
    'log_function_call',
    'log_exception',
    'validate_dataframe',
    'validate_data_format',
    'validate_file_path',
    'validate_file_type',
    'validate_parameter_names',
    'parse_optional_float',
    'validate_fitting_data',
]
