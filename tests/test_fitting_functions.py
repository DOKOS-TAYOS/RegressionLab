#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for fitting_functions module.
"""

# Standard library
import sys
import unittest
from pathlib import Path

# Third-party packages
import numpy as np
from numpy.typing import NDArray

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Local imports
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


class TestGeneratePolynomialFunction(unittest.TestCase):
    """Tests for generate_polynomial_function."""
    
    def test_no_parameters(self) -> None:
        """Test polynomial with no parameters returns zero."""
        func = generate_polynomial_function([False, False, False])
        result = func(5.0)
        self.assertEqual(result, 0.0)
    
    def test_constant_term(self) -> None:
        """Test polynomial with constant term."""
        func = generate_polynomial_function([True])
        result = func(5.0, 3.0)
        self.assertEqual(result, 3.0)
    
    def test_linear_term(self) -> None:
        """Test polynomial with linear term."""
        func = generate_polynomial_function([False, True])
        result = func(5.0, 2.0)
        self.assertEqual(result, 10.0)
    
    def test_quadratic_term(self) -> None:
        """Test polynomial with quadratic term."""
        func = generate_polynomial_function([False, False, True])
        result = func(3.0, 2.0)
        self.assertEqual(result, 18.0)
    
    def test_multiple_terms(self) -> None:
        """Test polynomial with multiple terms."""
        func = generate_polynomial_function([True, True, True])
        result = func(2.0, 1.0, 3.0, 2.0)
        self.assertEqual(result, 1.0 + 3.0*2.0 + 2.0*4.0)
    
    def test_array_input(self) -> None:
        """Test polynomial with array input."""
        func = generate_polynomial_function([False, True])
        x = np.array([1.0, 2.0, 3.0])
        result = func(x, 2.0)
        expected = np.array([2.0, 4.0, 6.0])
        np.testing.assert_array_almost_equal(result, expected)


class TestGenerateTrigonometricFunction(unittest.TestCase):
    """Tests for generate_trigonometric_function."""
    
    def test_sin_function(self) -> None:
        """Test sine function generation."""
        func = generate_trigonometric_function('sin')
        result = func(np.pi/2, 1.0, 1.0)
        self.assertAlmostEqual(result, 1.0)
    
    def test_cos_function(self) -> None:
        """Test cosine function generation."""
        func = generate_trigonometric_function('cos')
        result = func(0.0, 1.0, 1.0)
        self.assertAlmostEqual(result, 1.0)
    
    def test_sinh_function(self) -> None:
        """Test hyperbolic sine function generation."""
        func = generate_trigonometric_function('sinh')
        result = func(0.0, 1.0, 1.0)
        self.assertAlmostEqual(result, 0.0)
    
    def test_cosh_function(self) -> None:
        """Test hyperbolic cosine function generation."""
        func = generate_trigonometric_function('cosh')
        result = func(0.0, 1.0, 1.0)
        self.assertAlmostEqual(result, 1.0)
    
    def test_with_phase(self) -> None:
        """Test trigonometric function with phase shift."""
        func = generate_trigonometric_function('sin', with_phase=True)
        result = func(0.0, 1.0, 1.0, np.pi/2)
        self.assertAlmostEqual(result, 1.0)
    
    def test_invalid_type(self) -> None:
        """Test invalid function type raises error."""
        with self.assertRaises(ValueError):
            generate_trigonometric_function('invalid')


class TestGenerateInverseFunction(unittest.TestCase):
    """Tests for generate_inverse_function."""
    
    def test_inverse_power_1(self) -> None:
        """Test inverse function with power 1."""
        func = generate_inverse_function(1)
        result = func(2.0, 10.0)
        self.assertAlmostEqual(result, 5.0)
    
    def test_inverse_power_2(self) -> None:
        """Test inverse function with power 2."""
        func = generate_inverse_function(2)
        result = func(2.0, 8.0)
        self.assertAlmostEqual(result, 2.0)
    
    def test_array_input(self) -> None:
        """Test inverse function with array input."""
        func = generate_inverse_function(1)
        x = np.array([1.0, 2.0, 4.0])
        result = func(x, 12.0)
        expected = np.array([12.0, 6.0, 3.0])
        np.testing.assert_array_almost_equal(result, expected)


class TestPredefinedFunctions(unittest.TestCase):
    """Tests for predefined mathematical functions."""
    
    def test_linear_function_with_n(self) -> None:
        """Test linear function with intercept."""
        # linear_function_with_n(t, n, m) = n + m*t
        result = linear_function_with_n(2.0, 1.0, 3.0)
        self.assertAlmostEqual(result, 7.0)
    
    def test_linear_function(self) -> None:
        """Test linear function through origin."""
        result = linear_function(2.0, 3.0)
        self.assertAlmostEqual(result, 6.0)
    
    def test_quadratic_function_complete(self) -> None:
        """Test complete quadratic function."""
        result = quadratic_function_complete(2.0, 1.0, 2.0, 3.0)
        self.assertAlmostEqual(result, 1.0 + 2.0*2.0 + 3.0*4.0)
    
    def test_quadratic_function(self) -> None:
        """Test quadratic function through origin."""
        result = quadratic_function(3.0, 2.0)
        self.assertAlmostEqual(result, 18.0)
    
    def test_fourth_power(self) -> None:
        """Test fourth power function."""
        result = fourth_power(2.0, 3.0)
        self.assertAlmostEqual(result, 48.0)
    
    def test_sin_function(self) -> None:
        """Test sine function."""
        result = sin_function(np.pi/2, 2.0, 1.0)
        self.assertAlmostEqual(result, 2.0)
    
    def test_sin_function_with_c(self) -> None:
        """Test sine function with phase."""
        result = sin_function_with_c(0.0, 1.0, 1.0, np.pi/2)
        self.assertAlmostEqual(result, 1.0)
    
    def test_cos_function(self) -> None:
        """Test cosine function."""
        result = cos_function(0.0, 3.0, 1.0)
        self.assertAlmostEqual(result, 3.0)
    
    def test_cos_function_with_c(self) -> None:
        """Test cosine function with phase."""
        result = cos_function_with_c(np.pi/2, 1.0, 1.0, -np.pi/2)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_sinh_function(self) -> None:
        """Test hyperbolic sine function."""
        result = sinh_function(0.0, 1.0, 1.0)
        self.assertAlmostEqual(result, 0.0)
    
    def test_cosh_function(self) -> None:
        """Test hyperbolic cosine function."""
        result = cosh_function(0.0, 2.0, 1.0)
        self.assertAlmostEqual(result, 2.0)
    
    def test_ln_function(self) -> None:
        """Test natural logarithm function."""
        result = ln_function(np.e, 2.0)
        self.assertAlmostEqual(result, 2.0)
    
    def test_inverse_function(self) -> None:
        """Test inverse function."""
        result = inverse_function(4.0, 12.0)
        self.assertAlmostEqual(result, 3.0)
    
    def test_inverse_square_function(self) -> None:
        """Test inverse square function."""
        result = inverse_square_function(2.0, 8.0)
        self.assertAlmostEqual(result, 2.0)


class TestFunctionsWithArrays(unittest.TestCase):
    """Tests for functions with array inputs."""
    
    def test_linear_with_arrays(self) -> None:
        """Test linear function with array input."""
        x = np.array([1.0, 2.0, 3.0])
        result = linear_function(x, 2.0)
        expected = np.array([2.0, 4.0, 6.0])
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_sin_with_arrays(self) -> None:
        """Test sine function with array input."""
        x = np.array([0.0, np.pi/2, np.pi])
        result = sin_function(x, 1.0, 1.0)
        expected = np.array([0.0, 1.0, 0.0])
        np.testing.assert_array_almost_equal(result, expected, decimal=5)
    
    def test_ln_with_arrays(self) -> None:
        """Test logarithm function with array input."""
        x = np.array([1.0, np.e, np.e**2])
        result = ln_function(x, 1.0)
        expected = np.array([0.0, 1.0, 2.0])
        np.testing.assert_array_almost_equal(result, expected)


if __name__ == '__main__':
    unittest.main()
