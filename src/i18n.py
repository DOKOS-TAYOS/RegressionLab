"""
Internationalization (i18n) module for the RegressionLab application.

This module provides language support for the application, allowing all UI messages,
logs, and errors to be displayed in different languages based on the LANGUAGE
environment variable.

Supported languages:

    - 'es' or 'español': Spanish (default)
    - 'en' or 'english': English
    - 'de' or 'german': German

Usage:
    from i18n import t
    
    # In UI code
    messagebox.showerror(t('error.title'), t('error.fitting_failed'))
    
    # In logger code
    logger.info(t('log.application_starting'))
"""

# Standard library
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from config import (
    _DEFAULT_LANG,
    LANGUAGE_ALIASES,
    SUPPORTED_LANGUAGE_CODES,
)

# Default language if not specified (re-export from constants for backwards compatibility)
DEFAULT_LANGUAGE: str = _DEFAULT_LANG

# Current loaded language
_current_language: str = DEFAULT_LANGUAGE
_translations: Dict[str, Any] = {}


def _normalize_language(language: str) -> str:
    """
    Normalize language code to standard format.

    Args:
        language: Language name or code

    Returns:
        Normalized language code (one of SUPPORTED_LANGUAGE_CODES).
    """
    lang = language.lower()
    if lang in SUPPORTED_LANGUAGE_CODES:
        return lang
    return LANGUAGE_ALIASES.get(lang, DEFAULT_LANGUAGE)


def _get_language_from_env() -> str:
    """
    Get the language from the LANGUAGE environment variable.
    
    Returns:
        Language code ('es', 'en', or 'de')
    """
    lang = os.getenv('LANGUAGE', DEFAULT_LANGUAGE).lower()
    
    return _normalize_language(lang)


def _load_translations(language: str) -> Dict[str, Any]:
    """
    Load translation file for the specified language.
    
    Args:
        language: Language code ('es', 'en', or 'de')
        
    Returns:
        Dictionary with translations
        
    Raises:
        FileNotFoundError: If translation file doesn't exist
    """
    locales_dir = Path(__file__).parent / 'locales'
    translation_file = locales_dir / f'{language}.json'
    
    if not translation_file.exists():
        raise FileNotFoundError(
            f"Translation file not found: {translation_file}"
        )
    
    with open(translation_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def initialize_i18n(language: Optional[str] = None) -> None:
    """
    Initialize the internationalization system.
    
    This function should be called once at application startup.
    If no language is specified, it reads from the LANGUAGE environment variable.
    
    Args:
        language: Optional language code ('es', 'en', or 'de'). If None, reads from env var.
    """
    global _current_language, _translations
    
    if language is None:
        language = _get_language_from_env()
    else:
        language = _normalize_language(language)
    
    _current_language = language
    
    try:
        _translations = _load_translations(language)
    except FileNotFoundError as e:
        # Fallback to default language if specified language not found
        print(f"Warning: {e}")
        print(f"Falling back to default language: {DEFAULT_LANGUAGE}")
        _current_language = DEFAULT_LANGUAGE
        _translations = _load_translations(DEFAULT_LANGUAGE)


def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current language.
    
    This function retrieves the translation for a given key in the current language.
    The key uses dot notation to navigate nested dictionaries.
    
    Args:
        key: Translation key in dot notation (e.g., 'menu.welcome')
        **kwargs: Optional format parameters for string interpolation
        
    Returns:
        Translated string, or the key itself if translation not found
        
    Examples:
        >>> t('menu.welcome')
        'Welcome, scientist. What would you like to do?'
        
        >>> t('error.fitting_failed_details', error='Invalid data')
        'The fitter was unable to fit the data.\n\nDetails: Invalid data\n\nPlease try another equation or verify the data.'
    """
    # Ensure translations are loaded
    if not _translations:
        initialize_i18n()
    
    # Navigate nested dictionaries using dot notation
    keys = key.split('.')
    value = _translations
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Key not found, return the key itself as fallback
            return key
    
    # If value is still a dict, return the key (incomplete path)
    if isinstance(value, dict):
        return key
    
    # Apply string formatting if kwargs provided
    if kwargs:
        try:
            return str(value).format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return unformatted string
            return str(value)
    
    return str(value)
