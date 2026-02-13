"""Shared utilities for data analysis (transforms, cleaning)."""

from typing import List, Optional

import pandas as pd


def get_numeric_columns(
    data: pd.DataFrame, columns: Optional[List[str]] = None
) -> List[str]:
    """
    Return numeric column names from data, optionally filtered by columns.

    Args:
        data: DataFrame to extract numeric columns from.
        columns: Optional list of column names to filter. If None, returns all
            numeric columns.

    Returns:
        List of column names that are numeric (and in columns if specified).
    """
    if columns is None:
        return list(data.select_dtypes(include=["number"]).columns)
    return [
        c
        for c in columns
        if c in data.columns and pd.api.types.is_numeric_dtype(data[c])
    ]
