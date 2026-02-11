"""
Tests for data_loader module.
"""

import pytest
import pandas as pd
from pathlib import Path

from loaders import get_variable_names, get_file_list_by_type
from loaders.data_loader import _prepare_data_path as prepare_data_path
from utils import InvalidFileTypeError


class TestPrepareDataPath:
    """Tests for prepare_data_path function."""
    
    @pytest.mark.parametrize("file_type,expected_ext", [
        ('csv', '.csv'),
        ('xlsx', '.xlsx'),
        ('txt', '.txt'),
    ])
    def test_file_paths(self, file_type: str, expected_ext: str) -> None:
        """Test preparing paths for different file types."""
        path = prepare_data_path('test_file', file_type)
        assert isinstance(path, str)
        assert path.endswith(expected_ext)
        assert 'test_file' in path
        assert Path(path).is_absolute()
    
    def test_custom_base_dir(self) -> None:
        """Test preparing path with custom base directory."""
        path = prepare_data_path('test_file', 'csv', base_dir='custom_dir')
        assert 'custom_dir' in path


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


class TestGetFileListByType:
    """Tests for get_file_list_by_type function."""
    
    @pytest.fixture
    def file_lists(self) -> dict[str, list[str]]:
        """Fixture providing test file lists."""
        return {
            'csv': ['file1', 'file2'],
            'xlsx': ['file4', 'file5', 'file6'],
            'txt': ['file7']
        }
    
    @pytest.mark.parametrize("file_type", ['csv', 'xlsx', 'txt'])
    def test_get_files_by_type(self, file_type: str, file_lists: dict[str, list[str]]) -> None:
        """Test getting file list by type."""
        result = get_file_list_by_type(
            file_type,
            file_lists['csv'],
            file_lists['xlsx'],
            file_lists['txt']
        )
        assert result == file_lists[file_type]
    
    def test_invalid_file_type(self, file_lists: dict[str, list[str]]) -> None:
        """Test invalid file type raises error."""
        with pytest.raises(InvalidFileTypeError):
            get_file_list_by_type(
                'pdf',
                file_lists['csv'],
                file_lists['xlsx'],
                file_lists['txt']
            )
    
    def test_empty_lists(self) -> None:
        """Test with empty file lists."""
        assert get_file_list_by_type('csv', [], [], []) == []
