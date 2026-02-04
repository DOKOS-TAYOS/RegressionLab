#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from utils.exceptions import (
    DataValidationError,
    FileNotFoundError,
    InvalidFileTypeError,
    ValidationError
)
from utils.logger import get_logger
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
        allowed_types: List of allowed file types. Defaults to ['csv', 'xlsx', 'txt'].

    Raises:
        InvalidFileTypeError: If file type is not supported.
    """
    if allowed_types is None:
        allowed_types = ['csv', 'xlsx', 'txt']
    
    if file_type not in allowed_types:
        allowed_str = ', '.join(allowed_types)
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


def validate_column_exists(data: pd.DataFrame, column_name: str) -> None:
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


def validate_numeric_data(data: pd.Series, column_name: str) -> None:
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
    
    # Check for infinite values
    if np.isinf(data).any():
        inf_count = np.isinf(data).sum()
        logger.error(t('log.column_contains_infinite', column=column_name, count=inf_count))
        raise DataValidationError(
            t('error.column_contains_infinite_values', column=column_name)
        )
    
    logger.debug(t('log.numeric_data_validated', column=column_name))


def validate_uncertainty_column(data: pd.DataFrame, var_name: str) -> None:
    """
    Validate that uncertainty column exists and is valid for a variable.
    
    Args:
        data: DataFrame containing the data
        var_name: Name of the variable (uncertainty column should be 'u{var_name}')
        
    Raises:
        DataValidationError: If uncertainty column is missing or invalid
    """
    uncertainty_col = f'u{var_name}'
    validate_column_exists(data, uncertainty_col)
    validate_numeric_data(data[uncertainty_col], uncertainty_col)
    
    # Check that uncertainties are non-negative
    if (data[uncertainty_col] < 0).any():
        negative_count = (data[uncertainty_col] < 0).sum()
        logger.error(t('log.uncertainty_negative', column=uncertainty_col, count=negative_count))
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
    validate_column_exists(data, x_name)
    validate_column_exists(data, y_name)
    
    # Validate data is numeric
    validate_numeric_data(data[x_name], x_name)
    validate_numeric_data(data[y_name], y_name)
    
    # Validate uncertainty columns
    validate_uncertainty_column(data, x_name)
    validate_uncertainty_column(data, y_name)
    
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


def validate_positive_integer(value: Any, name: str) -> int:
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