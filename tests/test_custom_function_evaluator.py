"""
Tests for custom_function_evaluator module.
"""

import pytest
import numpy as np
import pandas as pd

from fitting.custom_function_evaluator import CustomFunctionEvaluator
from utils import EquationError, ValidationError


class TestCustomFunctionEvaluatorInit:
    """Tests for CustomFunctionEvaluator initialization."""
    
    @pytest.mark.parametrize("equation,params", [
        ("a*x + b", ["a", "b"]),
        ("a*x**2 + b*x + c", ["a", "b", "c"]),
    ])
    def test_valid_initialization(self, equation: str, params: list[str]) -> None:
        """Test creating evaluator with valid equations."""
        evaluator = CustomFunctionEvaluator(equation, params)
        assert evaluator is not None
        assert evaluator.parameter_names == params
    
    @pytest.mark.parametrize("equation,params", [
        ("", ["a"]),
        ("   ", ["a"]),
    ])
    def test_empty_equation(self, equation: str, params: list[str]) -> None:
        """Test that empty equation raises ValidationError."""
        with pytest.raises(ValidationError):
            CustomFunctionEvaluator(equation, params)
    
    def test_invalid_parameter_names(self) -> None:
        """Test that invalid parameter names raise ValidationError."""
        with pytest.raises(ValidationError):
            CustomFunctionEvaluator("a*x", ["123invalid"])
    
    def test_duplicate_parameter_names(self) -> None:
        """Test that duplicate parameter names raise ValidationError."""
        with pytest.raises(ValidationError):
            CustomFunctionEvaluator("a*x + a", ["a", "a"])


class TestPrepareFormula:
    """Tests for formula preparation."""
    
    @pytest.mark.parametrize("equation,replacement", [
        ("a*ln(x)", "np.log"),
        ("a*sin(x)", "np.sin"),
        ("a*cos(x)", "np.cos"),
        ("a*exp(x)", "np.exp"),
    ])
    def test_function_replacements(self, equation: str, replacement: str) -> None:
        """Test that math functions are replaced with numpy equivalents."""
        evaluator = CustomFunctionEvaluator(equation, ["a"])
        assert replacement in evaluator.equation_str
    
    def test_multiple_replacements(self) -> None:
        """Test multiple function replacements."""
        evaluator = CustomFunctionEvaluator("a*sin(x) + b*cos(x)", ["a", "b"])
        assert "np.sin" in evaluator.equation_str
        assert "np.cos" in evaluator.equation_str


class TestFunctionCreation:
    """Tests for function creation."""
    
    @pytest.mark.parametrize("equation,params,x,param_values,expected", [
        ("a*x + b", ["a", "b"], np.array([1.0, 2.0, 3.0]), (2.0, 3.0), lambda x: 2.0 * x + 3.0),
        ("a*x**2", ["a"], np.array([1.0, 2.0, 3.0]), (2.0,), lambda x: 2.0 * x**2),
        ("a*exp(b*x)", ["a", "b"], np.array([0.0, 1.0, 2.0]), (1.0, 0.5), lambda x: 1.0 * np.exp(0.5 * x)),
        ("a*sin(b*x)", ["a", "b"], np.array([0.0, np.pi/2, np.pi]), (2.0, 1.0), lambda x: 2.0 * np.sin(1.0 * x)),
    ])
    def test_function_evaluation(self, equation: str, params: list[str], x: np.ndarray, 
                                 param_values: tuple, expected: callable) -> None:
        """Test that created function evaluates correctly."""
        evaluator = CustomFunctionEvaluator(equation, params)
        func = evaluator.get_function()
        result = func(x, *param_values)
        expected_result = expected(x)
        np.testing.assert_array_almost_equal(result, expected_result)
    
    def test_wrong_parameter_count(self) -> None:
        """Test that wrong number of parameters raises error."""
        evaluator = CustomFunctionEvaluator("a*x + b", ["a", "b"])
        func = evaluator.get_function()
        x = np.array([1.0, 2.0, 3.0])
        with pytest.raises(EquationError):
            func(x, 2.0)  # Missing one parameter
    
    def test_division_by_zero(self) -> None:
        """Test that division by zero produces inf/nan values."""
        evaluator = CustomFunctionEvaluator("a/x", ["a"])
        func = evaluator.get_function()
        x = np.array([0.0, 1.0, 2.0])
        with np.errstate(divide='ignore', invalid='ignore'):
            result = func(x, 1.0)
        assert np.isinf(result[0]) or np.isnan(result[0])


class TestEquationTemplate:
    """Tests for equation template generation."""
    
    @pytest.mark.parametrize("equation,params", [
        ("a*x + b", ["a", "b"]),
        ("a*sin(b*x + c)", ["a", "b", "c"]),
    ])
    def test_template_generation(self, equation: str, params: list[str]) -> None:
        """Test template generation for equations."""
        evaluator = CustomFunctionEvaluator(equation, params)
        template = evaluator._generate_equation_template()
        
        for param in params:
            assert f"{{{param}}}" in template
        assert template.startswith("y=")


class TestFitMethod:
    """Tests for the fit method."""
    
    @pytest.fixture
    def test_data(self) -> pd.DataFrame:
        """Fixture for test data."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        return pd.DataFrame({
            'x': x,
            'ux': np.ones_like(x) * 0.1,
            'y': 2.0 * x + 1.0,
            'uy': np.ones_like(x) * 0.2
        })
    
    def test_fit_initialization(self) -> None:
        """Test that CustomFunctionEvaluator initializes correctly for fitting."""
        evaluator = CustomFunctionEvaluator("a*x + b", ["a", "b"])
        assert evaluator.function is not None
        assert evaluator.parameter_names == ["a", "b"]
        assert evaluator.original_equation_str == "a*x + b"
    
    def test_get_function_callable(self) -> None:
        """Test that get_function returns a callable."""
        evaluator = CustomFunctionEvaluator("a*x", ["a"])
        func = evaluator.get_function()
        assert callable(func)
        
        x = np.array([1.0, 2.0, 3.0])
        result = func(x, 2.0)
        expected = 2.0 * x
        np.testing.assert_array_almost_equal(result, expected)


class TestReprMethod:
    """Tests for string representation."""
    
    def test_repr(self) -> None:
        """Test string representation of evaluator."""
        evaluator = CustomFunctionEvaluator("a*x + b", ["a", "b"])
        repr_str = repr(evaluator)
        
        assert "CustomFunctionEvaluator" in repr_str
        assert "a*x + b" in repr_str
        assert "a" in repr_str
        assert "b" in repr_str
