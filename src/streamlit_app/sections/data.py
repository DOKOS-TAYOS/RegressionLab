"""Data loading and display for the Streamlit app."""

import io
import tempfile
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
import streamlit as st

from i18n import t
from utils import get_logger

logger = get_logger(__name__)

# Help content keys for View Data (matches Tkinter help dialog)
_VIEW_DATA_TRANSFORM_HELP_KEYS: List[str] = [
    'view_data_transform_fft',
    'view_data_transform_fft_magnitude',
    'view_data_transform_ifft',
    'view_data_transform_dct',
    'view_data_transform_idct',
    'view_data_transform_log',
    'view_data_transform_log10',
    'view_data_transform_exp',
    'view_data_transform_sqrt',
    'view_data_transform_square',
    'view_data_transform_standardize',
    'view_data_transform_normalize',
]
_VIEW_DATA_CLEAN_HELP_KEYS: List[str] = [
    'view_data_clean_drop_na',
    'view_data_clean_drop_duplicates',
    'view_data_clean_fill_na_mean',
    'view_data_clean_fill_na_median',
    'view_data_clean_fill_na_zero',
    'view_data_clean_remove_outliers_iqr',
    'view_data_clean_remove_outliers_zscore',
]


def _render_view_data_help() -> None:
    """Render help content for View Data mode (pair plots, transform, clean, save)."""
    with st.expander(f"❓ {t('dialog.help_title')}", expanded=False):
        st.markdown(f"**{t('help.view_data_pair_plots_header')}**")
        st.markdown(t('help.view_data_pair_plots_body'))
        st.markdown("---")
        st.markdown(f"**{t('help.view_data_transform_header')}**")
        for key in _VIEW_DATA_TRANSFORM_HELP_KEYS:
            st.markdown(t(f'help.{key}'))
        st.markdown("---")
        st.markdown(f"**{t('help.view_data_clean_header')}**")
        for key in _VIEW_DATA_CLEAN_HELP_KEYS:
            st.markdown(t(f'help.{key}'))
        st.markdown("---")
        st.markdown(f"**{t('help.view_data_save_header')}**")
        st.markdown(t('help.view_data_save_body'))


# Layout-only CSS for data expander (colors come from theme in app)
_EXPANDER_BUTTON_CSS = """
    <style>
    div[data-testid="stExpander"] .stButton > button {
        padding: 0.6rem 2rem; font-size: 1.15rem; min-height: 2.5rem; width: 100%%;
    }
    </style>
"""


def _get_variable_names(data: Any, filter_uncertainty: bool = True) -> List[str]:
    """Get variable names from data (defer loaders import)."""
    from loaders import get_variable_names
    return get_variable_names(data, filter_uncertainty=filter_uncertainty)


def load_uploaded_file(uploaded_file: Any) -> Optional[Any]:
    """
    Load data from an uploaded file (CSV, XLSX, or TXT).

    Args:
        uploaded_file: Streamlit UploadedFile object (e.g. from st.file_uploader).

    Returns:
        DataFrame with loaded data, or None if loading fails.
    """
    from loaders import csv_reader, excel_reader, txt_reader

    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = Path(tmp_file.name)

        try:
            if file_extension == 'csv':
                data = csv_reader(str(tmp_path))
            elif file_extension == 'xlsx':
                data = excel_reader(str(tmp_path))
            elif file_extension == 'txt':
                data = txt_reader(str(tmp_path))
            else:
                st.error(t('error.unsupported_file_type', file_type=file_extension))
                return None
        finally:
            tmp_path.unlink(missing_ok=True)

        logger.info(t('log.data_loaded', rows=len(data), cols=len(data.columns)))
        return data

    except Exception as e:
        logger.error(f"Error loading file: {str(e)}", exc_info=True)
        st.error(t('error.data_load_error', error=str(e)))
        return None


def _render_data_analysis_controls(
    current_data: pd.DataFrame,
    key_prefix: str,
) -> None:
    """Render transform, clean, and download controls for DataFrame data."""
    from data_analysis import (
        CLEAN_OPTIONS,
        TRANSFORM_OPTIONS,
        apply_cleaning,
        apply_transform,
    )

    translated_transforms = {tid: t(f'data_analysis.transform_label_{tid}') for tid in TRANSFORM_OPTIONS}
    translated_cleans = {cid: t(f'data_analysis.clean_label_{cid}') for cid in CLEAN_OPTIONS}

    st.markdown("---")
    st.caption(t('data_analysis.transform_title'))

    r1c1, r1c2 = st.columns([2, 1])
    with r1c1:
        transform_choice = st.selectbox(
            t('data_analysis.select_transform'),
            options=list(translated_transforms.values()),
            key=f'{key_prefix}_transform_select',
            label_visibility='collapsed',
        )
    with r1c2:
        if st.button(t('data_analysis.transform'), key=f'{key_prefix}_transform_btn'):
            tid = next(
                (k for k, v in translated_transforms.items() if v == transform_choice),
                None,
            )
            if tid:
                try:
                    new_data = apply_transform(current_data, tid)
                    st.session_state[f'{key_prefix}_df'] = new_data
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    st.caption(t('data_analysis.clean_title'))
    r2c1, r2c2 = st.columns([2, 1])
    with r2c1:
        clean_choice = st.selectbox(
            t('data_analysis.select_clean'),
            options=list(translated_cleans.values()),
            key=f'{key_prefix}_clean_select',
            label_visibility='collapsed',
        )
    with r2c2:
        if st.button(t('data_analysis.clean'), key=f'{key_prefix}_clean_btn'):
            cid = next(
                (k for k, v in translated_cleans.items() if v == clean_choice),
                None,
            )
            if cid:
                try:
                    new_data = apply_cleaning(current_data, cid)
                    st.session_state[f'{key_prefix}_df'] = new_data
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    st.caption(t('data_analysis.save_updated'))
    save_col1, save_col2 = st.columns([1, 1])
    with save_col1:
        save_format = st.selectbox(
            t('data_analysis.save_title'),
            options=['csv', 'txt', 'xlsx'],
            format_func=lambda x: {
                'csv': t('data_analysis.filetype_csv'),
                'txt': t('data_analysis.filetype_txt'),
                'xlsx': t('data_analysis.filetype_xlsx'),
            }[x],
            key=f'{key_prefix}_save_format',
            label_visibility='collapsed',
        )
    with save_col2:
        ext = {'csv': '.csv', 'txt': '.txt', 'xlsx': '.xlsx'}[save_format]
        if save_format == 'csv':
            buf = current_data.to_csv(index=False, na_rep='no').encode('utf-8')
        elif save_format == 'txt':
            buf = current_data.to_csv(sep='\t', index=False, na_rep='no').encode('utf-8')
        else:
            bio = io.BytesIO()
            current_data.to_excel(bio, index=False)
            buf = bio.getvalue()
        st.download_button(
            t('data_analysis.save_updated'),
            data=buf,
            file_name=f'data{ext}',
            mime={
                'csv': 'text/csv',
                'txt': 'text/plain',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            }[save_format],
            key=f'{key_prefix}_download_btn',
        )


def show_data_with_pair_plots(
    data: Any,
    *,
    key_prefix: Optional[str] = None,
    file_id: Optional[str] = None,
) -> None:
    """
    Show data in an expander with optional pair plots and data analysis (transform/clean/save).

    Args:
        data: DataFrame or data to display.
        key_prefix: If set (e.g. 'view_data'), enables transform/clean/save and uses
            session state for the current data. Required for analysis features.
        file_id: When key_prefix is set, used to detect file changes. When file_id
            changes, the displayed data is reset to the new loaded data.
    """
    display_data = data
    if key_prefix and file_id is not None:
        df_key = f'{key_prefix}_df'
        fid_key = f'{key_prefix}_file_id'
        if st.session_state.get(fid_key) != file_id:
            st.session_state[df_key] = data
            st.session_state[fid_key] = file_id
        if df_key in st.session_state:
            display_data = st.session_state[df_key]

    with st.expander(t('dialog.show_data_title'), expanded=True):
        st.dataframe(display_data)
        st.markdown(_EXPANDER_BUTTON_CSS, unsafe_allow_html=True)

        # Pair plots button
        if key_prefix and isinstance(display_data, pd.DataFrame):
            if st.button(t('dialog.show_pair_plots'), key=f'{key_prefix}_btn_pair', width='stretch'):
                st.session_state[f'{key_prefix}_show_pair_plots'] = True
        else:
            if st.button(t('dialog.show_pair_plots'), key='btn_show_pair_plots', width='stretch'):
                st.session_state['data_show_pair_plots'] = True

        pair_key = f'{key_prefix}_show_pair_plots' if key_prefix else 'data_show_pair_plots'
        if st.session_state.get(pair_key):
            variables = _get_variable_names(display_data, filter_uncertainty=True)
            if len(variables) < 1:
                st.caption(t('error.no_valid_data'))
            else:
                from plotting import create_pair_plots
                fig = create_pair_plots(display_data, variables, output_path=None)
                st.subheader(t('dialog.pair_plots_title'))
                st.pyplot(fig, width="stretch")
                if hasattr(fig, 'close'):
                    fig.close()

        if key_prefix and isinstance(display_data, pd.DataFrame):
            _render_data_analysis_controls(display_data, key_prefix)
            _render_view_data_help()


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
