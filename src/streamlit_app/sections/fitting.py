"""Fitting logic and equation selection UI for the Streamlit app."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from i18n import t
from utils import get_logger

from streamlit_app.sections.data import get_temp_output_dir, get_variable_names

logger = get_logger(__name__)


def perform_fit(
    data: Any,
    x_name: str,
    y_name: str,
    equation_name: str,
    plot_name: str,
    custom_formula: Optional[str] = None,
    parameter_names: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Perform curve fitting for the given dataset and equation selection.

    This helper wraps the core fitting logic used by the Streamlit UI:
    it resolves either a predefined fitting function or a custom
    :class:`~fitting.custom_function_evaluator.CustomFunctionEvaluator`,
    computes the fit and generates the corresponding plot.

    Args:
        data: Dataset with columns ``x_name``, ``y_name`` and optionally
            their uncertainties ``u{x_name}``, ``u{y_name}``.
        x_name: Name of the independent variable column.
        y_name: Name of the dependent variable column.
        equation_name: Internal equation identifier or ``'custom_formula'``.
        plot_name: Base name used for the generated plot.
        custom_formula: Custom formula string when ``equation_name`` is
            ``'custom_formula'``.
        parameter_names: List of parameter names used in ``custom_formula``.

    Returns:
        Dictionary with keys ``equation_name``, ``parameters``, ``equation``,
        ``plot_path`` and ``plot_name`` when the fit succeeds, or ``None``
        if the operation fails or is not supported.
    """
    from fitting import CustomFunctionEvaluator, get_fitting_function
    from plotting import create_plot
    from utils import FittingError
    from config import FILE_CONFIG

    try:
        if equation_name == 'custom_formula' and custom_formula and parameter_names:
            evaluator = CustomFunctionEvaluator(custom_formula, parameter_names)
            fit_function = evaluator.fit
        else:
            fit_function = get_fitting_function(equation_name)
            if fit_function is None:
                st.error(t('error.fitting_error'))
                return None

        result_fit = fit_function(data, x_name, y_name)
        text, y_fitted, equation = result_fit[0], result_fit[1], result_fit[2]
        fit_info = result_fit[3] if len(result_fit) >= 4 else None

        x = data[x_name]
        y = data[y_name]
        ux_col = f'u{x_name}'
        uy_col = f'u{y_name}'
        ux = data[ux_col] if ux_col in data.columns else [0.0] * len(x)
        uy = data[uy_col] if uy_col in data.columns else [0.0] * len(y)

        display_name = equation_name.replace('_', ' ').title()
        st.session_state.plot_counter += 1
        filename = f"{plot_name}_{st.session_state.plot_counter}"
        plot_ext = FILE_CONFIG.get('plot_format', 'png')
        out_path = get_temp_output_dir() / f"fit_{filename}.{plot_ext}"
        output_path = create_plot(
            x, y, ux, uy, y_fitted, filename, x_name, y_name,
            output_path=str(out_path),
            fit_info=fit_info,
        )

        result: Dict[str, Any] = {
            'equation_name': display_name,
            'parameters': text,
            'equation': equation,
            'plot_path': output_path,
            'plot_name': plot_name
        }
        # When output is PDF, plotting creates a _preview.png for display; use it for in-app visualization
        if Path(output_path).suffix.lower() == '.pdf':
            preview = Path(output_path).parent / (Path(output_path).stem + '_preview.png')
            if preview.exists():
                result['plot_path_display'] = str(preview)
        return result

    except FittingError as e:
        st.error(t('error.fitting_failed_details', error=str(e)))
        return None
    except Exception as e:
        st.error(t('error.fitting_failed_generic', error_type=type(e).__name__, error=str(e)))
        logger.error(f"Fitting error: {str(e)}", exc_info=True)
        return None


def _create_equation_options(equation_types: List[str]) -> Dict[str, str]:
    """
    Build a mapping from translated equation labels to internal keys.

    Args:
        equation_types: List of internal equation identifiers.

    Returns:
        Dictionary mapping human‑readable labels to equation keys,
        including a ``'custom_formula'`` entry.
    """
    equation_options: Dict[str, str] = {}
    for eq in equation_types:
        eq_name = t(f'equations.{eq}')
        equation_options[eq_name] = eq
    equation_options[t('equations.custom_formula')] = 'custom_formula'
    return equation_options


def select_variables(data: Any, key_prefix: str = '') -> Tuple[str, str, str]:
    """
    Show variable selection widgets and return the chosen variables and plot name.

    Args:
        data: Dataset from which variables are extracted.
        key_prefix: Optional prefix for Streamlit widget keys to avoid clashes.

    Returns:
        Tuple ``(x_name, y_name, plot_name)`` selected by the user.
    """
    variables = get_variable_names(data, filter_uncertainty=True)
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


def show_equation_selector(
    equation_types: List[str]
) -> Tuple[str, Optional[str], Optional[List[str]]]:
    """
    Show equation type selector in the sidebar/content area.

    Args:
        equation_types: List of available equation identifiers.

    Returns:
        Tuple ``(equation_key, custom_formula, parameter_names)`` where
        ``custom_formula`` and ``parameter_names`` are only populated
        when the custom‑formula option is selected.
    """
    from config import EQUATIONS

    equation_options = _create_equation_options(equation_types)

    selected_label = st.selectbox(
        t('dialog.select_equation'),
        options=list(equation_options.keys()),
        key='equation_selector'
    )

    selected_equation = equation_options[selected_label]
    if selected_equation != 'custom_formula':
        desc = t(f'equations_descriptions.{selected_equation}')
        formula = EQUATIONS.get(selected_equation, {}).get("formula", "")
        st.caption(f"**{desc}** — {formula}")
    custom_formula = None
    parameter_names = None

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
                    t('dialog.parameter_name', index=i + 1),
                    value=f'p{i + 1}',
                    key=f'param_{i}'
                )
                parameter_names.append(param_name)

        custom_formula = st.text_input(
            t('dialog.custom_formula_prompt'),
            placeholder="a*t**2 + b*t + c"
        )

    return selected_equation, custom_formula, parameter_names


def create_equation_options(equation_types: List[str]) -> Dict[str, str]:
    """
    Public wrapper around :func:`_create_equation_options`.

    This function is imported by the modes module to build the mapping
    from translated labels to equation identifiers.
    """
    return _create_equation_options(equation_types)
