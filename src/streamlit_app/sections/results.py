"""Results display for the Streamlit app."""

import os
from typing import Any, Dict, List

import streamlit as st

from i18n import t


def show_results(results: List[Dict[str, Any]]) -> None:
    """Display fitting results with download options."""
    if not results:
        return

    st.markdown('---')
    st.header(t('dialog.results_title'))

    for idx, result in enumerate(results):
        with st.container():
            st.markdown(f"### {result['plot_name']} - {result['equation_name']}")
            st.markdown(f"**{t('dialog.equation')}** {result['equation']}")

            if os.path.exists(result['plot_path']):
                param_col, download_col = st.columns([3, 1])
                plot_path = result['plot_path']
                plot_ext = os.path.splitext(plot_path)[1].lower() or '.png'
                mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.pdf': 'application/pdf'}
                mime = mime_map.get(plot_ext, 'image/png')
                download_name = f"{result['plot_name']}{plot_ext}"

                with param_col:
                    st.text(result['parameters'])

                with download_col:
                    with open(plot_path, "rb") as file:
                        st.download_button(
                            label=f"📥 {t('dialog.download')}",
                            data=file,
                            file_name=download_name,
                            mime=mime,
                            key=f"download_{idx}",
                            width='stretch'
                        )

                if plot_ext in ('.png', '.jpg', '.jpeg'):
                    st.image(plot_path, width='stretch')
                else:
                    st.caption(f"Plot saved as {plot_ext}. Download to view.")
            else:
                st.text(result['parameters'])
