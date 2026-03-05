"""
Loading utilities for data file operations.

This module provides functions to load data from CSV, TXT and Excel files.
"""

# Third-party packages
import pandas as pd

# Local imports
from i18n import t
from utils import (
    DataLoadError,
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
