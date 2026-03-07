"""Compatibility tests for configured equation presets."""

from __future__ import annotations

from config import EQUATIONS
from fitting import get_fitting_function


def test_all_python_equations_resolve_to_callable() -> None:
    """Every python-type equation in config should still load after refactors."""
    unresolved: list[str] = []
    for equation_id, meta in EQUATIONS.items():
        if str(meta.get("type", "python")) != "python":
            continue
        if get_fitting_function(equation_id) is None:
            unresolved.append(equation_id)

    assert not unresolved, f"Could not resolve fitting callables for: {unresolved}"
