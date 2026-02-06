"""
Tests for logger module.
"""

import os
import logging
import pytest
import tempfile
from pathlib import Path

from utils import (
    get_log_level_from_env,
    get_log_file_from_env,
    should_log_to_console,
    setup_logging,
    get_logger,
    log_function_call,
    log_exception,
    ColoredFormatter,
)


@pytest.fixture(autouse=True)
def cleanup_logging() -> None:
    """Clean up logging handlers after each test."""
    yield
    logger = logging.getLogger()
    # Close all handlers before clearing to release file handles
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


class TestGetLogLevelFromEnv:
    """Tests for get_log_level_from_env function."""
    
    @pytest.fixture(autouse=True)
    def cleanup_env(self) -> None:
        """Clean up LOG_LEVEL env var after each test."""
        original_level = os.getenv('LOG_LEVEL')
        yield
        if original_level:
            os.environ['LOG_LEVEL'] = original_level
        elif 'LOG_LEVEL' in os.environ:
            del os.environ['LOG_LEVEL']
    
    def test_default_log_level(self) -> None:
        """Test default log level when env var not set."""
        if 'LOG_LEVEL' in os.environ:
            del os.environ['LOG_LEVEL']
        assert get_log_level_from_env() == logging.INFO
    
    @pytest.mark.parametrize("level_str,expected", [
        ('DEBUG', logging.DEBUG),
        ('WARNING', logging.WARNING),
        ('ERROR', logging.ERROR),
        ('debug', logging.DEBUG),  # Case insensitive
    ])
    def test_log_levels(self, level_str: str, expected: int) -> None:
        """Test different log levels."""
        os.environ['LOG_LEVEL'] = level_str
        assert get_log_level_from_env() == expected
    
    def test_invalid_level(self) -> None:
        """Test that invalid level defaults to INFO."""
        os.environ['LOG_LEVEL'] = 'INVALID'
        assert get_log_level_from_env() == logging.INFO


class TestGetLogFileFromEnv:
    """Tests for get_log_file_from_env function."""
    
    @pytest.fixture(autouse=True)
    def cleanup_env(self) -> None:
        """Clean up LOG_FILE env var after each test."""
        original_file = os.getenv('LOG_FILE')
        yield
        if original_file:
            os.environ['LOG_FILE'] = original_file
        elif 'LOG_FILE' in os.environ:
            del os.environ['LOG_FILE']
    
    def test_default_log_file(self) -> None:
        """Test default log file when env var not set."""
        if 'LOG_FILE' in os.environ:
            del os.environ['LOG_FILE']
        assert get_log_file_from_env() == 'regressionlab.log'
    
    def test_custom_log_file(self) -> None:
        """Test custom log file from env var."""
        os.environ['LOG_FILE'] = 'custom.log'
        assert get_log_file_from_env() == 'custom.log'


class TestShouldLogToConsole:
    """Tests for should_log_to_console function."""
    
    @pytest.fixture(autouse=True)
    def cleanup_env(self) -> None:
        """Clean up LOG_CONSOLE env var after each test."""
        original_console = os.getenv('LOG_CONSOLE')
        yield
        if original_console:
            os.environ['LOG_CONSOLE'] = original_console
        elif 'LOG_CONSOLE' in os.environ:
            del os.environ['LOG_CONSOLE']
    
    def test_default_console_logging(self) -> None:
        """Test default console logging when env var not set."""
        if 'LOG_CONSOLE' in os.environ:
            del os.environ['LOG_CONSOLE']
        # Default is False according to get_env('LOG_CONSOLE', False, bool)
        assert should_log_to_console() is False
    
    @pytest.mark.parametrize("value,expected", [
        ('true', True),
        ('True', True),
        ('1', True),
        ('yes', True),
        ('YES', True),
        ('false', False),
    ])
    def test_console_values(self, value: str, expected: bool) -> None:
        """Test console logging with different values."""
        os.environ['LOG_CONSOLE'] = value
        assert should_log_to_console() == expected


class TestSetupLogging:
    """Tests for setup_logging function."""
    
    @pytest.fixture
    def temp_log_file(self) -> str:
        """Create temporary log file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        temp_file.close()
        yield temp_file.name
        # Close handlers before deleting file
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        try:
            Path(temp_file.name).unlink(missing_ok=True)
        except PermissionError:
            # File might still be locked on Windows, ignore
            pass
    
    def test_setup_with_defaults(self, temp_log_file: str) -> None:
        """Test setup logging with default values."""
        setup_logging(log_file=temp_log_file, console=False)
        logger = logging.getLogger()
        assert len(logger.handlers) > 0
    
    def test_setup_with_custom_level(self, temp_log_file: str) -> None:
        """Test setup logging with custom level."""
        setup_logging(log_file=temp_log_file, level=logging.DEBUG, console=False)
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG
    
    def test_log_file_created(self, temp_log_file: str) -> None:
        """Test that log file is created."""
        setup_logging(log_file=temp_log_file, console=False)
        assert Path(temp_log_file).exists()


class TestGetLogger:
    """Tests for get_logger function."""
    
    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a logger instance."""
        logger = get_logger('test_module')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_module'
    
    def test_multiple_loggers(self) -> None:
        """Test getting multiple loggers with different names."""
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')
        assert logger1.name != logger2.name


class TestLogFunctionCall:
    """Tests for log_function_call function."""
    
    def test_log_function_call(self) -> None:
        """Test logging a function call."""
        logger = get_logger('test')
        log_function_call(logger, 'test_function', x=1, y=2, name='test')
    
    def test_log_function_call_no_params(self) -> None:
        """Test logging a function call without parameters."""
        logger = get_logger('test')
        log_function_call(logger, 'test_function')


class TestLogException:
    """Tests for log_exception function."""
    
    def test_log_exception_with_context(self) -> None:
        """Test logging an exception with context."""
        logger = get_logger('test')
        exception = ValueError("Test error")
        log_exception(logger, exception, "Test context")
    
    def test_log_exception_without_context(self) -> None:
        """Test logging an exception without context."""
        logger = get_logger('test')
        exception = RuntimeError("Test error")
        log_exception(logger, exception)


class TestColoredFormatter:
    """Tests for ColoredFormatter class."""
    
    def test_formatter_creation(self) -> None:
        """Test creating a ColoredFormatter."""
        formatter = ColoredFormatter('%(message)s')
        assert isinstance(formatter, ColoredFormatter)
    
    def test_format_log_record(self) -> None:
        """Test formatting a log record."""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert 'INFO' in formatted
        assert 'Test message' in formatted
