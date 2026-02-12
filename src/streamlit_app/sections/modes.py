"""Operation modes: normal, multiple datasets, checker, total fitting, view data."""

from typing import List

import streamlit as st

from config import DATA_FILE_TYPES
from i18n import t

from streamlit_app.sections.data import load_uploaded_file, show_data_with_pair_plots
from streamlit_app.sections.fitting import (
    create_equation_options,
    perform_fit,
    select_variables,
    show_equation_selector,
    show_plot_title_checkbox,
)
from streamlit_app.sections.results import show_results


def mode_view_data(_equation_types: List[str]) -> None:
    """Handle view-data mode: load file and show data without fitting (like Tkinter 'Mirar datos')."""
    st.subheader(t('menu.view_data'))
    st.caption(t('workflow.view_data_hint'))

    uploaded_file = st.file_uploader(
        t('dialog.upload_file'),
        type=list(DATA_FILE_TYPES),
        key='view_data_file',
    )

    if uploaded_file is not None:
        data = load_uploaded_file(uploaded_file)
        if data is not None:
            show_data_with_pair_plots(data)


def mode_normal_fitting(equation_types: List[str]) -> None:
    """Handle normal fitting mode (single file, single equation), with optional loop mode."""
    st.subheader(t('menu.normal_fitting'))

    loop_mode = st.checkbox(
        t('workflow.loop_question'),
        key='normal_loop_mode',
        help=t('workflow.loop_help'),
    )

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
                show_title = show_plot_title_checkbox(key_prefix='normal_')
                if st.button(
                    t('menu.normal_fitting'), type="primary", key="fit_btn", width='stretch'
                ):
                    with st.spinner(t('workflow.normal_fitting_title')):
                        result = perform_fit(
                            data, x_name, y_name, equation_name, plot_name,
                            custom_formula, parameter_names,
                            show_title=show_title,
                        )
                        if result:
                            st.session_state.results = [result]
                            if loop_mode:
                                st.session_state.normal_fit_equation = equation_name
                                st.session_state.normal_fit_custom_formula = custom_formula
                                st.session_state.normal_fit_parameter_names = parameter_names

            if st.session_state.results:
                show_results(st.session_state.results)

            # Loop mode: after first fit, allow uploading another file and refitting with same equation
            eq_name = st.session_state.get('normal_fit_equation')
            if loop_mode and st.session_state.results and eq_name is not None:
                custom = st.session_state.get('normal_fit_custom_formula')
                params = st.session_state.get('normal_fit_parameter_names')
                with st.expander(t('workflow.loop_refit_same_equation')):
                    st.caption(t('workflow.loop_refit_caption'))
                    loop_file = st.file_uploader(
                        t('dialog.upload_file'),
                        type=list(DATA_FILE_TYPES),
                        key='single_file_loop',
                    )
                    if loop_file is not None:
                        loop_data = load_uploaded_file(loop_file)
                        if loop_data is not None:
                            loop_x, loop_y, loop_plot = select_variables(
                                loop_data, key_prefix='loop_'
                            )
                            loop_show_title = show_plot_title_checkbox(key_prefix='loop_')
                            if st.button(t('workflow.fit_again'), key='fit_again_btn'):
                                with st.spinner(t('workflow.normal_fitting_title')):
                                    extra = perform_fit(
                                        loop_data, loop_x, loop_y, eq_name, loop_plot,
                                        custom, params,
                                        show_title=loop_show_title,
                                    )
                                    if extra:
                                        st.session_state.results = (
                                            st.session_state.results + [extra]
                                        )
                                        st.rerun()


def mode_multiple_datasets(equation_types: List[str]) -> None:
    """Handle multiple datasets mode (multiple files, single equation), with loop hint."""
    st.subheader(t('menu.multiple_datasets'))
    st.caption(t('workflow.multiple_loop_hint'))

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
                show_title = show_plot_title_checkbox(key_prefix='multiple_')
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
                                        custom_formula, parameter_names,
                                        show_title=show_title,
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
                show_title = show_plot_title_checkbox(key_prefix='checker_')
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
                            result = perform_fit(
                                data, x_name, y_name, equation_name, plot_name,
                                show_title=show_title,
                            )

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
                show_title = show_plot_title_checkbox(key_prefix='total_')

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
                            result = perform_fit(
                                data, x_name, y_name, equation_name, plot_name,
                                show_title=show_title,
                            )

                            if result:
                                results.append(result)

                        progress_bar.progress((idx + 1) / len(equation_types))

                    if results:
                        st.session_state.results = results

            if st.session_state.results:
                show_results(st.session_state.results)
