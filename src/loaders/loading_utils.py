"""
Loading utilities for data file operations.

This module provides functions to:

    - Load data from CSV, TXT and Excel files
    - Scan directories for available data files
    - Get the project root directory path

All file operations are relative to the project root directory.
"""

# Standard library
from typing import List, Optional, Tuple

# Third-party packages
import pandas as pd

# Local imports
from config import FILE_CONFIG, get_project_root
from i18n import t
from utils import (
    DataLoadError,
    FileNotFoundError,
    get_logger,
    validate_dataframe,
    validate_data_format,
    validate_file_path,
)

logger = get_logger(__name__)


def csv_reader(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with the CSV data, treating 'no' as NaN values
        
    Raises:
        FileNotFoundError: If file does not exist
        DataLoadError: If file cannot be read
    """
    logger.info(t('log.loading_csv_file', path=file_path))
    
    # Validate file exists
    validate_file_path(file_path)
    
    try:
        data = pd.read_csv(file_path, na_values=['no'])
        validate_dataframe(data)
        validate_data_format(data)
        logger.info(t('log.successfully_loaded_csv', rows=len(data), columns=len(data.columns)))
        return data
    except pd.errors.EmptyDataError:
        logger.error(t('log.csv_file_empty', path=file_path))
        raise DataLoadError(t('error.csv_file_empty', path=file_path))
    except pd.errors.ParserError as e:
        logger.error(t('log.csv_parsing_error', path=file_path, error=str(e)))
        raise DataLoadError(t('error.csv_parsing_error', error=str(e)))
    except Exception as e:
        logger.error(
            t('log.unexpected_error_reading_csv', path=file_path, error=str(e)),
            exc_info=True
        )
        raise DataLoadError(t('error.unexpected_loading_csv', error=str(e)))


def txt_reader(file_path: str) -> pd.DataFrame:
    """
    Load data from a text file (whitespace or tab separated).

    Uses pandas read_csv with sep=None (delimiter sniffing) so that
    tab-separated and space-separated values are detected automatically.

    Args:
        file_path: Path to the text file.

    Returns:
        DataFrame with the text file data, treating 'no' as NaN values.

    Raises:
        FileNotFoundError: If file does not exist
        DataLoadError: If file cannot be read
    """
    logger.info(t('log.loading_txt_file', path=file_path))

    validate_file_path(file_path)

    try:
        # sep=None triggers Python engine's delimiter sniffing (tab, space, etc.)
        data = pd.read_csv(file_path, sep=None, engine='python', na_values=['no'])
        validate_dataframe(data)
        validate_data_format(data)
        logger.info(t('log.successfully_loaded_txt', rows=len(data), columns=len(data.columns)))
        return data
    except pd.errors.EmptyDataError:
        logger.error(t('log.csv_file_empty', path=file_path))
        raise DataLoadError(t('error.csv_file_empty', path=file_path))
    except pd.errors.ParserError as e:
        logger.error(t('log.csv_parsing_error', path=file_path, error=str(e)))
        raise DataLoadError(t('error.csv_parsing_error', error=str(e)))
    except Exception as e:
        logger.error(
            t('log.unexpected_error_reading_csv', path=file_path, error=str(e)),
            exc_info=True
        )
        raise DataLoadError(t('error.unexpected_loading_csv', error=str(e)))


def excel_reader(file_path: str) -> pd.DataFrame:
    """
    Load data from an Excel file (.xlsx).
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        DataFrame with the Excel data
        
    Raises:
        FileNotFoundError: If file does not exist
        DataLoadError: If file cannot be read
    """
    logger.info(t('log.loading_excel_file', path=file_path))
    
    # Validate file exists
    validate_file_path(file_path)
    
    try:
        data = pd.read_excel(file_path)
        validate_dataframe(data)
        validate_data_format(data)
        logger.info(t('log.successfully_loaded_excel', rows=len(data), columns=len(data.columns)))
        return data
    except Exception as e:
        logger.error(t('log.error_reading_excel', path=file_path, error=str(e)), exc_info=True)
        raise DataLoadError(t('error.loading_excel_file', error=str(e)))


def get_file_names(
    directory: Optional[str] = None,
) -> Tuple[List[str], List[str], List[str]]:
    """
    Get categorized file names from a directory.
    
    Scans the specified directory and categorizes files by extension,
    returning file names without their extensions. This allows the UI
    to present clean file names to the user while the full path can
    be reconstructed when needed.
    
    Args:
        directory: Name of the directory to scan (default: None, relative to project root)
        
    Returns:
        Tuple of three lists: (csv_files, xlsx_files, txt_files)
        Each list contains file names without extensions
        
    Raises:
        FileNotFoundError: If directory does not exist
        
    Examples:
        >>> csv, xlsx, txt = get_file_names()
        >>> # If 'input' contains 'data.csv' and 'experiment.xlsx':
        >>> print(csv)  # ['data']
        >>> print(xlsx)  # ['experiment']
    """
    
    # Get base directory from environment variable if not specified
    if directory is None:
        directory = FILE_CONFIG['input_dir']

    logger.debug(t('log.scanning_directory', directory=directory))
    
    # Use pathlib for cross-platform path handling, relative to project root
    project_root = get_project_root()
    file_path = project_root / directory
    
    # Check if directory exists
    if not file_path.exists():
        logger.error(t('log.directory_not_exist', path=str(file_path)))
        raise FileNotFoundError(t('error.directory_not_exist', directory=directory))
    
    if not file_path.is_dir():
        logger.error(t('log.path_not_directory', path=str(file_path)))
        raise DataLoadError(t('error.path_not_directory', directory=directory))
    
    try:
        by_ext: dict[str, List[str]] = {'.csv': [], '.xlsx': [], '.txt': []}
        for path in file_path.iterdir():
            if path.is_file() and path.suffix in by_ext:
                by_ext[path.suffix].append(path.stem)

        csv, xlsx, txt = by_ext['.csv'], by_ext['.xlsx'], by_ext['.txt']
        logger.info(t('log.found_files', csv=len(csv), xlsx=len(xlsx), txt=len(txt)))
        return csv, xlsx, txt
        
    except PermissionError:
        logger.error(t('log.permission_denied_directory', path=str(file_path)))
        raise DataLoadError(t('error.permission_denied_directory', directory=directory))
    except Exception as e:
        logger.error(
            t('log.error_scanning_directory', path=str(file_path), error=str(e)),
            exc_info=True
        )
        raise DataLoadError(t('error.scanning_directory', error=str(e)))
