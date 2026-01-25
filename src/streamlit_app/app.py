#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Streamlit Application for RegressionLab
Web-based interface for curve fitting operations.
"""

import sys
from pathlib import Path

# Add src directory to Python path for proper imports
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from typing import Optional, Tuple, List, Dict, Any
import tempfile
import os
import traceback

# Lightweight imports only at startup (config + heavy deps loaded lazily)
try:
    from i18n import initialize_i18n, t
    from utils.logger import setup_logging, get_logger
    
    # Initialize i18n first (before logging which uses t())
    initialize_i18n('es')  # Default to Spanish, will be changed by user later
    
    # Setup logging after i18n is initialized
    setup_logging()
    logger = get_logger(__name__)
except Exception as e:
    # Fallback error handling if imports fail
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize app: {e}")
    logger.error(traceback.format_exc())
    
    # Create minimal fallback functions
    def t(key: str, **kwargs) -> str:
        return key
    
    def initialize_i18n(language: Optional[str] = None) -> None:
        pass

# ============================================================================
# CONSTANTS
# ============================================================================

EQUATION_FORMULAS = {
    'linear_function_with_n': 'y=mx+n',
    'linear_function': 'y=mx',
    'quadratic_function_complete': 'y=cx²+bx+a',
    'quadratic_function': 'y=ax²',
    'fourth_power': 'y=ax⁴',
    'sin_function': 'y=a sin(bx)',
    'sin_function_with_c': 'y=a sin(bx+c)',
    'cos_function': 'y=a cos(bx)',
    'cos_function_with_c': 'y=a cos(bx+c)',
    'sinh_function': 'y=a sinh(bx)',
    'cosh_function': 'y=a cosh(bx)',
    'ln_function': 'y=a ln(x)',
    'inverse_function': 'y=a/x',
    'inverse_square_function': 'y=a/x²',
}

SIDEBAR_CSS = """
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

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

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


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_uploaded_file(uploaded_file):
    """
    Load data from uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        DataFrame with loaded data or None if loading fails
    """
    from loaders.loading_utils import csv_reader, excel_reader

    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Create temporary file to handle file loading
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            if file_extension == 'csv':
                data = csv_reader(tmp_path)
            elif file_extension in ['xls', 'xlsx']:
                data = excel_reader(tmp_path)
            else:
                st.error(t('error.unsupported_file_type', file_type=file_extension))
                return None
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        logger.info(t('log.data_loaded', rows=len(data), cols=len(data.columns)))
        return data
        
    except Exception as e:
        logger.error(f"Error loading file: {str(e)}", exc_info=True)
        st.error(t('error.data_load_error', error=str(e)))
        return None


# ============================================================================
# FITTING FUNCTIONS
# ============================================================================

def _get_variable_names(data: Any, filter_uncertainty: bool = True) -> List[str]:
    """Lazy wrapper for get_variable_names to defer pandas/loaders import."""
    from loaders.data_loader import get_variable_names
    return get_variable_names(data, filter_uncertainty=filter_uncertainty)


def get_temp_output_dir() -> Path:
    """
    Get or create a temporary directory for plots in Streamlit Cloud.
    Uses session-specific temp directory that persists during the session.
    
    Returns:
        Path to temporary output directory
    """
    if 'temp_output_dir' not in st.session_state:
        # Create a temporary directory for this session
        temp_dir = tempfile.mkdtemp(prefix='regressionlab_')
        st.session_state.temp_output_dir = temp_dir
        logger.info(f"Created temporary output directory: {temp_dir}")
    return Path(st.session_state.temp_output_dir)


def perform_fit(
    data,  # pd.DataFrame - type annotation removed for lazy loading
    x_name: str,
    y_name: str,
    equation_name: str,
    plot_name: str,
    custom_formula: Optional[str] = None,
    parameter_names: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Perform curve fitting and return results.
    
    Args:
        data: DataFrame with data
        x_name: X variable name
        y_name: Y variable name
        equation_name: Type of equation to fit
        plot_name: Name for the plot
        custom_formula: Optional custom formula
        parameter_names: Optional parameter names for custom formula
        
    Returns:
        Dictionary with fitting results or None if fitting fails
    """
    from fitting.fitting_utils import get_fitting_function
    from fitting.custom_function_evaluator import CustomFunctionEvaluator
    from plotting.plot_utils import create_plot
    from utils.exceptions import FittingError

    try:
        # Get fitting function
        if equation_name == 'custom_formula' and custom_formula and parameter_names:
            # Custom formula
            evaluator = CustomFunctionEvaluator(custom_formula, parameter_names)
            fit_function = evaluator.fit
        else:
            # Predefined equation
            fit_function = get_fitting_function(equation_name)
            if fit_function is None:
                st.error(t('error.fitting_error'))
                return None
        
        # Perform fitting
        text, y_fitted, equation, r_squared = fit_function(data, x_name, y_name)
        
        # Extract data for plotting
        x = data[x_name]
        y = data[y_name]
        
        # Get uncertainties if they exist, otherwise use zeros
        ux_col = f'u{x_name}'
        uy_col = f'u{y_name}'
        ux = data[ux_col] if ux_col in data.columns else [0.0] * len(x)
        uy = data[uy_col] if uy_col in data.columns else [0.0] * len(y)
        
        # Create plot in temporary directory (Streamlit Cloud compatible)
        display_name = equation_name.replace('_', ' ').title()
        st.session_state.plot_counter += 1
        filename = f"{plot_name}_{st.session_state.plot_counter}"
        out_path = get_temp_output_dir() / f"fit_{filename}.png"
        output_path = create_plot(
            x, y, ux, uy, y_fitted, filename, x_name, y_name,
            output_path=str(out_path),
        )
        
        return {
            'equation_name': display_name,
            'parameters': text,
            'equation': equation,
            'r_squared': r_squared,
            'plot_path': output_path,
            'plot_name': plot_name
        }
        
    except FittingError as e:
        st.error(t('error.fitting_failed_details', error=str(e)))
        return None
    except Exception as e:
        st.error(t('error.fitting_failed_generic', error_type=type(e).__name__, error=str(e)))
        logger.error(f"Fitting error: {str(e)}", exc_info=True)
        return None


# ============================================================================
# UI COMPONENTS
# ============================================================================

def _select_variables(data: Any, key_prefix: str = '') -> Tuple[str, str, str]:
    """
    Show variable selection widgets and return selected values.
    
    Args:
        data: DataFrame with data
        key_prefix: Prefix for widget keys to ensure uniqueness
        
    Returns:
        Tuple of (x_name, y_name, plot_name)
    """
    variables = _get_variable_names(data, filter_uncertainty=True)
    x_default_idx = 0 if len(variables) > 0 else None
    y_default_idx = 1 if len(variables) > 1 else (0 if len(variables) > 0 else None)
    
    x_name = st.selectbox(
        t('dialog.independent_variable'),
        variables,
        index=x_default_idx,
        key=f'{key_prefix}x' if key_prefix else None
    )
    y_name = st.selectbox(
        t('dialog.dependent_variable'),
        variables,
        index=y_default_idx,
        key=f'{key_prefix}y' if key_prefix else None
    )
    plot_name = st.text_input(
        t('dialog.plot_name'),
        value="fit",
        key=f'{key_prefix}plot' if key_prefix else None
    )
    
    return x_name, y_name, plot_name


def show_help_section() -> None:
    """Display help information in an expandable section."""
    with st.expander(f"ℹ️ {t('menu.information')}", expanded=False):
        # Objective Section
        st.subheader(t('help.objective_title'))
        st.markdown(t('help.objective_description'))
        
        # Advantages Section
        st.subheader(t('help.advantages_title'))
        for i in range(1, 10):
            st.markdown(t(f'help.advantage_{i}'))
        
        # Fitting Modes Section
        st.subheader(t('help.fitting_modes'))
        st.markdown(t('help.normal_fitting'))
        st.markdown(t('help.multiple_datasets'))
        st.markdown(t('help.checker_fitting'))
        st.markdown(t('help.total_fitting'))
        
        # Input Data Format Section
        st.subheader(t('help.data_format_title'))
        st.markdown(t('help.data_format_named'))
        st.markdown(t('help.data_format_u_prefix'))
        st.markdown(t('help.data_format_non_negative'))
        
        # Data Location Section
        st.markdown(t('help.data_formats'))

def _create_equation_options(equation_types: List[str]) -> Dict[str, str]:
    """
    Create equation options mapping display text to equation key.
    
    Args:
        equation_types: List of equation type keys
        
    Returns:
        Dictionary mapping display text to equation key
    """
    equation_options = {}
    for eq in equation_types:
        eq_name = t(f'equations.{eq}')
        eq_formula = EQUATION_FORMULAS.get(eq, '')
        display_text = f"{eq_name} - {eq_formula}" if eq_formula else eq_name
        equation_options[display_text] = eq
    
    # Add custom formula option
    equation_options[t('equations.custom_formula')] = 'custom_formula'
    return equation_options


def show_equation_selector(equation_types: List[str]) -> Tuple[str, Optional[str], Optional[List[str]]]:
    """
    Show equation type selector and return selection.

    Args:
        equation_types: List of equation type keys (e.g. from config.AVAILABLE_EQUATION_TYPES).

    Returns:
        Tuple of (equation_name, custom_formula, parameter_names)
    """
    equation_options = _create_equation_options(equation_types)
    
    selected_label = st.selectbox(
        t('dialog.select_equation'),
        options=list(equation_options.keys())
    )
    
    selected_equation = equation_options[selected_label]
    custom_formula = None
    parameter_names = None
    
    # If custom formula is selected, show input fields
    if selected_equation == 'custom_formula':
        st.info(t('dialog.formula_example'))
        
        num_params = st.number_input(
            t('dialog.num_parameters'),
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )
        
        parameter_names = []
        cols = st.columns(min(int(num_params), 3))
        for i in range(int(num_params)):
            col_idx = i % len(cols)
            with cols[col_idx]:
                param_name = st.text_input(
                    t('dialog.parameter_name', index=i+1),
                    value=f'p{i+1}',
                    key=f'param_{i}'
                )
                parameter_names.append(param_name)
        
        custom_formula = st.text_input(
            t('dialog.custom_formula_prompt'),
            placeholder="a*t**2 + b*t + c"
        )
    
    return selected_equation, custom_formula, parameter_names


def show_results(results: List[Dict[str, Any]]) -> None:
    """
    Display fitting results with download options.
    
    Args:
        results: List of result dictionaries
    """
    if not results:
        return

    st.markdown('---')
    st.header(t('dialog.results_title'))
    
    for idx, result in enumerate(results):
        with st.container():
            st.markdown(f"### {result['plot_name']} - {result['equation_name']}")
            
            # Display equation
            st.markdown(f"**{t('dialog.equation')}** {result['equation']}")
            
            # Display parameters and download button side by side
            if os.path.exists(result['plot_path']):
                param_col, download_col = st.columns([3, 1])
                
                with param_col:
                    st.text(result['parameters'])
                
                with download_col:
                    with open(result['plot_path'], "rb") as file:
                        st.download_button(
                            label=f"📥 {t('dialog.download')}",
                            data=file,
                            file_name=f"{result['plot_name']}.png",
                            mime="image/png",
                            key=f"download_{idx}",
                            width='stretch'
                        )
                
                st.image(result['plot_path'], width='stretch')
            else:
                st.text(result['parameters'])


# ============================================================================
# OPERATION MODES
# ============================================================================

def mode_normal_fitting(equation_types: List[str]) -> None:
    """Handle normal fitting mode (single file, single equation)."""
    st.subheader(t('menu.normal_fitting'))
    
    uploaded_file = st.file_uploader(t('dialog.upload_file'), type=['csv', 'xls', 'xlsx'], key='single_file')
    
    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
        
        if data is not None:
            with st.expander(t('dialog.show_data_title')):
                st.dataframe(data)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                x_name, y_name, plot_name = _select_variables(data)
            
            with col2:
                equation_name, custom_formula, parameter_names = show_equation_selector(equation_types)
                
                if st.button(t('menu.normal_fitting'), type="primary", key="fit_btn", width='stretch'):
                    with st.spinner(t('workflow.normal_fitting_title')):
                        result = perform_fit(
                            data, x_name, y_name, equation_name, plot_name,
                            custom_formula, parameter_names
                        )
                        
                        if result:
                            st.session_state.results = [result]
            
            if st.session_state.results:
                show_results(st.session_state.results)


def mode_multiple_datasets(equation_types: List[str]) -> None:
    """Handle multiple datasets mode (multiple files, single equation)."""
    st.subheader(t('menu.multiple_datasets'))
    
    equation_name, custom_formula, parameter_names = show_equation_selector(equation_types)
    
    uploaded_files = st.file_uploader(
        t('dialog.upload_file'), type=['csv', 'xls', 'xlsx'],
        accept_multiple_files=True, key='multiple_files'
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} uploaded files.")
        
        # Load all data
        files_data = {}
        for idx, uploaded_file in enumerate(uploaded_files):
            data = load_uploaded_file(uploaded_file)
            if data is not None:
                files_data[idx] = data
        
        if files_data:
            # Display files in pairs (2 columns)
            for i in range(0, len(uploaded_files), 2):
                pair_cols = st.columns(2)
                
                for col_idx in range(2):
                    file_idx = i + col_idx
                    if file_idx >= len(uploaded_files):
                        break
                    
                    uploaded_file = uploaded_files[file_idx]
                    with pair_cols[col_idx]:
                        st.markdown(f"### {uploaded_file.name} (#{file_idx + 1})")
                        
                        if file_idx in files_data:
                            data = files_data[file_idx]
                            _select_variables(data, key_prefix=f'{file_idx}_')
            
            # Centered execute button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(t('menu.multiple_datasets'), type="primary", key="fit_multiple_btn", width='stretch'):
                    results = []
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        if idx in files_data:
                            data = files_data[idx]
                            
                            x_name = st.session_state.get(f'{idx}_x')
                            y_name = st.session_state.get(f'{idx}_y')
                            plot_name = st.session_state.get(f'{idx}_plot', uploaded_file.name.split('.')[0])
                            
                            if x_name and y_name:
                                with st.spinner(f"{t('workflow.multiple_fitting_title')} {uploaded_file.name} (#{idx + 1})"):
                                    result = perform_fit(
                                        data, x_name, y_name, equation_name, plot_name,
                                        custom_formula, parameter_names
                                    )
                                    
                                    if result:
                                        results.append(result)
                    
                    if results:
                        st.session_state.results = results
                    st.rerun()
        
        if st.session_state.results:
            show_results(st.session_state.results)


def mode_checker_fitting(equation_types: List[str]) -> None:
    """Handle checker fitting mode (single file, multiple equations)."""
    st.subheader(t('menu.checker_fitting'))
    
    uploaded_file = st.file_uploader(t('dialog.upload_file'), type=['csv', 'xls', 'xlsx'], key='checker_file')
    
    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
        
        if data is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                x_name, y_name, plot_name = _select_variables(data, key_prefix='checker_')
            
            with col2:
                equation_options = _create_equation_options(equation_types)
                # Remove custom formula from checker mode
                equation_options_filtered = {k: v for k, v in equation_options.items() 
                                            if v != 'custom_formula'}
                
                selected_labels = st.multiselect(
                    t('dialog.select_equation'),
                    options=list(equation_options_filtered.keys()),
                    default=list(equation_options_filtered.keys())[:3]
                )
                
                selected_equations = [equation_options_filtered[label] for label in selected_labels]
                
                if st.button(t('menu.checker_fitting'), type="primary", key="checker_fit_btn", width='stretch'):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, equation_name in enumerate(selected_equations):
                        with st.spinner(f"{t('workflow.fitting_title', name=equation_name)}"):
                            result = perform_fit(data, x_name, y_name, equation_name, plot_name)
                            
                            if result:
                                results.append(result)
                        
                        progress_bar.progress((idx + 1) / len(selected_equations))
                    
                    if results:
                        st.session_state.results = results
            
            if st.session_state.results:
                show_results(st.session_state.results)


def mode_total_fitting(equation_types: List[str]) -> None:
    """Handle total fitting mode (single file, all equations)."""
    st.subheader(t('menu.total_fitting'))
    
    uploaded_file = st.file_uploader(t('dialog.upload_file'), type=['csv', 'xls', 'xlsx'], key='total_file')
    
    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
        
        if data is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                x_name, y_name, plot_name = _select_variables(data, key_prefix='total_')
            
            with col2:
                st.info(f"📊 {t('menu.total_fitting')}: {len(equation_types)}")
                
                if st.button(t('menu.total_fitting'), type="primary", key="total_fit_btn", width='stretch'):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, equation_name in enumerate(equation_types):
                        with st.spinner(f"{t('workflow.fitting_title', name=equation_name)}"):
                            result = perform_fit(data, x_name, y_name, equation_name, plot_name)
                            
                            if result:
                                results.append(result)
                        
                        progress_bar.progress((idx + 1) / len(equation_types))
                    
                    if results:
                        st.session_state.results = results
            
            if st.session_state.results:
                show_results(st.session_state.results)
            


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def _setup_sidebar(version: str) -> str:
    """
    Setup and render sidebar with language selector and mode options.
    
    Args:
        version: Application version string
        
    Returns:
        Selected operation mode
    """
    with st.sidebar:
        st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

        # Brand header
        st.markdown(f"""
            <div class="sidebar-brand">
                <h2>📊 RegressionLab</h2>
                <span class="version">v{version}</span>
            </div>
        """, unsafe_allow_html=True)

        # Language selector
        next_lang = "English 🇬🇧" if st.session_state.language == 'es' else "Español 🇪🇸"
        if st.button(next_lang, key="lang_toggle", width='stretch'):
            toggle_language()
            st.rerun()

        section_title = t('help.fitting_modes').replace("\n", "").strip()
        st.markdown(f'<p class="sidebar-section">{section_title}</p>', unsafe_allow_html=True)

        # Operation mode selector
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


def _show_logo() -> None:
    """Display application logo or fallback header."""
    logo_path = Path(__file__).parent.parent.parent / "images" / "RegressionLab_logo.png"
    logo_bytes = _cached_logo_bytes(str(logo_path))
    
    if logo_bytes is not None:
        st.image(logo_bytes, width='content')
    else:
        st.markdown("""
            <h1 style='text-align: center; color: #1f77b4; font-size: 3.5em; font-weight: bold; margin-bottom: 0;'>
                RegressionLab
            </h1>
            <p style='text-align: center; color: #666; font-size: 1.2em; margin-top: 0;'>
                📈 Curve Fitting & Data Analysis
            </p>
        """, unsafe_allow_html=True)


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
        # Page configuration MUST be first Streamlit call
        st.set_page_config(
            page_title="RegressionLab",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    except Exception as e:
        # If page config was already set, continue
        logger.warning(f"Page config already set: {e}")
    
    try:
        # Initialize session state and i18n
        initialize_session_state()
        initialize_i18n(st.session_state.language)
        
        # Setup sidebar and get operation mode
        operation_mode = _setup_sidebar(__version__)
        
        # Display logo and help section
        _show_logo()
        show_help_section()
        
        # Route to appropriate mode handler
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
