"""
Data validation utilities for the RegressionLab application.

This module provides functions to validate data integrity,
file paths, and parameter values before processing.
"""

# Standard library
from pathlib import Path
from typing import Any, List, Optional, Union

# Third-party packages
import numpy as np
import pandas as pd

# Local imports
from config import DATA_FILE_TYPES
from .exceptions import (
    DataValidationError,
    FileNotFoundError,
    InvalidFileTypeError,
    ValidationError,
)
from .logger import get_logger
from i18n import t

logger = get_logger(__name__)


def validate_file_path(file_path: str) -> None:
    """
    Validate that a file path exists and is accessible.
    
    Args:
        file_path: Path to the file
        
    Raises:
        FileNotFoundError: If file does not exist
        ValidationError: If path is not a file
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.error(t('log.file_not_found', path=file_path))
        raise FileNotFoundError(t('error.file_not_found', path=file_path))
    
    if not path.is_file():
        logger.error(t('log.path_not_file', path=file_path))
        raise ValidationError(t('error.path_not_file', path=file_path))
    
    logger.debug(t('log.file_path_validated', path=file_path))


def validate_file_type(
    file_type: str, allowed_types: Optional[List[str]] = None
) -> None:
    """
    Validate that a file type is supported.

    Args:
        file_type: File extension (e.g., 'csv', 'xlsx').
        allowed_types: List of allowed file types. If None, uses the
            central list from :data:`config.DATA_FILE_TYPES`.

    Raises:
        InvalidFileTypeError: If file type is not supported.
    """
    effective_types = allowed_types if allowed_types is not None else list(
        DATA_FILE_TYPES
    )

    if file_type not in effective_types:
        allowed_str = ', '.join(effective_types)
        logger.error(
            t('log.invalid_file_type', file_type=file_type, allowed_types=allowed_str)
        )
        raise InvalidFileTypeError(
            t(
                'error.unsupported_file_type_details',
                file_type=file_type,
                allowed_types=allowed_str
            )
        )
    logger.debug(t('log.file_type_validated', file_type=file_type))


def validate_dataframe(data: pd.DataFrame, min_rows: int = 2) -> None:
    """
    Validate that a DataFrame is suitable for fitting.
    
    Args:
        data: DataFrame to validate
        min_rows: Minimum number of rows required
        
    Raises:
        DataValidationError: If DataFrame is invalid
    """
    if data is None:
        logger.error(t('log.dataframe_is_none'))
        raise DataValidationError(t('error.data_is_null'))
    
    if data.empty:
        logger.error(t('log.dataframe_is_empty'))
        raise DataValidationError(t('error.data_is_empty'))
    
    if len(data) < min_rows:
        logger.error(t('log.insufficient_rows', rows=len(data), min_rows=min_rows))
        raise DataValidationError(
            t('error.insufficient_data', min_rows=min_rows, rows=len(data))
        )
    
    logger.debug(t('log.dataframe_validated', rows=len(data), columns=len(data.columns)))


def _validate_column_exists(data: pd.DataFrame, column_name: str) -> None:
    """
    Validate that a column exists in a DataFrame.
    
    Args:
        data: DataFrame to check
        column_name: Name of the column
        
    Raises:
        DataValidationError: If column does not exist
    """
    if column_name not in data.columns:
        available = ', '.join(data.columns.tolist())
        logger.error(t('log.column_not_found', column=column_name, available=available))
        raise DataValidationError(
            t('error.column_not_found', column=column_name, available=available)
        )
    
    logger.debug(t('log.column_validated', column=column_name))


def _validate_numeric_data(data: pd.Series, column_name: str) -> None:
    """
    Validate that data in a column is numeric and has no NaN values.
    
    Args:
        data: Series to validate
        column_name: Name of the column (for error messages)
        
    Raises:
        DataValidationError: If data is not numeric or contains NaN
    """
    if not pd.api.types.is_numeric_dtype(data):
        logger.error(t('log.column_not_numeric', column=column_name, dtype=str(data.dtype)))
        raise DataValidationError(
            t('error.column_must_be_numeric', column=column_name)
        )
    
    nan_count = data.isna().sum()
    if nan_count > 0:
        logger.warning(t('log.column_contains_nan', column=column_name, count=nan_count))
        raise DataValidationError(
            t('error.column_contains_missing_values', column=column_name, count=nan_count)
        )
    
    # Check for infinite values (compute once for performance)
    inf_mask = np.isinf(data)
    if inf_mask.any():
        logger.error(t('log.column_contains_infinite', column=column_name, count=inf_mask.sum()))
        raise DataValidationError(
            t('error.column_contains_infinite_values', column=column_name)
        )
    
    logger.debug(t('log.numeric_data_validated', column=column_name))


def _validate_uncertainty_column(data: pd.DataFrame, var_name: str) -> None:
    """
    Validate that uncertainty column exists and is valid for a variable.
    
    Args:
        data: DataFrame containing the data
        var_name: Name of the variable (uncertainty column should be 'u{var_name}')
        
    Raises:
        DataValidationError: If uncertainty column is missing or invalid
    """
    uncertainty_col = f'u{var_name}'
    _validate_column_exists(data, uncertainty_col)
    series = data[uncertainty_col]
    _validate_numeric_data(series, uncertainty_col)
    # Check that uncertainties are non-negative
    neg_mask = series < 0
    if neg_mask.any():
        logger.error(t('log.uncertainty_negative', column=uncertainty_col, count=neg_mask.sum()))
        raise DataValidationError(
            t('error.uncertainties_must_be_non_negative', column=uncertainty_col)
        )
    
    logger.debug(t('log.uncertainty_column_validated', column=uncertainty_col))


def validate_fitting_data(
    data: Union[pd.DataFrame, dict], x_name: str, y_name: str
) -> None:
    """
    Comprehensive validation for fitting data.

    Validates:

        - DataFrame is not empty
        - Required columns exist
        - Data is numeric
        - Uncertainty columns exist and are valid

    Args:
        data: DataFrame or dict with data to fit (dict is converted to DataFrame).
        x_name: Name of the independent variable column
        y_name: Name of the dependent variable column

    Raises:
        DataValidationError: If any validation fails
    """
    logger.info(t('log.validating_fitting_data', x=x_name, y=y_name))

    if isinstance(data, dict):
        data = pd.DataFrame(data)

    # Validate DataFrame
    validate_dataframe(data, min_rows=2)
    
    # Validate variable columns exist
    _validate_column_exists(data, x_name)
    _validate_column_exists(data, y_name)
    
    # Validate data is numeric
    _validate_numeric_data(data[x_name], x_name)
    _validate_numeric_data(data[y_name], y_name)
    
    # Validate uncertainty columns
    _validate_uncertainty_column(data, x_name)
    _validate_uncertainty_column(data, y_name)
    
    logger.info(t('log.fitting_data_validation_successful', points=len(data)))


def validate_parameter_names(param_names: List[str]) -> None:
    """
    Validate parameter names for custom equations.
    
    Args:
        param_names: List of parameter names
        
    Raises:
        ValidationError: If parameter names are invalid
    """
    if not param_names:
        logger.error(t('log.parameter_names_empty'))
        raise ValidationError(t('error.parameter_names_list_empty'))
    
    # Check for duplicate names
    if len(param_names) != len(set(param_names)):
        logger.error(t('log.duplicate_parameter_names', params=str(param_names)))
        raise ValidationError(t('error.parameter_names_must_be_unique'))
    
    # Check for valid Python identifiers
    for name in param_names:
        if not name.isidentifier():
            logger.error(t('log.invalid_parameter_name', name=name))
            raise ValidationError(
                t('error.invalid_parameter_name', name=name)
            )
    
    logger.debug(t('log.parameter_names_validated', params=str(param_names)))


def _validate_positive_integer(value: Any, name: str) -> int:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        
    Returns:
        The validated integer value
        
    Raises:
        ValidationError: If value is not a positive integer
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        logger.error(t('log.value_not_integer', value=str(value), name=name))
        raise ValidationError(t('error.must_be_integer', name=name))
    
    if int_value <= 0:
        logger.error(t('log.value_not_positive', value=int_value, name=name))
        raise ValidationError(t('error.must_be_positive', name=name))
    
    logger.debug(t('log.positive_integer_validated', name=name, value=int_value))
    return int_value


def parse_optional_float(s: str) -> Optional[float]:
    """
    Parse a string to float; empty or invalid input returns None.

    Useful for optional numeric fields in dialogs (e.g. initial guess, bounds).

    Args:
        s: String to parse (e.g. from an Entry widget).

    Returns:
        The parsed float, or None if empty or invalid.
    """
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _validate_column_names(data: pd.DataFrame) -> None:
    """
    Validate that column names are valid and not duplicated.
    
    Args:
        data: DataFrame to validate
        
    Raises:
        DataValidationError: If column names are invalid or duplicated
    """
    if len(data.columns) == 0:
        logger.error(t('log.no_columns_found'))
        raise DataValidationError(t('error.no_columns_in_file'))
    
    # Check for duplicate column names
    dup_mask = data.columns.duplicated()
    if dup_mask.any():
        dup_str = ', '.join(data.columns[dup_mask].unique().tolist())
        logger.error(t('log.duplicate_columns', columns=dup_str))
        raise DataValidationError(t('error.duplicate_column_names', columns=dup_str))
    
    # Check for empty column names
    empty_names = [name for name in data.columns if not str(name).strip()]
    if empty_names:
        logger.error(t('log.empty_column_names', count=len(empty_names)))
        raise DataValidationError(t('error.empty_column_names'))
    
    logger.debug(t('log.column_names_validated', count=len(data.columns)))


def _validate_all_columns_numeric(data: pd.DataFrame) -> None:
    """
    Validate that all columns contain numeric data (or can be converted to numeric).
    
    This function attempts to convert non-numeric columns to numeric and reports
    which columns cannot be converted.
    
    Args:
        data: DataFrame to validate
        
    Raises:
        DataValidationError: If any column cannot be converted to numeric
    """
    non_numeric_columns: List[str] = []
    
    for col in data.columns:
        # Check if column is already numeric
        if pd.api.types.is_numeric_dtype(data[col]):
            continue
        
        # Try to convert to numeric
        try:
            pd.to_numeric(data[col], errors='raise')
        except (ValueError, TypeError):
            non_numeric_columns.append(col)
    
    if non_numeric_columns:
        logger.error(
            t('log.non_numeric_columns', columns=', '.join(non_numeric_columns))
        )
        raise DataValidationError(
            t('error.columns_must_be_numeric', columns=', '.join(non_numeric_columns))
        )
    
    logger.debug(t('log.all_columns_numeric_validated'))


def _validate_no_completely_empty_rows(data: pd.DataFrame) -> None:
    """
    Validate that there are no completely empty rows in the DataFrame.
    
    Args:
        data: DataFrame to validate
        
    Raises:
        DataValidationError: If completely empty rows are found
    """
    # Find rows where all values are NaN or empty
    empty_rows = data.isna().all(axis=1)
    
    if empty_rows.any():
        empty_row_indices = data.index[empty_rows].tolist()
        empty_count = len(empty_row_indices)
        logger.warning(
            t('log.empty_rows_found', count=empty_count, rows=str(empty_row_indices[:10]))
        )
        # Note: We warn but don't raise an error, as pandas handles empty rows
        # But we log it for user awareness
    
    logger.debug(t('log.empty_rows_validated'))


def validate_data_format(data: pd.DataFrame) -> None:
    """
    Comprehensive validation of data file format.
    
    This function validates:
    - Column names are valid and not duplicated
    - All columns contain numeric data
    - No completely empty rows
    - Minimum requirements (rows and columns)
    
    Args:
        data: DataFrame to validate
        
    Raises:
        DataValidationError: If data format is invalid
    """
    logger.info(t('log.validating_data_format'))
    
    # Basic DataFrame validation
    validate_dataframe(data, min_rows=2)
    
    # Validate column names
    _validate_column_names(data)
    
    # Validate all columns are numeric
    _validate_all_columns_numeric(data)
    
    # Check for completely empty rows (warning only)
    _validate_no_completely_empty_rows(data)
    
    logger.info(t('log.data_format_validated', rows=len(data), columns=len(data.columns)))