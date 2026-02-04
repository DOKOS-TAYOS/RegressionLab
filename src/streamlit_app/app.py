#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Streamlit Application for RegressionLab
Web-based interface for curve fitting operations.
"""

import sys
import traceback
from pathlib import Path
from typing import Optional

# Add src directory to Python path for proper imports
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st

# Local imports (lightweight at startup)
try:
    from i18n import initialize_i18n, t
    from utils.logger import setup_logging, get_logger

    initialize_i18n('es')
    setup_logging()
    logger = get_logger(__name__)
except Exception as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize app: {e}")
    logger.error(traceback.format_exc())

    def t(key: str, **kwargs) -> str:
        return key

    def initialize_i18n(language: Optional[str] = None) -> None:
        pass

from streamlit_app.sections import (
    initialize_session_state,
    setup_sidebar,
    show_logo,
    show_help_section,
    mode_normal_fitting,
    mode_multiple_datasets,
    mode_checker_fitting,
    mode_total_fitting,
)


def main() -> None:
    """Main Streamlit application."""
    try:
        from config import __version__, AVAILABLE_EQUATION_TYPES
    except ImportError as e:
        st.error(f"Error importing configuration: {e}")
        st.error("Please ensure all dependencies are installed correctly.")
        logger.error(f"Import error: {e}", exc_info=True)
        return

    try:
        st.set_page_config(
            page_title="RegressionLab",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    except Exception as e:
        logger.warning(f"Page config already set: {e}")

    try:
        initialize_session_state()
        initialize_i18n(st.session_state.language)

        operation_mode = setup_sidebar(__version__)

        show_logo()
        show_help_section()

        mode_map = {
            t('menu.normal_fitting'): mode_normal_fitting,
            t('menu.multiple_datasets'): mode_multiple_datasets,
            t('menu.checker_fitting'): mode_checker_fitting,
            t('menu.total_fitting'): mode_total_fitting,
        }

        mode_handler = mode_map.get(operation_mode)
        if mode_handler:
            mode_handler(AVAILABLE_EQUATION_TYPES)
    except Exception as e:
        st.error(f"An error occurred while running the application: {e}")
        st.error("Please check the logs for more details.")
        logger.error(f"Application error: {e}", exc_info=True)
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
