"""
Tests for data_analysis.cleaning module.
"""

import numpy as np
import pandas as pd
import pytest

from data_analysis.cleaning import (
    CLEAN_DROP_NA,
    CLEAN_DROP_DUPLICATES,
    CLEAN_FILL_NA_MEAN,
    CLEAN_FILL_NA_MEDIAN,
    CLEAN_FILL_NA_ZERO,
    CLEAN_REMOVE_OUTLIERS_IQR,
    CLEAN_REMOVE_OUTLIERS_ZSCORE,
    CLEAN_OPTIONS,
    apply_cleaning,
)


class TestApplyCleaningDropNa:
    """Tests for CLEAN_DROP_NA."""

    def test_drop_na_removes_rows_with_nan(self) -> None:
        """Test drop_na removes rows containing NaN."""
        df = pd.DataFrame({'x': [1.0, np.nan, 3.0], 'y': [4.0, 5.0, 6.0]})
        result = apply_cleaning(df, CLEAN_DROP_NA)
        assert len(result) == 2
        assert result['x'].isna().sum() == 0

    def test_drop_na_empty_result_when_all_nan(self) -> None:
        """Test drop_na returns empty when all rows have NaN."""
        df = pd.DataFrame({'x': [np.nan, np.nan], 'y': [np.nan, np.nan]})
        result = apply_cleaning(df, CLEAN_DROP_NA)
        assert len(result) == 0


class TestApplyCleaningDropDuplicates:
    """Tests for CLEAN_DROP_DUPLICATES."""

    def test_drop_duplicates_removes_duplicate_rows(self) -> None:
        """Test drop_duplicates removes duplicate rows."""
        df = pd.DataFrame({'x': [1.0, 2.0, 2.0, 3.0], 'y': [4.0, 5.0, 5.0, 6.0]})
        result = apply_cleaning(df, CLEAN_DROP_DUPLICATES)
        assert len(result) == 3

    def test_drop_duplicates_no_change_when_all_unique(self) -> None:
        """Test drop_duplicates leaves data unchanged when no duplicates."""
        df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [4.0, 5.0, 6.0]})
        result = apply_cleaning(df, CLEAN_DROP_DUPLICATES)
        assert len(result) == 3


class TestApplyCleaningFillNa:
    """Tests for fill operations."""

    def test_fill_na_mean(self) -> None:
        """Test fill NaN with column mean."""
        df = pd.DataFrame({'x': [1.0, np.nan, 3.0], 'y': [4.0, 5.0, 6.0]})
        result = apply_cleaning(df, CLEAN_FILL_NA_MEAN)
        assert result['x'].isna().sum() == 0
        assert abs(result['x'].iloc[1] - 2.0) < 1e-10  # mean of 1 and 3

    def test_fill_na_median(self) -> None:
        """Test fill NaN with column median."""
        df = pd.DataFrame({'x': [1.0, np.nan, 5.0], 'y': [4.0, 5.0, 6.0]})
        result = apply_cleaning(df, CLEAN_FILL_NA_MEDIAN)
        assert result['x'].isna().sum() == 0
        assert abs(result['x'].iloc[1] - 3.0) < 1e-10  # median of 1 and 5

    def test_fill_na_zero(self) -> None:
        """Test fill NaN with zero."""
        df = pd.DataFrame({'x': [1.0, np.nan, 3.0], 'y': [4.0, 5.0, 6.0]})
        result = apply_cleaning(df, CLEAN_FILL_NA_ZERO)
        assert result['x'].isna().sum() == 0
        assert result['x'].iloc[1] == 0.0

    def test_fill_na_with_columns(self) -> None:
        """Test fill NaN only in specified columns."""
        df = pd.DataFrame({
            'x': [1.0, np.nan, 3.0],
            'y': [np.nan, 5.0, 6.0],
            'z': [7.0, 8.0, 9.0],
        })
        result = apply_cleaning(df, CLEAN_FILL_NA_ZERO, columns=['x'])
        assert result['x'].isna().sum() == 0
        assert result['y'].isna().sum() == 1  # y not filled


class TestApplyCleaningOutliersIQR:
    """Tests for CLEAN_REMOVE_OUTLIERS_IQR."""

    def test_remove_outliers_iqr(self) -> None:
        """Test IQR method removes outliers."""
        # 1, 2, 3, 4, 5, 100 (100 is outlier)
        df = pd.DataFrame({'x': [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]})
        result = apply_cleaning(df, CLEAN_REMOVE_OUTLIERS_IQR)
        assert len(result) < 6
        assert 100.0 not in result['x'].values

    def test_remove_outliers_iqr_no_outliers(self) -> None:
        """Test IQR leaves data unchanged when no outliers."""
        df = pd.DataFrame({'x': [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = apply_cleaning(df, CLEAN_REMOVE_OUTLIERS_IQR)
        assert len(result) == 5


class TestApplyCleaningOutliersZScore:
    """Tests for CLEAN_REMOVE_OUTLIERS_ZSCORE."""

    def test_remove_outliers_zscore(self) -> None:
        """Test z-score method removes extreme outliers (|z| > 3)."""
        # 10 similar values + 1 extreme: mean ~1, std ~0 -> need many similar + 1 far
        # [1]*10 + [100]: mean=10.9, std~30, z(100)~3. Use larger gap.
        df = pd.DataFrame({'x': [1.0] * 10 + [10000.0]})
        result = apply_cleaning(df, CLEAN_REMOVE_OUTLIERS_ZSCORE)
        assert len(result) < 11
        assert 10000.0 not in result['x'].values

    def test_remove_outliers_zscore_constant_column(self) -> None:
        """Test z-score skips constant columns (std=0)."""
        df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [5.0, 5.0, 5.0]})
        result = apply_cleaning(df, CLEAN_REMOVE_OUTLIERS_ZSCORE)
        assert len(result) == 3


class TestApplyCleaningUnknown:
    """Tests for error handling."""

    def test_unknown_clean_id_raises_value_error(self) -> None:
        """Test unknown clean_id raises ValueError."""
        df = pd.DataFrame({'x': [1, 2, 3]})
        with pytest.raises(ValueError, match="Unknown cleaning"):
            apply_cleaning(df, 'unknown_operation')


class TestCleanOptions:
    """Tests for CLEAN_OPTIONS constant."""

    def test_clean_options_contains_all_constants(self) -> None:
        """Test CLEAN_OPTIONS has entries for all CLEAN_* constants."""
        constants = [
            CLEAN_DROP_NA,
            CLEAN_DROP_DUPLICATES,
            CLEAN_FILL_NA_MEAN,
            CLEAN_FILL_NA_MEDIAN,
            CLEAN_FILL_NA_ZERO,
            CLEAN_REMOVE_OUTLIERS_IQR,
            CLEAN_REMOVE_OUTLIERS_ZSCORE,
        ]
        for c in constants:
            assert c in CLEAN_OPTIONS
            assert isinstance(CLEAN_OPTIONS[c], str)
