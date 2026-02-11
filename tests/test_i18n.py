"""
Tests for i18n module.
"""

import os
import pytest

from i18n import initialize_i18n, t, _get_language_from_env, DEFAULT_LANGUAGE


@pytest.fixture(autouse=True)
def reset_i18n() -> None:
    """Reset i18n after each test."""
    yield
    initialize_i18n()


class TestI18nLanguageDetection:
    """Tests for language detection."""
    
    @pytest.fixture(autouse=True)
    def cleanup_env(self) -> None:
        """Clean up LANGUAGE env var after each test."""
        original_lang = os.getenv('LANGUAGE')
        yield
        if original_lang:
            os.environ['LANGUAGE'] = original_lang
        elif 'LANGUAGE' in os.environ:
            del os.environ['LANGUAGE']
        initialize_i18n()
    
    def test_default_language(self) -> None:
        """Test default language is Spanish."""
        assert DEFAULT_LANGUAGE == 'es'
    
    @pytest.mark.parametrize("lang_value,expected", [
        ('es', 'es'),
        ('español', 'es'),
        ('spanish', 'es'),
        ('ESP', 'es'),
    ])
    def test_get_language_spanish(self, lang_value: str, expected: str) -> None:
        """Test getting Spanish language from env."""
        os.environ['LANGUAGE'] = lang_value
        assert _get_language_from_env() == expected
    
    @pytest.mark.parametrize("lang_value,expected", [
        ('en', 'en'),
        ('english', 'en'),
        ('inglés', 'en'),
        ('ENG', 'en'),
    ])
    def test_get_language_english(self, lang_value: str, expected: str) -> None:
        """Test getting English language from env."""
        os.environ['LANGUAGE'] = lang_value
        assert _get_language_from_env() == expected
    
    def test_get_language_unknown(self) -> None:
        """Test unknown language defaults to Spanish."""
        os.environ['LANGUAGE'] = 'unknown'
        assert _get_language_from_env() == 'es'


class TestI18nInitialization:
    """Tests for i18n initialization."""
    
    @pytest.mark.parametrize("lang", ['es', 'en', 'de'])
    def test_initialize_language(self, lang: str) -> None:
        """Test initializing with supported languages."""
        initialize_i18n(lang)
        result = t('menu.welcome')
        assert isinstance(result, str)
        assert result != 'menu.welcome'
    
    def test_initialize_invalid_language(self) -> None:
        """Test initializing with invalid language falls back."""
        initialize_i18n('invalid')
        result = t('menu.welcome')
        assert isinstance(result, str)


class TestI18nTranslation:
    """Tests for translation function."""
    
    def setup_method(self) -> None:
        """Initialize i18n with Spanish."""
        initialize_i18n('es')
    
    def test_simple_translation(self) -> None:
        """Test simple translation."""
        result = t('menu.welcome')
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_nested_translation(self) -> None:
        """Test nested translation with dot notation."""
        result = t('error.title')
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_missing_key(self) -> None:
        """Test missing translation key returns key itself."""
        assert t('nonexistent.key.path') == 'nonexistent.key.path'
    
    def test_translation_with_params(self) -> None:
        """Test translation with format parameters."""
        result = t('log.version', version='1.0.0')
        assert isinstance(result, str)
        assert '1.0.0' in result
    
    def test_incomplete_path(self) -> None:
        """Test incomplete translation path."""
        assert t('menu') == 'menu'


class TestI18nBothLanguages:
    """Tests to verify both language files work."""
    
    @pytest.mark.parametrize("lang,keys", [
        ('es', ['menu.welcome', 'error.title', 'dialog.exit_option']),
        ('en', ['menu.welcome', 'error.title', 'dialog.exit_option']),
        ('de', ['menu.welcome', 'error.title', 'dialog.exit_option']),
    ])
    def test_translations_loaded(self, lang: str, keys: list[str]) -> None:
        """Test translations are loaded for both languages."""
        initialize_i18n(lang)
        for key in keys:
            result = t(key)
            assert result != key, f"Missing {lang} translation for: {key}"
