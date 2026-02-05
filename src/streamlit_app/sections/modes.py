"""Operation modes: normal, multiple datasets, checker, total fitting."""

from typing import List

import streamlit as st

from config import DATA_FILE_TYPES
from i18n import t

from .data import load_uploaded_file, show_data_with_pair_plots
from .fitting import (
    create_equation_options,
    perform_fit,
    select_variables,
    show_equation_selector,
)
from .results import show_results


def mode_normal_fitting(equation_types: List[str]) -> None:
    """Handle normal fitting mode (single file, single equation)."""
    st.subheader(t('menu.normal_fitting'))

    uploaded_file = st.file_uploader(
        t('dialog.upload_file'),
        type=list(DATA_FILE_TYPES),
        key='single_file',
    )

    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)

        if data is not None:
            show_data_with_pair_plots(data)

            col1, col2 = st.columns([1, 1])

            with col1:
                x_name, y_name, plot_name = select_variables(data)

            with col2:
                equation_name, custom_formula, parameter_names = (
                    show_equation_selector(equation_types)
                )
                if st.button(
                    t('menu.normal_fitting'), type="primary", key="fit_btn", width='stretch'
                ):
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
        t('dialog.upload_file'),
        type=list(DATA_FILE_TYPES),
        accept_multiple_files=True,
        key='multiple_files',
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} uploaded files.")

        files_data = {}
        for idx, uploaded_file in enumerate(uploaded_files):
            data = load_uploaded_file(uploaded_file)
            if data is not None:
                files_data[idx] = data

        if files_data:
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
                            select_variables(data, key_prefix=f'{file_idx}_')

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    t('menu.multiple_datasets'),
                    type="primary",
                    key="fit_multiple_btn",
                    width='stretch'
                ):
                    results = []

                    for idx, uploaded_file in enumerate(uploaded_files):
                        if idx in files_data:
                            data = files_data[idx]

                            x_name = st.session_state.get(f'{idx}_x')
                            y_name = st.session_state.get(f'{idx}_y')
                            plot_name = st.session_state.get(
                                f'{idx}_plot', uploaded_file.name.split('.')[0]
                            )

                            if x_name and y_name:
                                title = (
                                    f"{t('workflow.multiple_fitting_title')} "
                                    f"{uploaded_file.name} (#{idx + 1})"
                                )
                                with st.spinner(title):
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

    uploaded_file = st.file_uploader(
        t('dialog.upload_file'),
        type=list(DATA_FILE_TYPES),
        key='checker_file',
    )

    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)

        if data is not None:
            show_data_with_pair_plots(data)

            col1, col2 = st.columns([1, 1])

            with col1:
                x_name, y_name, plot_name = select_variables(data, key_prefix='checker_')

            with col2:
                equation_options = create_equation_options(equation_types)
                equation_options_filtered = {
                    k: v for k, v in equation_options.items() if v != 'custom_formula'
                }

                selected_labels = st.multiselect(
                    t('dialog.select_equation'),
                    options=list(equation_options_filtered.keys()),
                    default=list(equation_options_filtered.keys())[:3]
                )

                selected_equations = [
                    equation_options_filtered[label] for label in selected_labels
                ]
                if st.button(
                    t('menu.checker_fitting'),
                    type="primary",
                    key="checker_fit_btn",
                    width='stretch'
                ):
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

    uploaded_file = st.file_uploader(
        t('dialog.upload_file'),
        type=list(DATA_FILE_TYPES),
        key='total_file',
    )

    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)

        if data is not None:
            show_data_with_pair_plots(data)

            col1, col2 = st.columns([1, 1])

            with col1:
                x_name, y_name, plot_name = select_variables(data, key_prefix='total_')

            with col2:
                st.info(f"📊 {t('menu.total_fitting')}: {len(equation_types)}")

                if st.button(
                    t('menu.total_fitting'),
                    type="primary",
                    key="total_fit_btn",
                    width='stretch'
                ):
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
