#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Internationalization (i18n) module for the RegresionLab application.

This module provides language support for the application, allowing all UI messages,
logs, and errors to be displayed in different languages based on the LANGUAGE
environment variable.

Supported languages:
- 'es' or 'español': Spanish (default)
- 'en' or 'english': English

Usage:
    from i18n import t
    
    # In UI code
    messagebox.showerror(t('error.title'), t('error.fitting_failed'))
    
    # In logger code
    logger.info(t('log.application_starting'))
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


# Default language if not specified
DEFAULT_LANGUAGE = 'es'

# Current loaded language
_current_language: str = DEFAULT_LANGUAGE
_translations: Dict[str, Any] = {}


def _get_language_from_env() -> str:
    """
    Get the language from the LANGUAGE environment variable.
    
    Returns:
        Language code ('es' or 'en')
    """
    lang = os.getenv('LANGUAGE', DEFAULT_LANGUAGE).lower()
    
    # Normalize language names
    if lang in ('español', 'spanish', 'es', 'esp'):
        return 'es'
    elif lang in ('english', 'inglés', 'ingles', 'en', 'eng'):
        return 'en'
    else:
        # Default to Spanish if unknown language
        return DEFAULT_LANGUAGE


def _load_translations(language: str) -> Dict[str, Any]:
    """
    Load translation file for the specified language.
    
    Args:
        language: Language code ('es' or 'en')
        
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
        language: Optional language code ('es' or 'en'). If None, reads from env var.
    """
    global _current_language, _translations
    
    if language is None:
        language = _get_language_from_env()
    
    # Normalize language
    if language.lower() in ('español', 'spanish', 'es', 'esp'):
        language = 'es'
    elif language.lower() in ('english', 'inglés', 'ingles', 'en', 'eng'):
        language = 'en'
    else:
        language = DEFAULT_LANGUAGE
    
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
        'Bienvenido, científico. ¿Qué deseas hacer?'
        
        >>> t('error.fitting_failed_details', error='Invalid data')
        'RegresionLab no ha sido capaz de ajustar los datos.\n\nDetalles: Invalid data'
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

# Initialize on module import
initialize_i18n()
