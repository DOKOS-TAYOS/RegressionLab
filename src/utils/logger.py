"""
Logging configuration for RegressionLab.

This module provides centralized logging configuration and utilities.
It supports both file and console logging with customizable log levels.
"""

# Standard library
import logging
from pathlib import Path
from typing import Optional

# Third-party packages
try:
    from colorama import Fore, Style, init as colorama_init

    # Initialize colorama for Windows
    colorama_init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Local imports
from config import DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, get_env
from i18n import t

# Format defaults
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Color configuration for different log levels
LOG_COLORS = {
    'DEBUG': Fore.CYAN if COLORAMA_AVAILABLE else '',
    'INFO': Fore.GREEN if COLORAMA_AVAILABLE else '',
    'WARNING': Fore.YELLOW if COLORAMA_AVAILABLE else '',
    'ERROR': Fore.RED if COLORAMA_AVAILABLE else '',
    'CRITICAL': Fore.RED + Style.BRIGHT if COLORAMA_AVAILABLE else '',
}


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color to console log output.
    
    Colors are applied based on log level:

        - DEBUG: Cyan
        - INFO: Green
        - WARNING: Yellow
        - ERROR: Red
        - CRITICAL: Bright Red
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with colors.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted and colored log string
        """
        if not COLORAMA_AVAILABLE:
            return super().format(record)
        
        # Get the color for this log level
        color = LOG_COLORS.get(record.levelname, '')
        reset = Style.RESET_ALL if COLORAMA_AVAILABLE else ''
        
        # Save the original levelname
        original_levelname = record.levelname
        
        # Add color to levelname
        record.levelname = f"{color}{record.levelname}{reset}"
        
        # Format the message
        formatted = super().format(record)
        
        # Restore original levelname
        record.levelname = original_levelname
        
        return formatted


def get_log_level_from_env() -> int:
    """
    Get log level from environment variable.
    
    Returns:
        Logging level constant (e.g., logging.INFO)
    """
    # Use central configuration helper so values and defaults always
    # match those defined in ``.env`` / ``config.env.ENV_SCHEMA``.
    level_name = str(get_env('LOG_LEVEL', DEFAULT_LOG_LEVEL)).upper()

    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    
    return level_map.get(level_name, logging.INFO)


def get_log_file_from_env() -> str:
    """
    Get log file path from environment variable.
    
    Returns:
        Path to log file
    """
    return str(get_env('LOG_FILE', DEFAULT_LOG_FILE))


def should_log_to_console() -> bool:
    """
    Check if console logging is enabled via environment variable.
    
    Returns:
        True if console logging should be enabled
    """
    # Default and casting are controlled by ``config.env`` so that GUI
    # and Streamlit apps share the exact same behaviour.
    return bool(get_env('LOG_CONSOLE', False, bool))


def setup_logging(
    log_file: Optional[str] = None,
    level: Optional[int] = None,
    console: Optional[bool] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT
) -> None:
    """
    Configure application-wide logging.
    
    This function sets up logging to both file and console (optional).
    If no parameters are provided, it uses environment variables or defaults.
    
    Args:
        log_file: Path to log file. If None, uses LOG_FILE env var or default
        level: Logging level. If None, uses LOG_LEVEL env var or INFO
        console: Enable console logging. If None, uses LOG_CONSOLE env var or True
        log_format: Format string for log messages
        date_format: Format string for timestamps
        
    Example:
        >>> setup_logging()  # Use defaults and env vars
        >>> setup_logging(log_file='my_app.log', level=logging.DEBUG)
    """
    # Get configuration from environment or use provided/default values
    if log_file is None:
        log_file = get_log_file_from_env()
    
    if level is None:
        level = get_log_level_from_env()
    
    if console is None:
        console = should_log_to_console()
    
    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    if log_path.parent != Path('.'):
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    # Use standard formatter for file (no colors)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    # Use colored formatter for console
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add file handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(t('warning.log_file_warning', log_file=log_file, error=str(e)))
    
    # Add console handler if enabled
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Log initial message
    root_logger.info(t('log.logging_initialized'))
    root_logger.debug(t('log.log_file', file=log_file))
    root_logger.debug(t('log.log_level', level=logging.getLevelName(level)))
    root_logger.debug(t('log.console_logging', enabled=console))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (typically __name__ of the module)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing data...")
        >>> logger.error("Failed to load file", exc_info=True)
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """
    Log a function call with its parameters.
    
    Args:
        logger: Logger instance to use
        func_name: Name of the function being called
        **kwargs: Function parameters to log
        
    Example:
        >>> logger = get_logger(__name__)
        >>> log_function_call(logger, 'fit_linear', x_name='time', y_name='distance')
    """
    params = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"Calling {func_name}({params})")


def log_exception(
    logger: logging.Logger, exception: Exception, context: Optional[str] = None
) -> None:
    """
    Log an exception with context.

    Args:
        logger: Logger instance to use.
        exception: Exception that occurred.
        context: Optional context description.

    Example:
        >>> try:
        >>>     # some code
        >>> except Exception as e:
        >>>     log_exception(logger, e, "Failed to load data")
    """
    if context:
        logger.error(f"{context}: {type(exception).__name__}: {exception}", exc_info=True)
    else:
        logger.error(f"{type(exception).__name__}: {exception}", exc_info=True)
