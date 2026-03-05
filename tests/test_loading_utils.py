"""
Tests for loading_utils module.
"""

import csv
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from loaders import csv_reader, excel_reader, txt_reader
from utils import DataLoadError


@pytest.fixture
def csv_file() -> str:
    """Create temporary CSV file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    writer = csv.writer(temp_file)
    writer.writerow(['x', 'ux', 'y', 'uy'])
    writer.writerow([1.0, 0.1, 2.0, 0.2])
    writer.writerow([2.0, 0.1, 4.0, 0.2])
    writer.writerow([3.0, 0.1, 6.0, 0.2])
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
def excel_file() -> str:
    """Create temporary Excel file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()
    
    df = pd.DataFrame({
        'x': [1.0, 2.0, 3.0],
        'ux': [0.1, 0.1, 0.1],
        'y': [2.0, 4.0, 6.0],
        'uy': [0.2, 0.2, 0.2]
    })
    df.to_excel(temp_file.name, index=False)
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
def txt_file() -> str:
    """Create temporary TXT file for testing (tab-separated)."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.write('x\tux\ty\tuy\n')
    temp_file.write('1.0\t0.1\t2.0\t0.2\n')
    temp_file.write('2.0\t0.1\t4.0\t0.2\n')
    temp_file.write('3.0\t0.1\t6.0\t0.2\n')
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


class TestCsvReader:
    """Tests for csv_reader function."""
    
    def test_read_valid_csv(self, csv_file: str) -> None:
        """Test reading valid CSV file."""
        df = csv_reader(csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'x' in df.columns
        assert 'y' in df.columns
    
    def test_nonexistent_file(self) -> None:
        """Test reading nonexistent file raises error."""
        with pytest.raises(DataLoadError):
            csv_reader('/nonexistent/file.csv')


class TestExcelReader:
    """Tests for excel_reader function."""
    
    def test_read_valid_excel(self, excel_file: str) -> None:
        """Test reading valid Excel file."""
        df = excel_reader(excel_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'x' in df.columns
        assert 'y' in df.columns
    
    def test_nonexistent_file(self) -> None:
        """Test reading nonexistent file raises error."""
        with pytest.raises(DataLoadError):
            excel_reader('/nonexistent/file.xlsx')


class TestTxtReader:
    """Tests for txt_reader function."""
    
    def test_read_valid_txt(self, txt_file: str) -> None:
        """Test reading valid TXT file."""
        df = txt_reader(txt_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'x' in df.columns
        assert 'y' in df.columns
    
    def test_nonexistent_file(self) -> None:
        """Test reading nonexistent file raises error."""
        with pytest.raises(DataLoadError):
            txt_reader('/nonexistent/file.txt')
