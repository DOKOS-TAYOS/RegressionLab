"""Central equation registry loader with base + user extension support."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import Any, Optional

import yaml

EQUATION_TYPE_PYTHON = "python"
EQUATION_TYPE_EXPRESSION = "expression"
_VALID_EQUATION_TYPES = frozenset({EQUATION_TYPE_PYTHON, EQUATION_TYPE_EXPRESSION})


def _registry_paths(
    base_path: Optional[Path] = None,
    user_path: Optional[Path] = None,
) -> tuple[Path, Path]:
    """Return (base_yaml_path, user_yaml_path)."""
    config_dir = Path(__file__).resolve().parent
    base = base_path if base_path is not None else config_dir / "equations.yaml"
    user = user_path if user_path is not None else config_dir / "equations.user.yaml"
    return base, user


def _load_yaml_mapping(path: Path, *, required: bool) -> dict[str, Any]:
    """Load YAML mapping from disk."""
    if not path.exists():
        if required:
            raise FileNotFoundError(
                f"Equations configuration file not found: {path}\n"
                "Please ensure the file exists in the config directory."
            )
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Error parsing equations file: {e}\n"
            f"File path: {path}"
        ) from e
    except OSError as e:
        raise RuntimeError(
            f"Unexpected error reading equations file: {e}\n"
            f"File path: {path}"
        ) from e

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(
            f"Equations file must contain a dictionary.\n"
            f"Found type: {type(raw).__name__}\n"
            f"File path: {path}"
        )
    return raw


def _normalize_param_names(eq_id: str, value: Any) -> list[str]:
    """Validate and normalize param_names."""
    if not isinstance(value, list) or not value:
        raise ValueError(
            f"Equation '{eq_id}' must define non-empty 'param_names' as a list."
        )
    out: list[str] = []
    for idx, raw_name in enumerate(value):
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ValueError(
                f"Equation '{eq_id}' has invalid param_names[{idx}]={raw_name!r}."
            )
        out.append(raw_name.strip())
    return out


def _normalize_optional_float_list(value: Any, *, field_name: str, eq_id: str) -> Optional[list[float]]:
    """Normalize an optional list of floats."""
    if value is None:
        return None
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"Equation '{eq_id}' field '{field_name}' must be a list/tuple of numbers."
        )
    out: list[float] = []
    for idx, v in enumerate(value):
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            raise ValueError(
                f"Equation '{eq_id}' has invalid {field_name}[{idx}]={v!r}."
            ) from None
    return out


def _normalize_bounds(
    value: Any,
    *,
    eq_id: str,
    n_params: int,
) -> Optional[tuple[list[Optional[float]], list[Optional[float]]]]:
    """Normalize optional bounds as (lower, upper), allowing None values per slot."""
    if value is None:
        return None
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or not isinstance(value[0], (list, tuple))
        or not isinstance(value[1], (list, tuple))
    ):
        raise ValueError(
            f"Equation '{eq_id}' field 'bounds' must be [lower_list, upper_list]."
        )
    lower_raw, upper_raw = value
    if len(lower_raw) != n_params or len(upper_raw) != n_params:
        raise ValueError(
            f"Equation '{eq_id}' bounds length must match param_names length ({n_params})."
        )
    lower: list[Optional[float]] = []
    upper: list[Optional[float]] = []
    for idx, v in enumerate(lower_raw):
        if v is None:
            lower.append(None)
        else:
            try:
                lower.append(float(v))
            except (TypeError, ValueError):
                raise ValueError(
                    f"Equation '{eq_id}' has invalid bounds lower[{idx}]={v!r}."
                ) from None
    for idx, v in enumerate(upper_raw):
        if v is None:
            upper.append(None)
        else:
            try:
                upper.append(float(v))
            except (TypeError, ValueError):
                raise ValueError(
                    f"Equation '{eq_id}' has invalid bounds upper[{idx}]={v!r}."
                ) from None
    return (lower, upper)


def _template_from_expression(expression: str, param_names: list[str]) -> str:
    """
    Build equation template from expression by replacing bare param names with {param}.

    Example:
        expression='a*x + b' -> 'y={a}*x + {b}'
    """
    ordered = sorted(param_names, key=len, reverse=True)
    pattern = re.compile("|".join(r"\b" + re.escape(name) + r"\b" for name in ordered))
    replaced = pattern.sub(lambda m: "{" + m.group(0) + "}", expression)
    return f"y={replaced}"


def _normalize_equation_entry(eq_id: str, raw_entry: Any) -> dict[str, Any]:
    """Validate and normalize one equation entry."""
    if not isinstance(raw_entry, dict):
        raise ValueError(
            f"Equation '{eq_id}' must be a dictionary."
        )

    eq_type = str(raw_entry.get("type", EQUATION_TYPE_PYTHON)).strip().lower()
    if eq_type not in _VALID_EQUATION_TYPES:
        raise ValueError(
            f"Equation '{eq_id}' has unsupported type '{eq_type}'. "
            f"Valid types: {sorted(_VALID_EQUATION_TYPES)}"
        )

    param_names = _normalize_param_names(eq_id, raw_entry.get("param_names"))
    num_independent_vars = int(raw_entry.get("num_independent_vars", 1))
    if num_independent_vars < 1:
        raise ValueError(
            f"Equation '{eq_id}' must have num_independent_vars >= 1."
        )

    initial_guess = _normalize_optional_float_list(
        raw_entry.get("initial_guess"),
        field_name="initial_guess",
        eq_id=eq_id,
    )
    bounds = _normalize_bounds(
        raw_entry.get("bounds"),
        eq_id=eq_id,
        n_params=len(param_names),
    )

    formula = str(raw_entry.get("formula", "")).strip()
    fmt = raw_entry.get("format")

    if eq_type == EQUATION_TYPE_PYTHON:
        target = str(raw_entry.get("target") or raw_entry.get("function") or "").strip()
        if not target:
            raise ValueError(
                f"Equation '{eq_id}' of type '{EQUATION_TYPE_PYTHON}' must define "
                "'target' (or legacy 'function')."
            )
        legacy_function = str(raw_entry.get("function") or target).strip()
        normalized: dict[str, Any] = {
            "type": EQUATION_TYPE_PYTHON,
            "target": target,
            # Keep legacy key for backwards compatibility with external code.
            "function": legacy_function,
            "formula": formula,
            "param_names": param_names,
            "num_independent_vars": num_independent_vars,
        }
        if fmt is None:
            normalized["format"] = _template_from_expression(formula, param_names) if formula else "y=" + target
        elif isinstance(fmt, str) and fmt.strip():
            normalized["format"] = fmt.strip()
        else:
            raise ValueError(f"Equation '{eq_id}' has invalid 'format'.")
    else:
        expression = str(raw_entry.get("expression", "")).strip()
        if not expression:
            raise ValueError(
                f"Equation '{eq_id}' of type '{EQUATION_TYPE_EXPRESSION}' must define 'expression'."
            )
        normalized = {
            "type": EQUATION_TYPE_EXPRESSION,
            "expression": expression,
            "target": str(raw_entry.get("target", f"expression::{eq_id}")).strip(),
            "formula": formula if formula else f"y = {expression}",
            "param_names": param_names,
            "num_independent_vars": num_independent_vars,
        }
        if fmt is None:
            normalized["format"] = _template_from_expression(expression, param_names)
        elif isinstance(fmt, str) and fmt.strip():
            normalized["format"] = fmt.strip()
        else:
            raise ValueError(f"Equation '{eq_id}' has invalid 'format'.")

    if initial_guess is not None:
        if len(initial_guess) != len(param_names):
            raise ValueError(
                f"Equation '{eq_id}' initial_guess length must match param_names length ({len(param_names)})."
            )
        normalized["initial_guess"] = initial_guess
    if bounds is not None:
        normalized["bounds"] = bounds
    return normalized


def load_equation_registry(
    base_path: Optional[Path] = None,
    user_path: Optional[Path] = None,
) -> dict[str, dict[str, Any]]:
    """
    Load and merge equations from base + optional user YAML files.

    Base file is required; user file is optional and can override existing ids.
    """
    base_yaml, user_yaml = _registry_paths(base_path, user_path)
    base_raw = _load_yaml_mapping(base_yaml, required=True)
    user_raw = _load_yaml_mapping(user_yaml, required=False)

    merged: dict[str, dict[str, Any]] = {}
    for eq_id, raw in base_raw.items():
        merged[str(eq_id)] = _normalize_equation_entry(str(eq_id), raw)
    for eq_id, raw in user_raw.items():
        merged[str(eq_id)] = _normalize_equation_entry(str(eq_id), raw)
    if not merged:
        raise ValueError(
            f"No equation definitions were loaded from: {base_yaml}"
        )
    return merged


@lru_cache(maxsize=1)
def get_equation_registry() -> dict[str, dict[str, Any]]:
    """Return cached equation registry from default paths."""
    return load_equation_registry()


def clear_equation_registry_cache() -> None:
    """Clear cached registry (useful in tests)."""
    get_equation_registry.cache_clear()
