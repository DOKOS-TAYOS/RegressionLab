#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for loading_utils module.
"""

import pytest
import tempfile
import pandas as pd
import csv
from pathlib import Path

from loaders.loading_utils import csv_reader, excel_reader
from utils.exceptions import DataLoadError


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
