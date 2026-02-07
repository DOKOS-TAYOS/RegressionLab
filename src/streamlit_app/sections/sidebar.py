"""Sidebar, session state, and logo for the Streamlit app."""

from pathlib import Path
from typing import Optional

import streamlit as st

from i18n import initialize_i18n, t

_SIDEBAR_CSS = """
    <style>
    .sidebar-brand {
        text-align: center;
        padding: 0.5rem 0 1rem 0;
        border-bottom: 2px solid rgba(49, 51, 63, 0.2);
        margin-bottom: 1rem;
    }
    .sidebar-brand h2 {
        color: #1f77b4;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .sidebar-brand .version {
        display: inline-block;
        background: linear-gradient(135deg, #1f77b4 0%, #2a9d8f 100%);
        color: white;
        font-size: 0.7rem;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        margin-top: 0.35rem;
        font-weight: 600;
    }
    .sidebar-section {
        margin: 1.25rem 0 0.75rem 0;
        font-size: 0.8rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stSidebar"] .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.25);
    }
    div[data-testid="stSidebar"] [data-testid="stRadio"] > label {
        font-size: 0.9rem;
    }
    </style>
"""


@st.cache_data
def _cached_logo_bytes(path: str) -> Optional[bytes]:
    """Load logo from disk once; cache for reruns."""
    p = Path(path)
    return p.read_bytes() if p.exists() else None


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if 'language' not in st.session_state:
        st.session_state.language = 'es'
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'plot_counter' not in st.session_state:
        st.session_state.plot_counter = 0


def toggle_language() -> None:
    """Toggle between Spanish and English."""
    if st.session_state.language == 'es':
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'es'
    initialize_i18n(st.session_state.language)


def setup_sidebar(version: str) -> str:
    """
    Setup and render the sidebar with language selector and mode options.

    Args:
        version: Application version string to display in the sidebar.

    Returns:
        Selected operation mode (e.g. 'normal_fitting', 'watch_data').
    """
    with st.sidebar:
        st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="sidebar-brand">
                <h2>📊 RegressionLab</h2>
                <span class="version">v{version}</span>
            </div>
        """, unsafe_allow_html=True)

        next_lang = t('menu.language_english') if st.session_state.language == 'es' else t('menu.language_spanish')
        if st.button(next_lang, key="lang_toggle", width='stretch'):
            toggle_language()
            st.rerun()

        section_title = t('help.fitting_modes').replace("\n", "").strip()
        st.markdown(f'<p class="sidebar-section">{section_title}</p>', unsafe_allow_html=True)

        mode_options = [
            t('menu.normal_fitting'),
            t('menu.multiple_datasets'),
            t('menu.checker_fitting'),
            t('menu.total_fitting'),
        ]
        operation_mode = st.radio(
            t('help.fitting_modes'),
            mode_options,
            label_visibility="collapsed",
        )
        return operation_mode


def show_logo() -> None:
    """Display application logo or fallback header."""
    # __file__ is streamlit_app/sections/sidebar.py -> parent.parent = streamlit_app, parent.parent.parent = src, project root = parent.parent.parent.parent
    logo_path = Path(__file__).resolve().parent.parent.parent.parent / "images" / "RegressionLab_logo.png"
    logo_bytes = _cached_logo_bytes(str(logo_path))

    if logo_bytes is not None:
        st.image(logo_bytes, width='content')
    else:
        st.markdown("""
            <h1 style='text-align: center; color: #1f77b4; font-size: 3.5em;
                font-weight: bold; margin-bottom: 0;'>
                RegressionLab
            </h1>
            <p style='text-align: center; color: #666; font-size: 1.2em; margin-top: 0;'>
                📈 Curve Fitting & Data Analysis
            </p>
        """, unsafe_allow_html=True)
