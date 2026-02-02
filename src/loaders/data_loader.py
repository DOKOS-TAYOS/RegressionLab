#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data loading logic module.

This module handles all data loading operations without UI dependencies.
It provides a clean separation between data access logic (backend) and
user interface (frontend).

Key features:

    - Path construction for data files
    - Loading from CSV and Excel formats
    - Variable name extraction from datasets
    - File categorization by type

All functions are UI-independent and can be used in both GUI and CLI contexts.
"""

# Standard library
from typing import List, Tuple

# Third-party packages
import pandas as pd

# Local imports
from config import FILE_CONFIG, get_project_root
from loaders.loading_utils import csv_reader, excel_reader
from utils.exceptions import InvalidFileTypeError
from utils.logger import get_logger
from utils.validators import validate_file_type

logger = get_logger(__name__)


def prepare_data_path(filename: str, file_type: str, base_dir: str = None) -> str:
    """
    Construct the complete path to a data file.
    
    This function builds an absolute path from the project root to the data file,
    ensuring cross-platform compatibility using pathlib.
    
    Args:
        filename: File name without extension (e.g., 'Ejemplo', 'Exper1')
        file_type: File extension ('csv', 'xls', 'xlsx')
        base_dir: Base directory where data files are located (relative to project root).
                  If None, uses FILE_INPUT_DIR from environment variables or default 'input'
        
    Returns:
        Complete file path (absolute from project root)
        
    Example:
        >>> prepare_data_path('Ejemplo', 'xlsx')
        'C:/Users/user/project/input/Ejemplo.xlsx'
    """
    # Get base directory from environment variable if not specified
    if base_dir is None:
        base_dir = FILE_CONFIG['input_dir']
    
    # Get the project root directory
    project_root = get_project_root()
    # Construct path: root / base_dir / filename.extension
    data_path = project_root / base_dir / f'{filename}.{file_type}'
    return str(data_path)


def load_data(file_path: str, file_type: str) -> pd.DataFrame:
    """
    Load data based on file type.
    
    Args:
        file_path: Complete path to the file
        file_type: File type ('csv', 'xls', 'xlsx')
        
    Returns:
        DataFrame with loaded data
        
    Raises:
        InvalidFileTypeError: If file type is not supported
        DataLoadError: If file cannot be loaded
    """
    logger.debug(f"Loading data: {file_path} (type: {file_type})")
    
    # Validate file type
    validate_file_type(file_type)
    
    try:
        if file_type == 'csv':
            return csv_reader(file_path)
        elif file_type in ['xls', 'xlsx']:
            return excel_reader(file_path)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            raise InvalidFileTypeError(f"Tipo de archivo no soportado: {file_type}")
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
        List of column names as strings

    Example:
        >>> df = pd.DataFrame({'x': [1,2], 'ux': [0.1, 0.1], 'y': [2,4], 'uy': [0.2, 0.2]})
        >>> get_variable_names(df)
        ['x', 'ux', 'y', 'uy']
        >>> get_variable_names(df, filter_uncertainty=True)
        ['x', 'y']
    """
    variable_names = list(data.columns)
    if not filter_uncertainty:
        return variable_names

    filtered: List[str] = []
    excluded: set = set()

    for var in variable_names:
        if var in excluded:
            continue
        if var.startswith('u') and len(var) > 1:
            base_var = var[1:]
            if base_var in variable_names:
                excluded.add(var)
                continue
        u_var = f'u{var}'
        if u_var in variable_names:
            excluded.add(u_var)
        filtered.append(var)

    return filtered if filtered else variable_names


def get_file_list_by_type(file_type: str, csv: list, xls: list, xlsx: list) -> list:
    """
    Get list of files based on selected type.
    
    This function acts as a selector/router that returns the appropriate
    file list based on the user's file type selection.
    
    Args:
        file_type: File type ('csv', 'xls', 'xlsx')
        csv: List of CSV file names (without extension)
        xls: List of XLS file names (without extension)
        xlsx: List of XLSX file names (without extension)
        
    Returns:
        List of files of the specified type
        
    Raises:
        InvalidFileTypeError: If file type is not valid
        
    Example:
        >>> csv_files = ['data1', 'data2']
        >>> xlsx_files = ['experiment1', 'experiment2']
        >>> get_file_list_by_type('csv', csv_files, [], xlsx_files)
        ['data1', 'data2']
    """
    logger.debug(f"Getting file list for type: {file_type}")
    
    # Validate file type
    validate_file_type(file_type)
    
    # Dictionary mapping file types to their corresponding lists
    file_lists = {
        'csv': csv,
        'xls': xls,
        'xlsx': xlsx
    }
    
    # Validate file type again (redundant but safe)
    if file_type not in file_lists:
        logger.error(f"Invalid file type: {file_type}")
        raise InvalidFileTypeError(f"Tipo de archivo no válido: {file_type}")
    
    # Return the appropriate list
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
        filename: File name without extension (e.g., 'Ejemplo')
        file_type: File type ('csv', 'xls', 'xlsx')
        
    Returns:
        Tuple of (data DataFrame, complete file path)
        The file path is returned so it can be used for reloading in loop mode
        
    Raises:
        DataLoadError: If data cannot be loaded
        
    Example:
        >>> data, path = load_data_workflow('Ejemplo', 'xlsx')
        >>> print(data.head())
        >>> print(f"Loaded from: {path}")
    """
    logger.info(f"Starting data loading workflow: {filename}.{file_type}")
    
    try:
        # Step 1: Construct the complete file path
        file_path = prepare_data_path(filename, file_type)
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
