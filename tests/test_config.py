"""
Tests for config module.
"""

import os
import shutil
import tempfile
import pytest
from pathlib import Path

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
    EQUATIONS,
    AVAILABLE_EQUATION_TYPES,
    EXIT_SIGNAL
)


@pytest.fixture
def env_var() -> str:
    """Fixture for test environment variable name."""
    return 'TEST_CONFIG_VAR'


@pytest.fixture(autouse=True)
def cleanup_env(env_var: str) -> None:
    """Clean up environment variable after each test."""
    yield
    if env_var in os.environ:
        del os.environ[env_var]


class TestGetEnv:
    """Tests for get_env function."""
    
    @pytest.mark.parametrize("env_value,default,expected", [
        (None, 'default_value', 'default_value'),
        ('test_value', 'default_value', 'test_value'),
    ])
    def test_get_env_string(self, env_var: str, env_value: str | None, default: str, expected: str) -> None:
        """Test getting string env var."""
        if env_value:
            os.environ[env_var] = env_value
        result = get_env(env_var, default)
        assert result == expected
    
    def test_get_env_int(self, env_var: str) -> None:
        """Test getting int env var."""
        os.environ[env_var] = '42'
        assert get_env(env_var, 0, int) == 42
    
    def test_get_env_int_invalid(self, env_var: str) -> None:
        """Test getting int env var with invalid value."""
        os.environ[env_var] = 'not_a_number'
        assert get_env(env_var, 10, int) == 10
    
    def test_get_env_float(self, env_var: str) -> None:
        """Test getting float env var."""
        os.environ[env_var] = '3.14'
        assert abs(get_env(env_var, 0.0, float) - 3.14) < 1e-6
    
    @pytest.mark.parametrize("value", ['true', 'True', '1', 'yes', 'YES'])
    def test_get_env_bool_true(self, env_var: str, value: str) -> None:
        """Test getting bool env var with true values."""
        os.environ[env_var] = value
        assert get_env(env_var, False, bool) is True
    
    @pytest.mark.parametrize("value", ['false', 'False', '0', 'no', 'NO'])
    def test_get_env_bool_false(self, env_var: str, value: str) -> None:
        """Test getting bool env var with false values."""
        os.environ[env_var] = value
        assert get_env(env_var, True, bool) is False


class TestConfigPaths:
    """Tests for path-related config functions."""
    
    def test_get_project_root(self) -> None:
        """Test getting project root directory."""
        root = get_project_root()
        assert isinstance(root, Path)
        assert root.exists()
        assert (root / 'src').exists()
    
    def test_ensure_output_directory_default(self) -> None:
        """Test ensuring output directory with default path."""
        output_dir = ensure_output_directory()
        assert os.path.exists(output_dir)
        assert os.path.isdir(output_dir)
    
    def test_ensure_output_directory_custom(self) -> None:
        """Test ensuring output directory with custom path."""
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dir = os.path.join(temp_dir, 'test_output')
            rel_path = os.path.relpath(custom_dir, get_project_root())
            output_dir = ensure_output_directory(rel_path)
            assert os.path.exists(output_dir)
            assert os.path.isdir(output_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_output_path(self) -> None:
        """Test getting output path for a fit."""
        fit_name = 'test_fit'
        output_path = get_output_path(fit_name)
        assert isinstance(output_path, str)
        # Check it ends with a valid image extension
        assert any(output_path.endswith(ext) for ext in ['.png', '.jpg', '.pdf'])
        assert fit_name in output_path


class TestConfigConstants:
    """Tests for configuration constants."""
    
    @pytest.mark.parametrize("config_dict,required_keys", [
        (UI_THEME, ['background', 'foreground', 'button_fg_accept', 'font_size']),
        (PLOT_CONFIG, ['figsize', 'line_color', 'marker_format']),
        (FONT_CONFIG, ['family', 'title_size', 'axis_size']),
        (FILE_CONFIG, ['input_dir', 'output_dir', 'filename_template', 'plot_format']),
    ])
    def test_config_dicts(self, config_dict: dict, required_keys: list[str]) -> None:
        """Test configuration dictionaries exist and have required keys."""
        assert isinstance(config_dict, dict)
        for key in required_keys:
            assert key in config_dict
    
    def test_math_function_replacements(self) -> None:
        """Test math function replacements exist."""
        assert isinstance(MATH_FUNCTION_REPLACEMENTS, dict)
        # Keys use lookbehind pattern; check that expected targets exist
        values = set(MATH_FUNCTION_REPLACEMENTS.values())
        assert 'np.log' in values
        assert 'np.sin' in values
    
    def test_equations_config(self) -> None:
        """Test equations config (from equations.yaml) exists."""
        assert isinstance(EQUATIONS, dict)
        assert 'linear_function' in EQUATIONS
        assert 'quadratic_function' in EQUATIONS
        for eq_id, entry in EQUATIONS.items():
            assert 'function' in entry
            assert 'param_names' in entry
    
    def test_available_equation_types(self) -> None:
        """Test available equation types list."""
        assert isinstance(AVAILABLE_EQUATION_TYPES, list)
        assert len(AVAILABLE_EQUATION_TYPES) > 0
        assert 'linear_function' in AVAILABLE_EQUATION_TYPES
    
    def test_exit_signal(self) -> None:
        """Test exit signal constant."""
        assert isinstance(EXIT_SIGNAL, str)
        assert EXIT_SIGNAL == 'Exit'


def test_setup_fonts() -> None:
    """Test that setup_fonts returns a tuple of fonts."""
    fonts = setup_fonts()
    assert isinstance(fonts, tuple)
    assert len(fonts) == 2
