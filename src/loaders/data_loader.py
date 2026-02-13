"""
Data loading logic module.

This module handles all data loading operations without UI dependencies.
It provides a clean separation between data access logic (backend) and
user interface (frontend).

Key features:

    - Path construction for data files
    - Loading from CSV, TXT and Excel formats
    - Variable name extraction from datasets
    - File categorization by type

All functions are UI-independent and can be used in both GUI and CLI contexts.
"""

# Standard library
from typing import Callable, List, Optional, Tuple

# Third-party packages
import pandas as pd

# Local imports
from config import FILE_CONFIG, get_project_root
from loaders.loading_utils import csv_reader, excel_reader, txt_reader
from utils import get_logger, validate_file_type

logger = get_logger(__name__)


def _prepare_data_path(
    filename: str, file_type: str, base_dir: Optional[str] = None
) -> str:
    """
    Construct the complete path to a data file.

    This function builds an absolute path from the project root to the data file,
    ensuring cross-platform compatibility using pathlib.

    Args:
        filename: File name without extension (e.g., 'Example', 'Experiment1').
        file_type: File extension ('csv', 'xlsx', 'txt').
        base_dir: Base directory where data files are located (relative to project root).
            If None, uses FILE_CONFIG['input_dir'].

    Returns:
        Complete file path (absolute from project root).

    Examples:
        >>> _prepare_data_path('Example', 'xlsx')
        'C:/Users/user/project/input/Example.xlsx'
    """
    if base_dir is None:
        base_dir = FILE_CONFIG['input_dir']
    
    # Get the project root directory
    project_root = get_project_root()
    # Construct path: root / base_dir / filename.extension
    data_path = project_root / base_dir / f'{filename}.{file_type}'
    return str(data_path)


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


def get_file_list_by_type(
    file_type: str,
    csv: List[str],
    xlsx: List[str],
    txt: List[str],
) -> List[str]:
    """
    Get list of files based on selected type.
    
    This function acts as a selector/router that returns the appropriate
    file list based on the user's file type selection.
    
    Args:
        file_type: File type ('csv', 'xlsx', 'txt')
        csv: List of CSV file names (without extension)
        xlsx: List of XLSX file names (without extension)
        txt: List of TXT file names (without extension)
        
    Returns:
        List of files of the specified type
        
    Raises:
        InvalidFileTypeError: If file type is not valid
        
    Examples:
        >>> csv_files = ['data1', 'data2']
        >>> xlsx_files = ['experiment1', 'experiment2']
        >>> get_file_list_by_type('csv', csv_files, xlsx_files, [])
        ['data1', 'data2']
    """
    logger.debug(f"Getting file list for type: {file_type}")
    validate_file_type(file_type)

    file_lists: dict[str, List[str]] = {
        'csv': csv,
        'xlsx': xlsx,
        'txt': txt,
    }
    file_list = file_lists[file_type]
    logger.debug(f"Found {len(file_list)} files of type {file_type}")
    return file_list


def load_data_workflow(filename: str, file_type: str) -> Tuple[pd.DataFrame, str]:
    """
    Complete data loading workflow.
    
    This convenience function combines path preparation and data loading
    into a single operation. It's the main entry point for loading data
    files in the application.
    
    Args:
        filename: File name without extension (e.g., 'Example')
        file_type: File type ('csv', 'xlsx', 'txt')
        
    Returns:
        Tuple of (data DataFrame, complete file path)
        The file path is returned so it can be used for reloading in loop mode
        
    Raises:
        DataLoadError: If data cannot be loaded
        
    Examples:
        >>> data, path = load_data_workflow('Example', 'xlsx')
        >>> print(data.head())
        >>> print(f"Loaded from: {path}")
    """
    logger.info(f"Starting data loading workflow: {filename}.{file_type}")
    
    try:
        # Step 1: Construct the complete file path
        file_path = _prepare_data_path(filename, file_type)
        logger.debug(f"Prepared file path: {file_path}")
        
        # Step 2: Load the data from the file
        data = load_data(file_path, file_type)
        
        logger.info(f"Data loading workflow completed successfully: {filename}.{file_type}")
        # Return both data and path (path needed for reloading in loop mode)
        return data, file_path
        
    except Exception as e:
        logger.error(
            f"Data loading workflow failed: {filename}.{file_type} - {str(e)}",
            exc_info=True
        )
        raise
