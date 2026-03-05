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

    def test_empty_csv_raises_data_load_error(self) -> None:
        """Test empty CSV file raises DataLoadError (EmptyDataError path)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tf:
            tf.write('')  # Empty file
        try:
            with pytest.raises(DataLoadError):
                csv_reader(tf.name)
        finally:
            Path(tf.name).unlink(missing_ok=True)

    def test_malformed_csv_raises_data_load_error(self) -> None:
        """Test malformed CSV raises DataLoadError (ParserError path)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tf:
            tf.write('x,y\n"unclosed,quote\n1,2\n')  # Unclosed quote
        try:
            with pytest.raises(DataLoadError):
                csv_reader(tf.name)
        finally:
            Path(tf.name).unlink(missing_ok=True)


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

    def test_empty_txt_raises_data_load_error(self) -> None:
        """Test empty TXT file raises DataLoadError (EmptyDataError path)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tf:
            tf.write('')
        try:
            with pytest.raises(DataLoadError):
                txt_reader(tf.name)
        finally:
            Path(tf.name).unlink(missing_ok=True)

    def test_malformed_txt_raises_data_load_error(self) -> None:
        """Test malformed TXT raises DataLoadError (ParserError path)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tf:
            tf.write('x\ty\n"bad\tdata\n')  # Unclosed quote causes parse error
        try:
            with pytest.raises(DataLoadError):
                txt_reader(tf.name)
        finally:
            Path(tf.name).unlink(missing_ok=True)


class TestExcelReaderErrors:
    """Tests for excel_reader error paths."""

    def test_invalid_excel_raises_data_load_error(self) -> None:
        """Test invalid/corrupted Excel file raises DataLoadError."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx') as tf:
            tf.write(b'not a valid xlsx file')
        try:
            with pytest.raises(DataLoadError):
                excel_reader(tf.name)
        finally:
            Path(tf.name).unlink(missing_ok=True)
