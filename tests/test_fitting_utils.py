"""
Tests for fitting_utils module.
"""

import pytest
import numpy as np
import pandas as pd

from config import EXIT_SIGNAL
from fitting.fitting_utils import (
    format_parameter,
    generic_fit,
    get_fitting_function,
)
from fitting.estimators import (
    estimate_phase_shift,
    estimate_trigonometric_parameters,
)
from fitting.fitting_functions import linear_function, sin_function
from utils import FittingError


class TestFormatParameter:
    """Tests for format_parameter function."""
    
    def test_normal_value(self) -> None:
        """Test formatting normal parameter value."""
        value, sigma = format_parameter(1.234567, 0.001)
        assert isinstance(value, float)
        assert isinstance(sigma, str)
    
    @pytest.mark.parametrize("sigma,expected", [
        (np.inf, '∞'),
        (np.nan, 'NaN'),
    ])
    def test_special_sigma_values(self, sigma: float, expected: str) -> None:
        """Test formatting with special sigma values."""
        _, sigma_str = format_parameter(1.0, sigma)
        assert sigma_str == expected
    
    def test_small_sigma(self) -> None:
        """Test formatting with very small uncertainty."""
        _, sigma = format_parameter(1.23456789, 1e-8)
        assert 'E' in sigma or 'e' in sigma


class TestEstimateTrigonometricParameters:
    """Tests for estimate_trigonometric_parameters function."""
    
    @pytest.mark.parametrize("x,y", [
        (np.linspace(0, 4*np.pi, 100), lambda x: 2.0 * np.sin(x)),
        (np.linspace(0, 4*np.pi, 100), lambda x: 3.0 * np.cos(2.0*x)),
    ])
    def test_parameter_estimation(self, x: np.ndarray, y: callable) -> None:
        """Test parameter estimation for trigonometric waves."""
        y_data = y(x)
        amplitude, frequency = estimate_trigonometric_parameters(x, y_data)
        assert isinstance(amplitude, float)
        assert isinstance(frequency, float)
        assert amplitude > 0
        assert frequency > 0
    
    def test_constant_data(self) -> None:
        """Test parameter estimation with constant data."""
        x = np.linspace(0, 10, 50)
        y = np.ones_like(x) * 5.0
        amplitude, frequency = estimate_trigonometric_parameters(x, y)
        assert isinstance(amplitude, float)
        assert isinstance(frequency, float)


class TestEstimatePhaseShift:
    """Tests for estimate_phase_shift function."""
    
    def test_phase_estimation(self) -> None:
        """Test phase shift estimation."""
        x = np.linspace(0, 4*np.pi, 100)
        y = 2.0 * np.sin(x + np.pi/4)
        phase = estimate_phase_shift(x, y, 2.0, 1.0)
        assert isinstance(phase, float)
        assert -np.pi <= phase <= np.pi
    
    def test_zero_amplitude(self) -> None:
        """Test phase estimation with zero amplitude."""
        x = np.linspace(0, 4*np.pi, 100)
        y = np.zeros_like(x)
        phase = estimate_phase_shift(x, y, 0.0, 1.0)
        assert isinstance(phase, float)


class TestGenericFit:
    """Tests for generic_fit function."""
    
    @pytest.fixture
    def test_data(self) -> pd.DataFrame:
        """Fixture for test data."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        return pd.DataFrame({
            'x': x,
            'ux': np.ones_like(x) * 0.1,
            'y': 2.0 * x,
            'uy': np.ones_like(x) * 0.2
        })
    
    def test_linear_fit(self, test_data: pd.DataFrame) -> None:
        """Test generic fit with linear function."""
        text, y_fitted, equation, fit_info = generic_fit(
            test_data,
            'x',
            'y',
            linear_function,
            ['m'],
            'y={m}x'
        )
        assert isinstance(text, str)
        assert isinstance(y_fitted, (np.ndarray, pd.Series))
        assert isinstance(equation, str)
        assert 'm=' in text
        assert 'R²=' in text
        assert fit_info is not None
        assert 'fit_func' in fit_info
        assert 'params' in fit_info
        assert 'cov' in fit_info
        assert 'x_names' in fit_info
    
    def test_fit_with_initial_guess(self, test_data: pd.DataFrame) -> None:
        """Test generic fit with initial parameter guess."""
        text, y_fitted, equation, _ = generic_fit(
            test_data,
            'x',
            'y',
            linear_function,
            ['m'],
            'y={m}x',
            initial_guess=[1.5]
        )
        assert isinstance(text, str)
        assert 'm=' in text
    
    def test_invalid_data(self) -> None:
        """Test generic fit with invalid data."""
        bad_data = pd.DataFrame({
            'x': np.array([1.0, 2.0]),
            'ux': np.array([0.1, 0.1])
        })
        with pytest.raises(FittingError):
            generic_fit(
                bad_data,
                'x',
                'y',
                linear_function,
                ['m'],
                'y={m}x'
            )
    
    def test_non_convergent_fit(self) -> None:
        """Test handling of non-convergent fit (linear data with sin model)."""
        bad_data = pd.DataFrame({
            'x': np.array([1.0, 2.0, 3.0]),
            'ux': np.array([0.1, 0.1, 0.1]),
            'y': np.array([100.0, 200.0, 300.0]),
            'uy': np.array([1.0, 1.0, 1.0])
        })
        # Fit may converge to a poor solution or raise FittingError; both are acceptable.
        try:
            generic_fit(
                bad_data,
                'x',
                'y',
                sin_function,
                ['a', 'b'],
                'y={a}sin({b}x)'
            )
        except FittingError:
            pass  # Expected when optimizer does not converge


class TestGetFittingFunction:
    """Tests for get_fitting_function."""
    
    @pytest.mark.parametrize("func_name", [
        'linear_function',
        'quadratic_function',
        'sin_function',
    ])
    def test_get_fitting_functions(self, func_name: str) -> None:
        """Test getting fitting functions."""
        func = get_fitting_function(func_name)
        assert func is not None
        assert callable(func)
    
    def test_unknown_equation(self) -> None:
        """Test getting unknown equation returns None."""
        assert get_fitting_function('unknown_equation') is None
    
    def test_exit_signal(self) -> None:
        """Test exit signal returns None."""
        assert get_fitting_function(EXIT_SIGNAL) is None
