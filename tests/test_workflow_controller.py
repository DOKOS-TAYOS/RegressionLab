"""
Tests for workflow_controller module.
"""

import csv
import pytest
import tempfile
import pandas as pd
from pathlib import Path

from fitting.workflow_controller import (
    reload_data_by_type,
    apply_all_equations
)
from utils import DataLoadError


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

    df = pd.DataFrame({
        'x': [1.0, 2.0, 3.0],
        'y': [2.0, 4.0, 6.0]
    })
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


@pytest.fixture
def test_data() -> pd.DataFrame:
    """Fixture for test data."""
    return pd.DataFrame({
        'x': [1.0, 2.0, 3.0],
        'ux': [0.1, 0.1, 0.1],
        'y': [2.0, 4.0, 6.0],
        'uy': [0.2, 0.2, 0.2]
    })


class TestReloadDataByType:
    """Tests for reload_data_by_type function."""

    def test_reload_csv(self, csv_file: str) -> None:
        """Test reloading CSV file."""
        df = reload_data_by_type(csv_file, 'csv')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['x', 'y']

    def test_reload_xlsx(self, excel_file: str) -> None:
        """Test reloading XLSX file."""
        df = reload_data_by_type(excel_file, 'xlsx')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_reload_txt(self, txt_file: str) -> None:
        """Test reloading TXT file."""
        df = reload_data_by_type(txt_file, 'txt')
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['x', 'y']
    
    def test_invalid_file_type(self, excel_file: str) -> None:
        """Test reloading with invalid file type raises error."""
        with pytest.raises(DataLoadError):
            reload_data_by_type(excel_file, 'invalid')
    
    def test_nonexistent_file(self) -> None:
        """Test reloading nonexistent file raises error."""
        with pytest.raises(DataLoadError):
            reload_data_by_type('/nonexistent/file.xlsx', 'xlsx')


class TestApplyAllEquations:
    """Tests for apply_all_equations function."""
    
    @pytest.fixture
    def equation_tracker(self) -> dict:
        """Fixture to track equation calls."""
        return {
            'current_equation': None,
            'fit_calls': []
        }
    
    def equation_setter(self, eq_type: str, tracker: dict) -> None:
        """Mock equation setter."""
        tracker['current_equation'] = eq_type
    
    def get_fitter(self, tracker: dict):
        """Mock fitter getter."""
        def mock_fitter(data, x_name, y_name, plot_name):
            tracker['fit_calls'].append({
                'equation': tracker['current_equation'],
                'x_name': x_name,
                'y_name': y_name,
                'plot_name': plot_name
            })
        return mock_fitter
    
    def test_apply_multiple_equations(self, test_data: pd.DataFrame, equation_tracker: dict) -> None:
        """Test applying multiple equations."""
        equation_types = ['eq1', 'eq2', 'eq3']
        
        apply_all_equations(
            equation_setter=lambda eq: self.equation_setter(eq, equation_tracker),
            get_fitter=lambda: self.get_fitter(equation_tracker),
            equation_types=equation_types,
            data=test_data,
            x_name='x',
            y_name='y',
            plot_name='test_plot'
        )
        
        assert len(equation_tracker['fit_calls']) == 3
        applied_equations = [call['equation'] for call in equation_tracker['fit_calls']]
        assert applied_equations == equation_types
    
    def test_apply_with_plot_name(self, test_data: pd.DataFrame, equation_tracker: dict) -> None:
        """Test applying equations with plot name."""
        equation_types = ['eq1']
        
        apply_all_equations(
            equation_setter=lambda eq: self.equation_setter(eq, equation_tracker),
            get_fitter=lambda: self.get_fitter(equation_tracker),
            equation_types=equation_types,
            data=test_data,
            x_name='x',
            y_name='y',
            plot_name='my_plot'
        )
        
        assert 'my_plot_eq1' in equation_tracker['fit_calls'][0]['plot_name']
    
    def test_apply_empty_list(self, test_data: pd.DataFrame, equation_tracker: dict) -> None:
        """Test applying empty equation list."""
        apply_all_equations(
            equation_setter=lambda eq: self.equation_setter(eq, equation_tracker),
            get_fitter=lambda: self.get_fitter(equation_tracker),
            equation_types=[],
            data=test_data,
            x_name='x',
            y_name='y',
            plot_name='test_plot'
        )
        
        assert len(equation_tracker['fit_calls']) == 0
