#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for config module.
"""

# Standard library
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Local imports
from config import (
    get_env,
    get_project_root,
    ensure_output_directory,
    get_output_path,
    setup_fonts,
    UI_THEME,
    PLOT_CONFIG,
    FONT_CONFIG,
    FILE_CONFIG,
    MATH_FUNCTION_REPLACEMENTS,
    EQUATION_FUNCTION_MAP,
    AVAILABLE_EQUATION_TYPES,
    EXIT_SIGNAL
)


class TestConfigGetEnv(unittest.TestCase):
    """Tests for get_env function."""
    
    def setUp(self) -> None:
        """Set up test environment variables."""
        self.test_key = 'TEST_CONFIG_VAR'
        
    def tearDown(self) -> None:
        """Clean up test environment variables."""
        if self.test_key in os.environ:
            del os.environ[self.test_key]
    
    def test_get_env_string_default(self) -> None:
        """Test getting string env var with default."""
        result = get_env(self.test_key, 'default_value')
        self.assertEqual(result, 'default_value')
    
    def test_get_env_string_exists(self) -> None:
        """Test getting string env var that exists."""
        os.environ[self.test_key] = 'test_value'
        result = get_env(self.test_key, 'default_value')
        self.assertEqual(result, 'test_value')
    
    def test_get_env_int(self) -> None:
        """Test getting int env var."""
        os.environ[self.test_key] = '42'
        result = get_env(self.test_key, 0, int)
        self.assertEqual(result, 42)
    
    def test_get_env_int_invalid(self) -> None:
        """Test getting int env var with invalid value."""
        os.environ[self.test_key] = 'not_a_number'
        result = get_env(self.test_key, 10, int)
        self.assertEqual(result, 10)
    
    def test_get_env_float(self) -> None:
        """Test getting float env var."""
        os.environ[self.test_key] = '3.14'
        result = get_env(self.test_key, 0.0, float)
        self.assertAlmostEqual(result, 3.14)
    
    def test_get_env_bool_true(self) -> None:
        """Test getting bool env var with true values."""
        for value in ['true', 'True', '1', 'yes', 'YES']:
            os.environ[self.test_key] = value
            result = get_env(self.test_key, False, bool)
            self.assertTrue(result, f"Failed for value: {value}")
    
    def test_get_env_bool_false(self) -> None:
        """Test getting bool env var with false values."""
        for value in ['false', 'False', '0', 'no', 'NO']:
            os.environ[self.test_key] = value
            result = get_env(self.test_key, True, bool)
            self.assertFalse(result, f"Failed for value: {value}")


class TestConfigPaths(unittest.TestCase):
    """Tests for path-related config functions."""
    
    def test_get_project_root(self) -> None:
        """Test getting project root directory."""
        root = get_project_root()
        self.assertIsInstance(root, Path)
        self.assertTrue(root.exists())
        # Check that src directory exists under root
        self.assertTrue((root / 'src').exists())
    
    def test_ensure_output_directory_default(self) -> None:
        """Test ensuring output directory with default path."""
        output_dir = ensure_output_directory()
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.isdir(output_dir))
    
    def test_ensure_output_directory_custom(self) -> None:
        """Test ensuring output directory with custom path."""
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dir = os.path.join(temp_dir, 'test_output')
            # Use relative path from project root
            rel_path = os.path.relpath(custom_dir, get_project_root())
            output_dir = ensure_output_directory(rel_path)
            self.assertTrue(os.path.exists(output_dir))
            self.assertTrue(os.path.isdir(output_dir))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_output_path(self) -> None:
        """Test getting output path for a fit."""
        fit_name = 'test_fit'
        output_path = get_output_path(fit_name)
        self.assertIsInstance(output_path, str)
        self.assertTrue(output_path.endswith('.png'))
        self.assertIn(fit_name, output_path)


class TestConfigConstants(unittest.TestCase):
    """Tests for configuration constants."""
    
    def test_ui_theme_exists(self) -> None:
        """Test UI theme configuration exists."""
        self.assertIsInstance(UI_THEME, dict)
        required_keys = ['background', 'foreground', 'button_fg', 'font_size']
        for key in required_keys:
            self.assertIn(key, UI_THEME)
    
    def test_plot_config_exists(self) -> None:
        """Test plot configuration exists."""
        self.assertIsInstance(PLOT_CONFIG, dict)
        required_keys = ['figsize', 'line_color', 'marker_format']
        for key in required_keys:
            self.assertIn(key, PLOT_CONFIG)
    
    def test_font_config_exists(self) -> None:
        """Test font configuration exists."""
        self.assertIsInstance(FONT_CONFIG, dict)
        required_keys = ['family', 'title_size', 'axis_size']
        for key in required_keys:
            self.assertIn(key, FONT_CONFIG)
    
    def test_file_config_exists(self) -> None:
        """Test file configuration exists."""
        self.assertIsInstance(FILE_CONFIG, dict)
        required_keys = ['input_dir', 'output_dir', 'filename_template']
        for key in required_keys:
            self.assertIn(key, FILE_CONFIG)
    
    def test_math_function_replacements(self) -> None:
        """Test math function replacements exist."""
        self.assertIsInstance(MATH_FUNCTION_REPLACEMENTS, dict)
        self.assertIn(r'\bln\b', MATH_FUNCTION_REPLACEMENTS)
        self.assertIn(r'\bsin\b', MATH_FUNCTION_REPLACEMENTS)
    
    def test_equation_function_map(self) -> None:
        """Test equation function map exists."""
        self.assertIsInstance(EQUATION_FUNCTION_MAP, dict)
        self.assertIn('linear_function', EQUATION_FUNCTION_MAP)
        self.assertIn('quadratic_function', EQUATION_FUNCTION_MAP)
    
    def test_available_equation_types(self) -> None:
        """Test available equation types list."""
        self.assertIsInstance(AVAILABLE_EQUATION_TYPES, list)
        self.assertGreater(len(AVAILABLE_EQUATION_TYPES), 0)
        self.assertIn('linear_function', AVAILABLE_EQUATION_TYPES)
    
    def test_exit_signal(self) -> None:
        """Test exit signal constant."""
        self.assertIsInstance(EXIT_SIGNAL, str)
        self.assertEqual(EXIT_SIGNAL, 'Salir')


class TestSetupFonts(unittest.TestCase):
    """Tests for setup_fonts function."""
    
    def test_setup_fonts_returns_tuple(self) -> None:
        """Test that setup_fonts returns a tuple of fonts."""
        fonts = setup_fonts()
        self.assertIsInstance(fonts, tuple)
        self.assertEqual(len(fonts), 2)


if __name__ == '__main__':
    unittest.main()
