"""
Tests for data_loader module.
"""

import pandas as pd

from loaders import get_variable_names


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
