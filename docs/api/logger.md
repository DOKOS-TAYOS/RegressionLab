# utils.logger

Logging configuration for RegressionLab.

## Overview

The `logger.py` module provides centralized logging configuration and utilities. It supports both file and console logging with customizable log levels and colored output.

## Key Functions

### Logging Setup

#### `setup_logging(log_file=None, level=None, console=None, log_format=DEFAULT_LOG_FORMAT, date_format=DEFAULT_DATE_FORMAT) -> None`

Configure application-wide logging.

This function sets up logging to both file and console (optional). If no parameters are provided, it uses environment variables or defaults.

**Parameters:**
- `log_file`: Path to log file. If None, uses LOG_FILE env var or default
- `level`: Logging level. If None, uses LOG_LEVEL env var or INFO
- `console`: Enable console logging. If None, uses LOG_CONSOLE env var or True
- `log_format`: Format string for log messages
- `date_format`: Format string for timestamps

**Example:**
```python
from utils.logger import setup_logging
import logging

# Use defaults and env vars
setup_logging()

# Custom configuration
setup_logging(
    log_file='my_app.log',
    level=logging.DEBUG,
    console=True
)
```

### Getting Loggers

#### `get_logger(name: str) -> logging.Logger`

Get a logger instance for a specific module.

**Parameters:**
- `name`: Name of the logger (typically `__name__` of the module)

**Returns:**
- Logger instance

**Example:**
```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Processing data...")
logger.error("Failed to load file", exc_info=True)
```

## Logging Levels

The module supports standard Python logging levels:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Setting Log Level

```python
from utils.logger import setup_logging
import logging

# Via function
setup_logging(level=logging.DEBUG)

# Via environment variable
# LOG_LEVEL=DEBUG
```

## Configuration

### Environment Variables

Logging can be configured via environment variables:

```ini
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path
LOG_FILE=regressionlab.log

# Enable console logging (true/false)
LOG_CONSOLE=true
```

### Default Values

- **Log Level**: INFO
- **Log File**: `regressionlab.log`
- **Console Logging**: Enabled
- **Format**: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- **Date Format**: `'%Y-%m-%d %H:%M:%S'`

## Colored Output

The module provides colored console output when `colorama` is available:

- **DEBUG**: Cyan
- **INFO**: Green
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Bright Red

### ColoredFormatter

Custom formatter that adds color to console log output.

**Usage:**
```python
from utils.logger import ColoredFormatter
import logging

formatter = ColoredFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

## Utility Functions

### `log_function_call(logger: logging.Logger, func_name: str, **kwargs) -> None`

Log a function call with its parameters.

**Parameters:**
- `logger`: Logger instance to use
- `func_name`: Name of the function being called
- `**kwargs`: Function parameters to log

**Example:**
```python
from utils.logger import get_logger, log_function_call

logger = get_logger(__name__)

def fit_linear(x, y):
    log_function_call(logger, 'fit_linear', x_name='time', y_name='distance')
    # ... function implementation
```

### `log_exception(logger: logging.Logger, exception: Exception, context: str = None) -> None`

Log an exception with context.

**Parameters:**
- `logger`: Logger instance to use
- `exception`: Exception that occurred
- `context`: Optional context description

**Example:**
```python
from utils.logger import get_logger, log_exception

logger = get_logger(__name__)

try:
    # some code
    result = risky_operation()
except Exception as e:
    log_exception(logger, e, "Failed to load data")
```

## Usage Examples

### Basic Setup

```python
# In main_program.py
from utils.logger import setup_logging

# Initialize logging at startup
setup_logging()
```

### Module Logging

```python
# In any module
from utils.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("Starting operation")
    try:
        # do something
        logger.debug("Operation successful")
    except Exception as e:
        logger.error("Operation failed", exc_info=True)
        raise
```

### Error Logging

```python
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    data = load_data('file.csv')
except FileNotFoundError as e:
    logger.error(f"File not found: {e}", exc_info=True)
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### Debug Logging

```python
from utils.logger import get_logger
import logging

logger = get_logger(__name__)

# Enable debug logging
logger.setLevel(logging.DEBUG)

logger.debug("Detailed diagnostic information")
logger.debug(f"Variable value: {variable}")
```

## Log File Location

By default, log files are saved in the project root directory. The directory is created automatically if it doesn't exist.

**Example:**
```python
# Log file: regressionlab.log (in project root)
setup_logging()

# Custom location
setup_logging(log_file='logs/app.log')
# Creates logs/ directory if needed
```

## Best Practices

1. **Initialize Early**: Set up logging at application startup
   ```python
   # main_program.py
   from utils.logger import setup_logging
   
   if __name__ == "__main__":
       setup_logging()
       # ... rest of application
   ```

2. **Use Module Name**: Use `__name__` for logger names
   ```python
   logger = get_logger(__name__)  # Good
   logger = get_logger('my_module')  # Also OK
   ```

3. **Appropriate Levels**: Use appropriate log levels
   ```python
   logger.debug("Detailed diagnostic")  # Development
   logger.info("General information")    # Normal operation
   logger.warning("Potential issue")     # Warning
   logger.error("Error occurred")        # Error
   logger.critical("Critical failure")    # Critical
   ```

4. **Include Context**: Provide context in log messages
   ```python
   # Good
   logger.error(f"Failed to load {file_path}: {e}")
   
   # Less informative
   logger.error("Failed to load")
   ```

5. **Exception Logging**: Always use `exc_info=True` for exceptions
   ```python
   try:
       risky_operation()
   except Exception as e:
       logger.error("Operation failed", exc_info=True)
   ```

6. **Performance**: Avoid expensive operations in log messages
   ```python
   # Good (lazy evaluation)
   logger.debug(f"Value: {expensive_operation()}")
   
   # Better (only evaluates if DEBUG enabled)
   if logger.isEnabledFor(logging.DEBUG):
       logger.debug(f"Value: {expensive_operation()}")
   ```

## Integration with i18n

Log messages can be internationalized:

```python
from utils.logger import get_logger
from i18n import t

logger = get_logger(__name__)
logger.info(t('log.application_starting'))
```

## Testing

```python
import logging
from utils.logger import get_logger, setup_logging

# Setup logging for tests
setup_logging(level=logging.DEBUG)

logger = get_logger(__name__)

def test_function():
    logger.info("Running test")
    # ... test code
```

## Technical Details

### Handler Management

- **File Handler**: Always added (unless file creation fails)
- **Console Handler**: Added if console logging is enabled
- **Existing Handlers**: Cleared before adding new ones to avoid duplicates

### Thread Safety

Logging is thread-safe by default in Python's logging module.

### Performance

- **Lazy Evaluation**: Log messages are only formatted if the level is enabled
- **Buffering**: File handler uses default buffering
- **Colorama**: Only initialized if available
- **Log Level Resolution**: Environment log level is resolved via a module-level mapping (no per-call dict build)

---

*For more information about logging, see [Troubleshooting Guide](../troubleshooting.md).*
