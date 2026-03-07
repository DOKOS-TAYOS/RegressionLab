"""Integration-style tests for equation extensibility and UI fallbacks."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from fitting import fitting_utils
from frontend.ui_dialogs import equation as equation_dialog
from streamlit_app.sections import fitting as streamlit_fitting


def _sample_linear_data(m: float = 2.0, n: float = 1.0) -> pd.DataFrame:
    """Create deterministic linear data with uncertainties."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    return pd.DataFrame(
        {
            "x": x,
            "ux": np.full_like(x, 0.1),
            "y": m * x + n,
            "uy": np.full_like(x, 0.2),
        }
    )


def test_expression_equation_from_registry_entry_can_fit(monkeypatch: Any) -> None:
    """Expression-type equation entries should run through the standard fit pipeline."""
    monkeypatch.setattr(
        fitting_utils,
        "EQUATIONS",
        {
            "expr_linear": {
                "type": "expression",
                "expression": "a*x + b",
                "formula": "y = ax + b",
                "format": "y={a}x+{b}",
                "param_names": ["a", "b"],
                "num_independent_vars": 1,
                "initial_guess": [1.0, 0.0],
            }
        },
    )
    monkeypatch.setattr(fitting_utils, "FUNCTION_TO_EQUATION", {})

    fit_fn = fitting_utils.get_fitting_function("expr_linear")
    assert fit_fn is not None

    text, _, equation, fit_info = fit_fn(_sample_linear_data(m=3.0, n=2.0), "x", "y")
    assert "a=" in text
    assert "b=" in text
    assert "a*x + b" in equation
    assert fit_info is not None


def test_python_equation_supports_module_path_target(monkeypatch: Any) -> None:
    """Python entries should resolve fully qualified callable targets."""
    monkeypatch.setattr(
        fitting_utils,
        "EQUATIONS",
        {
            "linear_python_path": {
                "type": "python",
                "target": "fitting.functions.polynomials.fit_linear_function",
                "function": "fit_linear_function",
                "formula": "y = mx",
                "format": "y={m}x",
                "param_names": ["m"],
            }
        },
    )
    monkeypatch.setattr(
        fitting_utils,
        "FUNCTION_TO_EQUATION",
        {
            "fitting.functions.polynomials.fit_linear_function": "linear_python_path",
            "fit_linear_function": "linear_python_path",
        },
    )

    fit_fn = fitting_utils.get_fitting_function(
        "linear_python_path",
        initial_guess_override=[2.0],
    )
    assert fit_fn is not None
    assert getattr(fit_fn, "num_independent_vars", 1) == 1

    text, _, _, _ = fit_fn(_sample_linear_data(m=2.0, n=0.0), "x", "y")
    assert "m=" in text


def test_tk_equation_label_fallback_when_translation_is_missing(monkeypatch: Any) -> None:
    """Tk dialog should derive a readable label from equation id when i18n key is missing."""
    monkeypatch.setattr(equation_dialog, "t", lambda key, **kwargs: key)
    assert equation_dialog._equation_label("my_new_equation") == "My New Equation"
    assert equation_dialog._equation_description("my_new_equation") == ""


def test_streamlit_equation_label_fallback_when_translation_is_missing(monkeypatch: Any) -> None:
    """Streamlit selector should use id-based fallback labels when i18n key is missing."""
    monkeypatch.setattr(streamlit_fitting, "t", lambda key, **kwargs: key)
    options = streamlit_fitting._create_equation_options(["my_new_equation"])
    assert options["My New Equation"] == "my_new_equation"
