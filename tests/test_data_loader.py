"""
Tests for data_loader module.
"""

import csv
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from loaders import get_variable_names, load_data
from utils import DataLoadError, InvalidFileTypeError


@pytest.fixture
def csv_file() -> str:
    """Create temporary CSV file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    writer = csv.writer(temp_file)
    writer.writerow(['x', 'y'])
    writer.writerow([1.0, 2.0])
    writer.writerow([2.0, 4.0])
    writer.writerow([3.0, 6.0])
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
def excel_file() -> str:
    """Create temporary Excel file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()
    df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [2.0, 4.0, 6.0]})
    df.to_excel(temp_file.name, index=False)
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
def txt_file() -> str:
    """Create temporary TXT file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.write('x\ty\n')
    temp_file.write('1.0\t2.0\n')
    temp_file.write('2.0\t4.0\n')
    temp_file.write('3.0\t6.0\n')
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


class TestLoadData:
    """Tests for load_data function."""

    def test_load_csv(self, csv_file: str) -> None:
        """Test loading CSV file."""
        df = load_data(csv_file, 'csv')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['x', 'y']

    def test_load_xlsx(self, excel_file: str) -> None:
        """Test loading Excel file."""
        df = load_data(excel_file, 'xlsx')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_load_txt(self, txt_file: str) -> None:
        """Test loading TXT file."""
        df = load_data(txt_file, 'txt')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['x', 'y']

    def test_invalid_file_type(self, csv_file: str) -> None:
        """Test that invalid file type raises InvalidFileTypeError."""
        with pytest.raises(InvalidFileTypeError):
            load_data(csv_file, 'pdf')

    def test_nonexistent_file(self) -> None:
        """Test that nonexistent file raises DataLoadError."""
        with pytest.raises(DataLoadError):
            load_data('/nonexistent/path/file.csv', 'csv')


class TestGetVariableNames:
    """Tests for get_variable_names function."""
    
    def test_simple_dataframe(self) -> None:
        """Test getting variable names from simple DataFrame."""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        names = get_variable_names(df)
        assert names == ['x', 'y']
    
    def test_with_uncertainties(self) -> None:
        """Test getting variable names including uncertainties."""
        df = pd.DataFrame({
            'x': [1, 2, 3],
            'ux': [0.1, 0.1, 0.1],
            'y': [4, 5, 6],
            'uy': [0.2, 0.2, 0.2]
        })
        names = get_variable_names(df)
        assert set(names) == {'x', 'ux', 'y', 'uy'}
    
    def test_empty_dataframe(self) -> None:
        """Test getting variable names from empty DataFrame."""
        df = pd.DataFrame()
        assert get_variable_names(df) == []

    def test_filter_uncertainty_excludes_ux_uy(self) -> None:
        """Test filter_uncertainty=True excludes uncertainty columns."""
        df = pd.DataFrame({
            'x': [1, 2, 3],
            'ux': [0.1, 0.1, 0.1],
            'y': [4, 5, 6],
            'uy': [0.2, 0.2, 0.2],
        })
        names = get_variable_names(df, filter_uncertainty=True)
        assert names == ['x', 'y']

    def test_filter_uncertainty_preserves_order(self) -> None:
        """Test filter_uncertainty preserves column order."""
        df = pd.DataFrame({
            'a': [1], 'ua': [0.1], 'b': [2], 'ub': [0.2], 'c': [3],
        })
        names = get_variable_names(df, filter_uncertainty=True)
        assert names == ['a', 'b', 'c']
