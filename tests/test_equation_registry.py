"""Tests for the equation registry loader and schema normalization."""

from __future__ import annotations

import shutil
from pathlib import Path
from textwrap import dedent
from uuid import uuid4

import pytest

from config.equation_registry import load_equation_registry


def _write_yaml(path: Path, content: str) -> None:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def _new_local_tmp_dir() -> Path:
    """Create a writable temp dir under tests/ for sandbox-safe runs."""
    root = Path(__file__).resolve().parent / "_tmp_runtime"
    root.mkdir(parents=True, exist_ok=True)
    tmp_dir = root / f"registry_{uuid4().hex}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def test_registry_merges_base_and_user_files() -> None:
    """User equations should extend/override base equations."""
    tmp_dir = _new_local_tmp_dir()
    try:
        base_path = tmp_dir / "equations.yaml"
        user_path = tmp_dir / "equations.user.yaml"

        _write_yaml(
            base_path,
            """
            linear_function:
              function: fit_linear_function
              formula: "y = mx"
              format: "y={m}x"
              param_names: [m]

            quadratic_function:
              type: python
              target: fitting.functions.polynomials.fit_quadratic_function
              formula: "y = ax^2"
              format: "y={a}x^2"
              param_names: [a]
            """,
        )
        _write_yaml(
            user_path,
            """
            linear_function:
              function: fit_linear_function
              formula: "y = m*x"
              format: "y={m}*x"
              param_names: [m]
              initial_guess: [2]
              bounds:
                - [0]
                - [10]

            user_expression:
              type: expression
              expression: "a*x + b"
              param_names: [a, b]
            """,
        )

        registry = load_equation_registry(base_path=base_path, user_path=user_path)

        assert set(registry.keys()) == {
            "linear_function",
            "quadratic_function",
            "user_expression",
        }

        linear = registry["linear_function"]
        assert linear["type"] == "python"
        assert linear["target"] == "fit_linear_function"
        assert linear["initial_guess"] == [2.0]
        assert linear["bounds"] == ([0.0], [10.0])

        user_expression = registry["user_expression"]
        assert user_expression["type"] == "expression"
        assert user_expression["expression"] == "a*x + b"
        assert user_expression["format"] == "y={a}*x + {b}"
        assert user_expression["formula"] == "y = a*x + b"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_registry_defaults_to_python_type_for_legacy_entries() -> None:
    """Old schema entries without 'type' should remain fully supported."""
    tmp_dir = _new_local_tmp_dir()
    try:
        base_path = tmp_dir / "equations.yaml"
        _write_yaml(
            base_path,
            """
            legacy_linear:
              function: fit_linear_function
              formula: "y = mx"
              format: "y={m}x"
              param_names: [m]
            """,
        )

        registry = load_equation_registry(
            base_path=base_path,
            user_path=tmp_dir / "missing.user.yaml",
        )

        entry = registry["legacy_linear"]
        assert entry["type"] == "python"
        assert entry["function"] == "fit_linear_function"
        assert entry["target"] == "fit_linear_function"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_registry_rejects_invalid_expression_bounds() -> None:
    """Invalid bounds schema should fail fast with a clear error."""
    tmp_dir = _new_local_tmp_dir()
    try:
        base_path = tmp_dir / "equations.yaml"
        _write_yaml(
            base_path,
            """
            bad_expression:
              type: expression
              expression: "a*x + b"
              param_names: [a, b]
              bounds:
                - [0]
                - [1, 1]
            """,
        )

        with pytest.raises(ValueError):
            load_equation_registry(base_path=base_path, user_path=tmp_dir / "missing.user.yaml")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
