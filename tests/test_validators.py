"""
Tests for validators module.
"""

import pytest
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

from utils import (
    validate_file_path,
    validate_file_type,
    validate_dataframe,
    validate_data_format,
    validate_fitting_data,
    validate_parameter_names,
    parse_optional_float,
    DataValidationError,
    FileNotFoundError,
    InvalidFileTypeError,
    ValidationError,
)
from utils.validators import (
    _validate_column_exists,
    _validate_numeric_data,
    _validate_uncertainty_column,
    _validate_positive_integer,
)


class TestValidateFilePath:
    """Tests for validate_file_path function."""
    
    def test_valid_file_path(self) -> None:
        """Test validation passes for valid file."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_path = tf.name
        try:
            validate_file_path(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_nonexistent_file(self) -> None:
        """Test validation fails for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            validate_file_path('/nonexistent/path/file.txt')
    
    def test_directory_path(self) -> None:
        """Test validation fails for directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError):
                validate_file_path(temp_dir)


class TestValidateFileType:
    """Tests for validate_file_type function."""
    
    @pytest.mark.parametrize("file_type", ['csv', 'xlsx', 'txt'])
    def test_valid_types(self, file_type: str) -> None:
        """Test validation passes for valid types."""
        validate_file_type(file_type)
    
    def test_invalid_type(self) -> None:
        """Test validation fails for invalid type."""
        with pytest.raises(InvalidFileTypeError):
            validate_file_type('pdf')
    
    def test_custom_allowed_types(self) -> None:
        """Test validation with custom allowed types."""
        validate_file_type('txt', allowed_types=['txt', 'dat'])
        with pytest.raises(InvalidFileTypeError):
            validate_file_type('csv', allowed_types=['txt', 'dat'])


class TestValidateDataFrame:
    """Tests for validate_dataframe function."""
    
    def test_valid_dataframe(self) -> None:
        """Test validation passes for valid DataFrame."""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        validate_dataframe(df)
    
    def test_none_dataframe(self) -> None:
        """Test validation fails for None."""
        with pytest.raises(DataValidationError):
            validate_dataframe(None)
    
    def test_empty_dataframe(self) -> None:
        """Test validation fails for empty DataFrame."""
        with pytest.raises(DataValidationError):
            validate_dataframe(pd.DataFrame())
    
    def test_insufficient_rows(self) -> None:
        """Test validation fails for insufficient rows."""
        df = pd.DataFrame({'x': [1], 'y': [2]})
        with pytest.raises(DataValidationError):
            validate_dataframe(df, min_rows=2)


class TestValidateColumnExists:
    """Tests for _validate_column_exists function."""
    
    def test_existing_column(self) -> None:
        """Test validation passes for existing column."""
        df = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        _validate_column_exists(df, 'x')
    
    def test_missing_column(self) -> None:
        """Test validation fails for missing column."""
        df = pd.DataFrame({'x': [1, 2]})
        with pytest.raises(DataValidationError):
            _validate_column_exists(df, 'y')


class TestValidateNumericData:
    """Tests for _validate_numeric_data function."""
    
    @pytest.mark.parametrize("data", [
        pd.Series([1.0, 2.0, 3.0]),
        pd.Series([1, 2, 3]),
    ])
    def test_valid_numeric(self, data: pd.Series) -> None:
        """Test validation passes for numeric data."""
        _validate_numeric_data(data, 'test_col')
    
    def test_non_numeric(self) -> None:
        """Test validation fails for non-numeric data."""
        with pytest.raises(DataValidationError):
            _validate_numeric_data(pd.Series(['a', 'b', 'c']), 'test_col')
    
    @pytest.mark.parametrize("data", [
        pd.Series([1.0, np.nan, 3.0]),
        pd.Series([1.0, np.inf, 3.0]),
    ])
    def test_invalid_values(self, data: pd.Series) -> None:
        """Test validation fails for NaN or infinite values."""
        with pytest.raises(DataValidationError):
            _validate_numeric_data(data, 'test_col')


class TestValidateUncertaintyColumn:
    """Tests for _validate_uncertainty_column function."""
    
    def test_valid_uncertainty(self) -> None:
        """Test validation passes for valid uncertainty column."""
        df = pd.DataFrame({'x': [1, 2, 3], 'ux': [0.1, 0.1, 0.1]})
        _validate_uncertainty_column(df, 'x')
    
    def test_missing_uncertainty(self) -> None:
        """Test validation fails for missing uncertainty column."""
        df = pd.DataFrame({'x': [1, 2, 3]})
        with pytest.raises(DataValidationError):
            _validate_uncertainty_column(df, 'x')
    
    def test_negative_uncertainty(self) -> None:
        """Test validation fails for negative uncertainties."""
        df = pd.DataFrame({'x': [1, 2, 3], 'ux': [0.1, -0.1, 0.1]})
        with pytest.raises(DataValidationError):
            _validate_uncertainty_column(df, 'x')


class TestValidateFittingData:
    """Tests for validate_fitting_data function."""
    
    @pytest.fixture
    def valid_data(self) -> pd.DataFrame:
        """Fixture for valid fitting data."""
        return pd.DataFrame({
            'x': [1.0, 2.0, 3.0],
            'ux': [0.1, 0.1, 0.1],
            'y': [2.0, 4.0, 6.0],
            'uy': [0.2, 0.2, 0.2]
        })
    
    def test_valid_fitting_data(self, valid_data: pd.DataFrame) -> None:
        """Test validation passes for valid fitting data."""
        validate_fitting_data(valid_data, 'x', 'y')
    
    def test_missing_x_column(self) -> None:
        """Test validation fails for missing x column."""
        df = pd.DataFrame({
            'y': [2.0, 4.0, 6.0],
            'uy': [0.2, 0.2, 0.2]
        })
        with pytest.raises(DataValidationError):
            validate_fitting_data(df, 'x', 'y')
    
    def test_missing_uncertainty(self) -> None:
        """Test validation fails for missing uncertainty columns."""
        df = pd.DataFrame({
            'x': [1.0, 2.0, 3.0],
            'y': [2.0, 4.0, 6.0]
        })
        with pytest.raises(DataValidationError):
            validate_fitting_data(df, 'x', 'y')


class TestValidateParameterNames:
    """Tests for validate_parameter_names function."""
    
    def test_valid_names(self) -> None:
        """Test validation passes for valid parameter names."""
        validate_parameter_names(['a', 'b', 'c'])
    
    def test_empty_list(self) -> None:
        """Test validation fails for empty list."""
        with pytest.raises(ValidationError):
            validate_parameter_names([])
    
    def test_duplicate_names(self) -> None:
        """Test validation fails for duplicate names."""
        with pytest.raises(ValidationError):
            validate_parameter_names(['a', 'b', 'a'])
    
    @pytest.mark.parametrize("invalid_name", ['123invalid', 'my-param'])
    def test_invalid_identifier(self, invalid_name: str) -> None:
        """Test validation fails for invalid Python identifiers."""
        with pytest.raises(ValidationError):
            validate_parameter_names([invalid_name])


class TestValidateDataFormat:
    """Tests for validate_data_format function."""
    
    def test_valid_data_format(self) -> None:
        """Test validation passes for valid DataFrame."""
        df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [4.0, 5.0, 6.0]})
        validate_data_format(df)
    
    def test_none_dataframe(self) -> None:
        """Test validation fails for None."""
        with pytest.raises(DataValidationError):
            validate_data_format(None)
    
    def test_empty_dataframe(self) -> None:
        """Test validation fails for empty DataFrame."""
        with pytest.raises(DataValidationError):
            validate_data_format(pd.DataFrame())
    
    def test_non_numeric_columns(self) -> None:
        """Test validation fails for non-numeric columns."""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': ['a', 'b', 'c']})
        with pytest.raises(DataValidationError):
            validate_data_format(df)
    
    def test_duplicate_column_names(self) -> None:
        """Test validation fails for duplicate column names."""
        df = pd.DataFrame([[1, 4], [2, 5], [3, 6]], columns=['x', 'x'])
        with pytest.raises(DataValidationError):
            validate_data_format(df)


class TestParseOptionalFloat:
    """Tests for parse_optional_float function."""
    
    @pytest.mark.parametrize("value,expected", [
        ('1.5', 1.5),
        ('0', 0.0),
        ('-3.14', -3.14),
        ('1e-3', 0.001),
    ])
    def test_valid_float_strings(self, value: str, expected: float) -> None:
        """Test parsing valid float strings."""
        result = parse_optional_float(value)
        assert result is not None
        assert abs(result - expected) < 1e-10
    
    @pytest.mark.parametrize("value", ['', '   '])
    def test_empty_returns_none(self, value: str) -> None:
        """Test empty or whitespace returns None."""
        assert parse_optional_float(value) is None
    
    @pytest.mark.parametrize("value", ['abc', 'not_a_number', '1.2.3'])
    def test_invalid_returns_none(self, value: str) -> None:
        """Test invalid strings return None."""
        assert parse_optional_float(value) is None


class TestValidatePositiveInteger:
    """Tests for _validate_positive_integer function."""
    
    def test_valid_positive_integer(self) -> None:
        """Test validation passes for positive integer."""
        assert _validate_positive_integer(5, 'test_param') == 5
    
    def test_string_number(self) -> None:
        """Test validation passes for string number."""
        assert _validate_positive_integer('10', 'test_param') == 10
    
    @pytest.mark.parametrize("value", [0, -5])
    def test_non_positive(self, value: int) -> None:
        """Test validation fails for zero or negative."""
        with pytest.raises(ValidationError):
            _validate_positive_integer(value, 'test_param')
    
    def test_non_integer(self) -> None:
        """Test validation fails for non-integer."""
        with pytest.raises(ValidationError):
            _validate_positive_integer('not_a_number', 'test_param')
