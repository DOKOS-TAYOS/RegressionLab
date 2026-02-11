"""Results display for the Streamlit app."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st

from i18n import t

# MIME types for plot download buttons
_PLOT_MIME_BY_EXT: Dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".pdf": "application/pdf",
}
_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def _split_equation(equation_str: str) -> Tuple[str, str]:
    """Split equation string into formula (optional) and formatted equation. Both left-aligned."""
    parts = equation_str.strip().split("\n", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "", parts[0].strip()


def _split_parameters_text(text: str) -> Tuple[List[str], List[str]]:
    """
    Split backend parameters text into:
    - Statistics: R², RMSE, χ², χ²_red, dof (exactly 5 lines).
    - Parameters: fit params (a, b, c) with uncertainties and their IC 95%.
    Backend order: (param=value , σ(param)=unc)* then 5 stats lines then (param IC 95%)*.
    """
    lines = [ln.strip() for ln in text.strip().split("\n") if ln.strip()]
    # Find where statistics start (first line containing R²)
    stats_start = -1
    for i, ln in enumerate(lines):
        if "R²" in ln or "R\u00B2" in ln:
            stats_start = i
            break
    if stats_start < 0:
        return [], lines
    stats_lines = lines[stats_start : stats_start + 5]
    param_value_lines = lines[:stats_start]  # param=value , σ(param)=unc
    param_ci_lines = lines[stats_start + 5 :]  # param IC 95%: [...]
    param_lines = param_value_lines + param_ci_lines
    return stats_lines, param_lines


def _get_plot_display_path(result: Dict[str, Any]) -> Tuple[str, str]:
    """Return (path_for_display, path_for_download) for a result's plot."""
    plot_path = result["plot_path"]
    display_path = result.get("plot_path_display") or plot_path
    return display_path, plot_path


def show_results(results: List[Dict[str, Any]]) -> None:
    """Display fitting results: equation (formula + formatted) left, params center, stats right; plot; download below."""
    if not results:
        return

    st.markdown('---')
    st.header(t('dialog.results_title'))

    for idx, result in enumerate(results):
        with st.container():
            st.markdown(f"### {result['plot_name']} - {result['equation_name']}")

            formula_line, formatted_line = _split_equation(result["equation"])
            stats_lines, param_lines = _split_parameters_text(result["parameters"])

            eq_col, params_col, stats_col = st.columns([1, 1, 1])

            with eq_col:
                if formula_line:
                    st.markdown(f"**{t('dialog.equation_formula')}**")
                    st.text(formula_line)
                st.markdown(f"**{t('dialog.equation_formatted')}**")
                st.text(formatted_line)

            with params_col:
                if param_lines:
                    st.markdown(f"**{t('dialog.results_params_heading')}**")
                    for line in param_lines:
                        st.text(line)

            with stats_col:
                if stats_lines:
                    st.markdown(f"**{t('dialog.results_stats_heading')}**")
                    for line in stats_lines:
                        st.text(line)

            plot_path = Path(result["plot_path"])
            if plot_path.exists():
                display_path, download_path = _get_plot_display_path(result)
                plot_ext = plot_path.suffix.lower() or ".png"
                mime = _PLOT_MIME_BY_EXT.get(plot_ext, "image/png")
                download_name = f"{result['plot_name']}{plot_ext}"
                display_path_p = Path(display_path)

                if display_path_p.exists() and display_path_p.suffix.lower() in _IMAGE_EXTENSIONS:
                    st.image(display_path, width='stretch')
                elif plot_ext == ".pdf":
                    st.caption(t("dialog.plot_pdf_preview_caption"))

                st.markdown("")  # spacing
                with open(download_path, "rb") as f:
                    plot_bytes = f.read()
                st.download_button(
                    label=f"📥 {t('dialog.download')}",
                    data=plot_bytes,
                    file_name=download_name,
                    mime=mime,
                    key=f"download_{idx}",
                )
            else:
                st.text(result["parameters"])
