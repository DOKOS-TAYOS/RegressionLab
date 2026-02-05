"""Data loading and display for the Streamlit app."""

import os
import tempfile
from pathlib import Path
from typing import Any, List, Optional

import streamlit as st

from i18n import t
from utils.logger import get_logger

logger = get_logger(__name__)


def _get_variable_names(data: Any, filter_uncertainty: bool = True) -> List[str]:
    """Get variable names from data (defer loaders import)."""
    from loaders.data_loader import get_variable_names
    return get_variable_names(data, filter_uncertainty=filter_uncertainty)


def load_uploaded_file(uploaded_file: Any) -> Optional[Any]:
    """
    Load data from uploaded file.

    Returns:
        DataFrame with loaded data, or None if loading fails.
    """
    from loaders.loading_utils import csv_reader, excel_reader, txt_reader

    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            if file_extension == 'csv':
                data = csv_reader(tmp_path)
            elif file_extension == 'xlsx':
                data = excel_reader(tmp_path)
            elif file_extension == 'txt':
                data = txt_reader(tmp_path)
            else:
                st.error(t('error.unsupported_file_type', file_type=file_extension))
                return None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        logger.info(t('log.data_loaded', rows=len(data), cols=len(data.columns)))
        return data

    except Exception as e:
        logger.error(f"Error loading file: {str(e)}", exc_info=True)
        st.error(t('error.data_load_error', error=str(e)))
        return None


def show_data_with_pair_plots(data: Any) -> None:
    """Show data in an expander with optional pair plots (scatter matrix)."""
    with st.expander(t('dialog.show_data_title'), expanded=True):
        st.dataframe(data)
        st.markdown(
            """
            <style>
            div[data-testid="stExpander"] .stButton > button {
                padding: 0.6rem 2rem; font-size: 1.15rem; min-height: 2.5rem; width: 100%%;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        if st.button(t('dialog.show_pair_plots'), key='btn_show_pair_plots', use_container_width=True):
            st.session_state['data_show_pair_plots'] = True
        if st.session_state.get('data_show_pair_plots'):
            variables = _get_variable_names(data, filter_uncertainty=True)
            if len(variables) < 1:
                st.caption(t('error.no_valid_data'))
            else:
                from plotting.plot_utils import create_pair_plots
                fig = create_pair_plots(data, variables, output_path=None)
                st.subheader(t('dialog.pair_plots_title'))
                st.pyplot(fig, width="stretch")
                if hasattr(fig, 'close'):
                    fig.close()


def get_temp_output_dir() -> Path:
    """Get or create a temporary directory for plots. Uses session-specific temp directory."""
    if 'temp_output_dir' not in st.session_state:
        temp_dir = tempfile.mkdtemp(prefix='regressionlab_')
        st.session_state.temp_output_dir = temp_dir
        logger.info(f"Created temporary output directory: {temp_dir}")
    return Path(st.session_state.temp_output_dir)


def get_variable_names(data: Any, filter_uncertainty: bool = True) -> List[str]:
    """Public wrapper for variable names (used by fitting and modes)."""
    return _get_variable_names(data, filter_uncertainty=filter_uncertainty)
