#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for fitting_functions module.
"""

import pytest
import numpy as np
from numpy.typing import NDArray

from fitting.fitting_functions import (
    generate_polynomial_function,
    generate_trigonometric_function,
    generate_inverse_function,
    linear_function_with_n,
    linear_function,
    quadratic_function_complete,
    quadratic_function,
    fourth_power,
    sin_function,
    sin_function_with_c,
    cos_function,
    cos_function_with_c,
    sinh_function,
    cosh_function,
    ln_function,
    inverse_function,
    inverse_square_function
)


class TestGeneratePolynomialFunction:
    """Tests for generate_polynomial_function."""
    
    def test_no_parameters(self) -> None:
        """Test polynomial with no parameters returns zero."""
        func = generate_polynomial_function([False, False, False])
        assert func(5.0) == 0.0
    
    def test_constant_term(self) -> None:
        """Test polynomial with constant term."""
        func = generate_polynomial_function([True])
        assert func(5.0, 3.0) == 3.0
    
    def test_linear_term(self) -> None:
        """Test polynomial with linear term."""
        func = generate_polynomial_function([False, True])
        assert func(5.0, 2.0) == 10.0
    
    def test_quadratic_term(self) -> None:
        """Test polynomial with quadratic term."""
        func = generate_polynomial_function([False, False, True])
        assert func(3.0, 2.0) == 18.0
    
    def test_multiple_terms(self) -> None:
        """Test polynomial with multiple terms."""
        func = generate_polynomial_function([True, True, True])
        result = func(2.0, 1.0, 3.0, 2.0)
        assert abs(result - (1.0 + 3.0*2.0 + 2.0*4.0)) < 1e-10
    
    def test_array_input(self) -> None:
        """Test polynomial with array input."""
        func = generate_polynomial_function([False, True])
        x = np.array([1.0, 2.0, 3.0])
        result = func(x, 2.0)
        expected = np.array([2.0, 4.0, 6.0])
        np.testing.assert_array_almost_equal(result, expected)


class TestGenerateTrigonometricFunction:
    """Tests for generate_trigonometric_function."""
    
    @pytest.mark.parametrize("func_type,test_input,expected", [
        ('sin', (np.pi/2, 1.0, 1.0), 1.0),
        ('cos', (0.0, 1.0, 1.0), 1.0),
        ('sinh', (0.0, 1.0, 1.0), 0.0),
        ('cosh', (0.0, 1.0, 1.0), 1.0),
    ])
    def test_trigonometric_functions(self, func_type: str, test_input: tuple, expected: float) -> None:
        """Test trigonometric function generation."""
        func = generate_trigonometric_function(func_type)
        result = func(*test_input)
        assert abs(result - expected) < 1e-10
    
    def test_with_phase(self) -> None:
        """Test trigonometric function with phase shift."""
        func = generate_trigonometric_function('sin', with_phase=True)
        result = func(0.0, 1.0, 1.0, np.pi/2)
        assert abs(result - 1.0) < 1e-10
    
    def test_invalid_type(self) -> None:
        """Test invalid function type raises error."""
        with pytest.raises(ValueError):
            generate_trigonometric_function('invalid')


class TestGenerateInverseFunction:
    """Tests for generate_inverse_function."""
    
    @pytest.mark.parametrize("power,x_val,param,expected", [
        (1, 2.0, 10.0, 5.0),
        (2, 2.0, 8.0, 2.0),
    ])
    def test_inverse_power(self, power: int, x_val: float, param: float, expected: float) -> None:
        """Test inverse function with different powers."""
        func = generate_inverse_function(power)
        result = func(x_val, param)
        assert abs(result - expected) < 1e-10
    
    def test_array_input(self) -> None:
        """Test inverse function with array input."""
        func = generate_inverse_function(1)
        x = np.array([1.0, 2.0, 4.0])
        result = func(x, 12.0)
        expected = np.array([12.0, 6.0, 3.0])
        np.testing.assert_array_almost_equal(result, expected)


class TestPredefinedFunctions:
    """Tests for predefined mathematical functions."""
    
    @pytest.mark.parametrize("func,args,expected", [
        (linear_function_with_n, (2.0, 1.0, 3.0), 7.0),
        (linear_function, (2.0, 3.0), 6.0),
        (quadratic_function_complete, (2.0, 1.0, 2.0, 3.0), 1.0 + 2.0*2.0 + 3.0*4.0),
        (quadratic_function, (3.0, 2.0), 18.0),
        (fourth_power, (2.0, 3.0), 48.0),
        (sin_function, (np.pi/2, 2.0, 1.0), 2.0),
        (sin_function_with_c, (0.0, 1.0, 1.0, np.pi/2), 1.0),
        (cos_function, (0.0, 3.0, 1.0), 3.0),
        (cos_function_with_c, (np.pi/2, 1.0, 1.0, -np.pi/2), 1.0),
        (sinh_function, (0.0, 1.0, 1.0), 0.0),
        (cosh_function, (0.0, 2.0, 1.0), 2.0),
        (ln_function, (np.e, 2.0), 2.0),
        (inverse_function, (4.0, 12.0), 3.0),
        (inverse_square_function, (2.0, 8.0), 2.0),
    ])
    def test_function_evaluation(self, func: callable, args: tuple, expected: float) -> None:
        """Test predefined functions evaluate correctly."""
        result = func(*args)
        assert abs(result - expected) < 1e-5


class TestFunctionsWithArrays:
    """Tests for functions with array inputs."""
    
    @pytest.mark.parametrize("func,args,expected", [
        (linear_function, (np.array([1.0, 2.0, 3.0]), 2.0), np.array([2.0, 4.0, 6.0])),
        (sin_function, (np.array([0.0, np.pi/2, np.pi]), 1.0, 1.0), np.array([0.0, 1.0, 0.0])),
        (ln_function, (np.array([1.0, np.e, np.e**2]), 1.0), np.array([0.0, 1.0, 2.0])),
    ])
    def test_array_inputs(self, func: callable, args: tuple, expected: NDArray) -> None:
        """Test functions with array input."""
        result = func(*args)
        np.testing.assert_array_almost_equal(result, expected, decimal=5)
