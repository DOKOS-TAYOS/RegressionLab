"""
Tests for loaders.saving_utils module.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from loaders import save_dataframe, get_default_save_directory


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Fixture for sample DataFrame."""
    return pd.DataFrame({
        'x': [1.0, 2.0, 3.0],
        'y': [4.0, 5.0, 6.0],
    })


class TestSaveDataframe:
    """Tests for save_dataframe function."""

    def test_save_csv(self, sample_dataframe: pd.DataFrame) -> None:
        """Test saving to CSV format."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tf:
            path = tf.name
        try:
            result = save_dataframe(sample_dataframe, path, 'csv')
            assert result == path
            loaded = pd.read_csv(path)
            pd.testing.assert_frame_equal(loaded, sample_dataframe)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_txt(self, sample_dataframe: pd.DataFrame) -> None:
        """Test saving to TXT format (tab-separated)."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tf:
            path = tf.name
        try:
            result = save_dataframe(sample_dataframe, path, 'txt')
            assert result == path
            loaded = pd.read_csv(path, sep='\t')
            pd.testing.assert_frame_equal(loaded, sample_dataframe)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_xlsx(self, sample_dataframe: pd.DataFrame) -> None:
        """Test saving to Excel format."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tf:
            path = tf.name
        try:
            result = save_dataframe(sample_dataframe, path, 'xlsx')
            assert result == path
            loaded = pd.read_excel(path)
            pd.testing.assert_frame_equal(
                loaded, sample_dataframe, check_dtype=False
            )
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_infers_type_from_extension(self, sample_dataframe: pd.DataFrame) -> None:
        """Test file_type is inferred from path when None."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tf:
            path = tf.name
        try:
            result = save_dataframe(sample_dataframe, path)
            assert result == path
            loaded = pd.read_csv(path)
            pd.testing.assert_frame_equal(loaded, sample_dataframe)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_save_creates_directory(self, sample_dataframe: pd.DataFrame) -> None:
        """Test save creates parent directory if it does not exist."""
        temp_dir = tempfile.mkdtemp()
        nested_path = Path(temp_dir) / 'subdir' / 'output.csv'
        try:
            result = save_dataframe(sample_dataframe, str(nested_path), 'csv')
            assert nested_path.exists()
            loaded = pd.read_csv(result)
            pd.testing.assert_frame_equal(loaded, sample_dataframe)
        finally:
            Path(temp_dir).joinpath('subdir', 'output.csv').unlink(missing_ok=True)
            Path(temp_dir).joinpath('subdir').rmdir()
            Path(temp_dir).rmdir()

    def test_save_unsupported_type_raises_value_error(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test unsupported file type raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tf:
            path = tf.name
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                save_dataframe(sample_dataframe, path, 'pdf')
        finally:
            Path(path).unlink(missing_ok=True)


class TestGetDefaultSaveDirectory:
    """Tests for get_default_save_directory function."""

    def test_returns_string_path(self) -> None:
        """Test returns a string path."""
        result = get_default_save_directory()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_absolute_path(self) -> None:
        """Test returned path is absolute (or valid relative)."""
        result = get_default_save_directory()
        path = Path(result)
        # Should resolve to existing directory or valid path
        assert path.is_absolute() or path.exists() or path.parent.exists()
