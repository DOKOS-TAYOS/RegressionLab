"""Help and information section for the Streamlit app."""

import streamlit as st

from i18n import t


def show_help_section() -> None:
    """Display help information in an expandable section."""
    with st.expander(f"ℹ️ {t('menu.information')}", expanded=False):
        st.subheader(t('help.objective_title'))
        st.markdown(t('help.objective_description'))

        st.subheader(t('help.advantages_title'))
        for i in range(1, 10):
            st.markdown(t(f'help.advantage_{i}'))

        st.subheader(t('help.fitting_modes'))
        st.markdown(t('help.normal_fitting'))
        st.markdown(t('help.multiple_datasets'))
        st.markdown(t('help.checker_fitting'))
        st.markdown(t('help.total_fitting'))

        st.subheader(t('help.custom_functions_title').strip())
        st.markdown(t('help.custom_functions_how'))

        st.subheader(t('help.data_format_title'))
        st.markdown(t('help.data_format_named'))
        st.markdown(t('help.data_format_u_prefix'))
        st.markdown(t('help.data_format_non_negative'))
        st.markdown(t('help.data_formats'))

        st.subheader(t('help.stats_title').strip())
        st.markdown(t('help.r_squared_desc'))
        st.markdown(t('help.r_squared_formula'))
        st.markdown(t('help.chi_squared_desc'))
        st.markdown(t('help.chi_squared_formula'))
        st.markdown(t('help.reduced_chi_squared_desc'))
        st.markdown(t('help.reduced_chi_squared_formula'))
        st.markdown(t('help.dof_desc'))
        st.markdown(t('help.dof_formula'))
        st.markdown(t('help.param_ci_95_desc'))
        st.markdown(t('help.param_ci_95_formula'))

        from config import DONATIONS_URL
        if DONATIONS_URL:
            st.link_button(t('dialog.donations'), DONATIONS_URL)
