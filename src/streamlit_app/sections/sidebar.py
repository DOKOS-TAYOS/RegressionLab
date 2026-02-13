"""Sidebar, session state, and logo for the Streamlit app."""

from pathlib import Path
from typing import Optional

import streamlit as st

from config import SUPPORTED_LANGUAGE_CODES
from i18n import initialize_i18n, t
from streamlit_app.theme import get_streamlit_theme

# Key for "switch to X" button label per language code
_LANG_MENU_KEYS: dict[str, str] = {
    'es': 'menu.language_spanish',
    'en': 'menu.language_english',
    'de': 'menu.language_german',
}

# Layout-only CSS (colors come from theme via get_main_css in app)
_SIDEBAR_LAYOUT_CSS = """
    <style>
    .sidebar-brand {
        text-align: center;
        padding: 0.5rem 0 1rem 0;
        border-bottom: 2px solid rgba(255,255,255,0.08);
        margin-bottom: 1rem;
    }
    .sidebar-brand h2 { font-size: 1.4rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
    .sidebar-brand .version-badge {
        display: inline-block;
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
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stSidebar"] [data-testid="stRadio"] > label { font-size: 0.9rem; }
    </style>
"""


@st.cache_data
def _cached_logo_bytes(path: str) -> Optional[bytes]:
    """Load logo from disk once; cache for reruns."""
    p = Path(path)
    return p.read_bytes() if p.exists() else None


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables (language from config env)."""
    if 'language' not in st.session_state:
        from config import get_env_from_schema
        st.session_state.language = get_env_from_schema('LANGUAGE')
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'plot_counter' not in st.session_state:
        st.session_state.plot_counter = 0


def cycle_language() -> None:
    """Cycle to the next supported language (es -> en -> de -> es)."""
    codes = list(SUPPORTED_LANGUAGE_CODES)
    try:
        idx = codes.index(st.session_state.language)
    except ValueError:
        idx = 0
    next_idx = (idx + 1) % len(codes)
    st.session_state.language = codes[next_idx]
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
        st.markdown(_SIDEBAR_LAYOUT_CSS, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="sidebar-brand">
                <h2>📊 RegressionLab</h2>
                <span class="version-badge">v{version}</span>
            </div>
        """, unsafe_allow_html=True)

        codes = list(SUPPORTED_LANGUAGE_CODES)
        try:
            current_idx = codes.index(st.session_state.language)
        except ValueError:
            current_idx = 0
        next_idx = (current_idx + 1) % len(codes)
        next_code = codes[next_idx]
        next_lang_label = t(_LANG_MENU_KEYS[next_code])
        if st.button(next_lang_label, key="lang_toggle", width='stretch'):
            cycle_language()
            st.rerun()

        section_title = t('help.fitting_modes').replace("\n", "").strip()
        st.markdown(f'<p class="sidebar-section">{section_title}</p>', unsafe_allow_html=True)

        mode_options = [
            t('menu.normal_fitting'),
            t('menu.multiple_datasets'),
            t('menu.checker_fitting'),
            t('menu.total_fitting'),
            t('menu.view_data'),
        ]
        operation_mode = st.radio(
            t('help.fitting_modes'),
            mode_options,
            label_visibility="collapsed",
        )

        return operation_mode


def show_logo() -> None:
    """Display application logo or fallback header (colors from config theme)."""
    # __file__ is streamlit_app/sections/sidebar.py -> parent.parent = streamlit_app, parent.parent.parent = src, project root = parent.parent.parent.parent
    logo_path = Path(__file__).resolve().parent.parent.parent.parent / "images" / "RegressionLab_logo.png"
    logo_bytes = _cached_logo_bytes(str(logo_path))
    theme = st.session_state.get("streamlit_theme") or get_streamlit_theme()
    primary = theme['button_fg_primary']
    muted = theme['muted']

    if logo_bytes is not None:
        st.image(logo_bytes, width='content')
    else:
        st.markdown(f"""
            <h1 class="main-title" style='text-align: center; color: {primary}; font-size: 3.5em;
                font-weight: bold; margin-bottom: 0;'>
                RegressionLab
            </h1>
            <p style='text-align: center; color: {muted}; font-size: 1.2em; margin-top: 0;'>
                📈 Curve Fitting & Data Analysis
            </p>
        """, unsafe_allow_html=True)
