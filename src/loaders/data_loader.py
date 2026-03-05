"""
Data loading logic module.

This module handles all data loading operations without UI dependencies.
It provides a clean separation between data access logic (backend) and
user interface (frontend).

Key features:

    - Loading from CSV, TXT and Excel formats
    - Variable name extraction from datasets

All functions are UI-independent and can be used in both GUI and CLI contexts.
"""

# Standard library
from typing import Callable, List

# Third-party packages
import pandas as pd

# Local imports
from loaders.loading_utils import csv_reader, excel_reader, txt_reader
from utils import get_logger, validate_file_type

logger = get_logger(__name__)


# Reader dispatch by file type (used by load_data and workflow_controller)
FILE_TYPE_READERS: dict[str, Callable[[str], pd.DataFrame]] = {
    'csv': csv_reader,
    'xlsx': excel_reader,
    'txt': txt_reader,
}


def load_data(file_path: str, file_type: str) -> pd.DataFrame:
    """
    Load data based on file type.
    
    Args:
        file_path: Complete path to the file
        file_type: File type ('csv', 'xlsx', 'txt')
        
    Returns:
        DataFrame with loaded data.

    Raises:
        InvalidFileTypeError: If file type is not supported.
        DataLoadError: If file cannot be loaded (from underlying readers).
        Other exceptions from csv_reader/excel_reader may propagate.
    """
    logger.debug(f"Loading data: {file_path} (type: {file_type})")
    validate_file_type(file_type)

    try:
        return FILE_TYPE_READERS[file_type](file_path)
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {str(e)}", exc_info=True)
        raise


def get_variable_names(data: pd.DataFrame, filter_uncertainty: bool = False) -> List[str]:
    """
    Extract variable names from the dataset.

    When filter_uncertainty is False, returns all column names (e.g. 'x', 'ux', 'y', 'uy').
    When True, excludes uncertainty columns (e.g. 'ux', 'uy') so only base variables
    like 'x', 'y' are returned. Uncertainty columns are assumed to be named 'u<varname>'.

    Args:
        data: DataFrame with the data
        filter_uncertainty: If True, exclude uncertainty columns from the result

    Returns:
        List of column names as strings.

    Examples:
        >>> df = pd.DataFrame({'x': [1,2], 'ux': [0.1, 0.1], 'y': [2,4], 'uy': [0.2, 0.2]})
        >>> get_variable_names(df)
        ['x', 'ux', 'y', 'uy']
        >>> get_variable_names(df, filter_uncertainty=True)
        ['x', 'y']
    """
    columns = list(data.columns)
    if not filter_uncertainty:
        return columns

    columns_set = set(data.columns)
    uncertainty_cols = {
        c for c in data.columns
        if len(c) > 1 and c.startswith('u') and c[1:] in columns_set
    }
    return [c for c in columns if c not in uncertainty_cols]
