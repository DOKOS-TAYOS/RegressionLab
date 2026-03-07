"""
Fitting utilities for RegressionLab.

This module provides parameter formatting, equation resolution, and integration
with fitting functions (initial guesses, bounds, fit execution).
"""

# Standard library
import importlib
import inspect
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union

# Numerical library
import numpy as np

# Local imports (heavy numerical libraries are imported lazily inside functions)
from config import EQUATIONS, EXIT_SIGNAL, FORMAT_TO_FORMULA, FUNCTION_TO_EQUATION
from i18n import t
from utils import FittingError, get_logger

logger = get_logger(__name__)


# Unicode superscript digits and signs for literal elevated display
_SUPERS = str.maketrans(
    "0123456789+-",
    "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207a\u207b",
)


def _exp_to_superscript(exp_int: int) -> str:
    """Convert exponent integer to Unicode superscript."""
    return str(exp_int).translate(_SUPERS)


def _to_power10_format(s: str) -> str:
    """Convert scientific notation (E/e) to 10^exp with superscript exponent."""
    match = re.match(r"^([+-]?\d+\.?\d*)[eE]([+-]?\d+)$", s.strip())
    if match:
        mantissa, exp = match.groups()
        exp_int = int(exp)
        return f"{mantissa}\u00d710{_exp_to_superscript(exp_int)}"
    return s


def format_scientific(value: float, fmt: str = ".4g") -> str:
    """Format a number using superscript notation instead of E/e."""
    if not np.isfinite(value):
        return "\u221e" if np.isinf(value) else "NaN"
    return _to_power10_format(f"{value:{fmt}}")


def format_parameter(value: float, sigma: float) -> Tuple[float, str]:
    """Format parameter value and uncertainty with robust fallback behavior."""
    if not np.isfinite(sigma):
        return round(value, 6), "\u221e" if np.isinf(sigma) else "NaN"

    try:
        sigma_raw = "%.1E" % Decimal(sigma)
        if "E" in sigma_raw:
            exp_part = sigma_raw.split("E")[-1]
            if exp_part:
                exp_value = int(exp_part)
                rounded_value = round(value, 1 - exp_value)
            else:
                logger.debug(t("log.no_exponent_found", sigma_str=sigma_raw))
                rounded_value = round(value, 6)
        else:
            logger.debug(t("log.no_exponential_notation", sigma_str=sigma_raw))
            rounded_value = round(value, 6)
        sigma_str = _to_power10_format(sigma_raw)
        return rounded_value, sigma_str
    except (ValueError, IndexError, OverflowError) as e:
        logger.warning(t("log.error_formatting_parameter", error=str(e)))
        sigma_str = _to_power10_format(f"{sigma:.1E}")
        return round(value, 6), sigma_str


@dataclass(frozen=True)
class _PreparedFitData:
    """Validated data arrays ready for scipy curve_fit."""

    x_names: List[str]
    x: Any
    y: np.ndarray
    uy: np.ndarray


def _normalize_x_names(x_name: Union[str, List[str]]) -> List[str]:
    """Normalize x variable selection to a non-empty list."""
    if isinstance(x_name, list):
        names = [str(n) for n in x_name if str(n).strip()]
    else:
        names = [str(x_name)]
    if not names:
        raise FittingError("At least one independent variable must be provided.")
    return names


def _prepare_fit_arrays(
    data: Any,
    x_name: Union[str, List[str]],
    y_name: str,
) -> _PreparedFitData:
    """Validate fitting inputs and convert to float NumPy arrays."""
    from utils import validate_fitting_data

    x_names = _normalize_x_names(x_name)
    try:
        validate_fitting_data(data, x_names[0], y_name)
        for extra_x in x_names[1:]:
            if extra_x not in data.columns:
                raise FittingError(f"Independent variable '{extra_x}' not found in data")
    except Exception as e:
        logger.error(t("log.data_validation_failed", error=str(e)))
        raise FittingError(t("error.data_validation_failed", error=str(e)))

    if len(x_names) == 1:
        x_arr: Any = np.asarray(data[x_names[0]], dtype=float)
    else:
        x_arr = np.column_stack([np.asarray(data[x_n], dtype=float) for x_n in x_names])

    y_arr = np.asarray(data[y_name], dtype=float)
    uy_arr = np.asarray(data.get(f"u{y_name}", np.zeros_like(y_arr)), dtype=float)
    logger.debug(
        t(
            "log.data_points_info",
            points=len(y_arr),
            x_min=f"{np.asarray(x_arr).min():.3f}",
            x_max=f"{np.asarray(x_arr).max():.3f}",
            y_min=f"{y_arr.min():.3f}",
            y_max=f"{y_arr.max():.3f}",
        )
    )
    return _PreparedFitData(x_names=x_names, x=x_arr, y=y_arr, uy=uy_arr)


def _run_curve_fit(
    fit_func: Callable[..., Any],
    prepared: _PreparedFitData,
    initial_guess: Optional[List[float]],
    bounds: Optional[Tuple[Sequence[float], Sequence[float]]],
    n_params: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Execute scipy curve_fit with consistent error translation."""
    from scipy.optimize import curve_fit

    p0 = list(initial_guess) if initial_guess is not None else [1.0] * n_params
    if initial_guess is None:
        logger.debug(t("log.using_initial_guess", guess=str(p0)))

    fit_kwargs: dict[str, Any] = {
        "f": fit_func,
        "xdata": prepared.x,
        "ydata": prepared.y,
        "p0": p0,
        "sigma": prepared.uy,
        "absolute_sigma": True,
        "maxfev": 10000,
    }
    if bounds is not None:
        fit_kwargs["bounds"] = bounds
    try:
        logger.debug(t("log.attempting_curve_fitting"))
        params, cov = curve_fit(**fit_kwargs)
        logger.debug(t("log.curve_fitting_successful"))
        return np.asarray(params, dtype=float), np.asarray(cov, dtype=float)
    except RuntimeError as e:
        logger.error(t("log.curve_fitting_convergence_failed", error=str(e)))
        raise FittingError(t("error.fitting_convergence_failed", error=str(e)))
    except ValueError as e:
        logger.error(t("log.invalid_data_for_fitting", error=str(e)))
        raise FittingError(t("error.invalid_data_for_fitting", error=str(e)))
    except TypeError as e:
        logger.error(t("log.function_signature_error", error=str(e)))
        raise FittingError(t("error.fitting_function_error", error=str(e)))
    except Exception as e:
        logger.error(t("log.unexpected_fitting_error", error=str(e)), exc_info=True)
        raise FittingError(t("error.unexpected_fitting_error", error=str(e)))


def _format_parameter_output(
    param_names: List[str],
    params: Sequence[float],
    uncertainties: Sequence[float],
) -> tuple[dict[str, float], list[str]]:
    """Format parameters and return (formatted_param_map, parameter_lines)."""
    formatted_params: dict[str, float] = {}
    lines: list[str] = []
    for name, param, uncertainty in zip(param_names, params, uncertainties):
        formatted_param, formatted_uncertainty = format_parameter(param, uncertainty)
        formatted_params[name] = formatted_param
        lines.append(f"{name}={formatted_param}, \u03c3({name})={formatted_uncertainty}")
    return formatted_params, lines


def _compute_fit_statistics(
    y: np.ndarray,
    y_fitted: np.ndarray,
    uy: np.ndarray,
    params: Sequence[float],
    param_names: Sequence[str],
) -> dict[str, Any]:
    """Compute goodness-of-fit metrics."""

    n_points = len(y)
    n_params = len(params)
    dof = n_points - n_params
    fit_stats: dict[str, Any] = {}
    try:
        residuals_sq = (y - y_fitted) ** 2
        ss_res = float(np.sum(residuals_sq))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        fit_stats["r_squared"] = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        fit_stats["rmse"] = float(np.sqrt(np.mean(residuals_sq)))
    except Exception as e:
        logger.warning("Error calculating fit statistics: %s", str(e))
        fit_stats["r_squared"] = 0.0
        fit_stats["rmse"] = float("nan")

    uy_safe = np.where(np.greater(uy, 1e-15), uy, 1e-15)
    chi_sq = float(np.sum(((y - y_fitted) / uy_safe) ** 2))
    fit_stats["chi_squared"] = chi_sq
    fit_stats["reduced_chi_squared"] = chi_sq / dof if dof > 0 else float("nan")
    fit_stats["dof"] = dof

    # Confidence intervals are built in a separate helper once uncertainties are available.
    fit_stats["confidence_intervals"] = {}
    return fit_stats


def _build_confidence_intervals(
    fit_stats: dict[str, Any],
    params: Sequence[float],
    uncertainties: Sequence[float],
    param_names: Sequence[str],
) -> None:
    """Populate confidence intervals in fit_stats."""
    from scipy import stats as scipy_stats

    dof = int(fit_stats.get("dof", 0))
    t_crit = scipy_stats.t.ppf(0.975, dof) if dof > 0 else float("nan")
    confidence_intervals: dict[str, dict[str, Any]] = {}
    for name, param, uncertainty in zip(param_names, params, uncertainties):
        if dof > 0 and np.isfinite(uncertainty) and np.isfinite(t_crit):
            confidence_intervals[name] = {
                "low": float(param - t_crit * uncertainty),
                "high": float(param + t_crit * uncertainty),
                "available": True,
            }
        else:
            confidence_intervals[name] = {"low": None, "high": None, "available": False}
    fit_stats["confidence_intervals"] = confidence_intervals


def _append_statistics_lines(
    lines: list[str],
    fit_stats: dict[str, Any],
    param_names: Sequence[str],
) -> None:
    """Append human-readable statistics lines to result text."""
    lines.append(f"R\u00b2={fit_stats['r_squared']:.6f}")
    lines.append(t("stats.rmse", value=format_scientific(fit_stats["rmse"])))
    lines.append(t("stats.chi_squared", value=format_scientific(fit_stats["chi_squared"])))
    lines.append(
        t("stats.reduced_chi_squared", value=format_scientific(fit_stats["reduced_chi_squared"]))
    )
    lines.append(t("stats.dof", value=fit_stats["dof"]))

    ci_map = fit_stats.get("confidence_intervals", {})
    for name in param_names:
        ci = ci_map.get(name, {"available": False, "low": None, "high": None})
        if ci["available"]:
            lines.append(
                t(
                    "stats.param_ci_95",
                    param=name,
                    low=format_scientific(ci["low"]),
                    high=format_scientific(ci["high"]),
                )
            )
        else:
            lines.append(t("stats.param_ci_95_na", param=name))


def generic_fit(
    data: Any,
    x_name: Union[str, List[str]],
    y_name: str,
    fit_func: Callable[..., Any],
    param_names: List[str],
    equation_template: Optional[str],
    initial_guess: Optional[List[float]] = None,
    bounds: Optional[Tuple[Sequence[float], Sequence[float]]] = None,
    equation_formula: Optional[str] = None,
) -> Tuple[str, Any, str, Optional[dict]]:
    """Generic fitting function that performs curve fitting with any model."""
    x_names = _normalize_x_names(x_name)
    logger.info(t("log.starting_generic_fit", x=str(x_names), y=y_name, params=str(param_names)))

    if equation_template is None:
        raise FittingError("Equation format template is missing in config (equations.yaml 'format' key).")

    prepared = _prepare_fit_arrays(data=data, x_name=x_name, y_name=y_name)
    params_array, cov = _run_curve_fit(
        fit_func=fit_func,
        prepared=prepared,
        initial_guess=initial_guess,
        bounds=bounds,
        n_params=len(param_names),
    )
    params = list(params_array)

    try:
        uncertainties = list(np.sqrt(np.diag(cov)))
        logger.debug(t("log.extracted_parameters", params=str(dict(zip(param_names, params)))))
        if any(np.isinf(u) for u in uncertainties):
            logger.info(t("log.infinite_uncertainties"))
    except Exception as e:
        logger.error(t("log.error_extracting_parameters", error=str(e)), exc_info=True)
        raise FittingError(t("error.extracting_parameters", error=str(e)))

    formatted_params, text_lines = _format_parameter_output(param_names, params, uncertainties)

    try:
        y_fitted = np.asarray(fit_func(prepared.x, *params), dtype=float)
        logger.debug(t("log.fitted_curve_calculated", points=len(y_fitted)))
    except Exception as e:
        logger.error(t("log.error_calculating_fitted_curve", error=str(e)), exc_info=True)
        raise FittingError(t("error.calculating_fitted_curve", error=str(e)))

    fit_stats = _compute_fit_statistics(
        y=prepared.y,
        y_fitted=y_fitted,
        uy=prepared.uy,
        params=params,
        param_names=param_names,
    )
    _build_confidence_intervals(fit_stats, params, uncertainties, param_names)
    _append_statistics_lines(text_lines, fit_stats, param_names)
    text = "\n".join(text_lines)

    formatted_equation = equation_template.format(**formatted_params)
    # Fix "+-" when a negative param follows "+" (e.g. y=5.2*x+-3.5 -> y=5.2*x-3.5)
    formatted_equation = formatted_equation.replace("+-", "-")
    logger.info(t("log.fit_completed_successfully", equation=formatted_equation))
    if equation_formula is None:
        equation_formula = FORMAT_TO_FORMULA.get(equation_template) or None
    equation_str = f"{equation_formula}\n{formatted_equation}" if equation_formula else formatted_equation

    fit_info: Optional[dict] = {
        "fit_func": fit_func,
        "params": params,
        "cov": cov,
        "x_names": prepared.x_names,
    }
    return text, y_fitted, equation_str, fit_info


def get_equation_param_info(
    equation_name: str,
) -> Optional[Tuple[List[str], str]]:
    """Get parameter names and display formula for a given equation type."""
    meta = EQUATIONS.get(equation_name)
    if meta is None:
        return None
    return (list(meta["param_names"]), str(meta.get("formula", "")))


def get_equation_format_for_function(function_name: str) -> Optional[str]:
    """Return the format template for the given fit function name/path."""
    eq_id = FUNCTION_TO_EQUATION.get(function_name)
    if eq_id is None:
        return None
    return EQUATIONS[eq_id].get("format")


def get_equation_param_names_for_function(function_name: str) -> List[str]:
    """Return parameter names for the given fit function from equations config."""
    eq_id = FUNCTION_TO_EQUATION.get(function_name)
    if eq_id is None:
        raise FittingError(f"No equation config found for function {function_name!r}")
    names = EQUATIONS[eq_id].get("param_names")
    if not names:
        raise FittingError(
            f"Missing param_names in equations config for {function_name!r}"
        )
    return list(names)


def merge_initial_guess(
    computed: List[float],
    override: Optional[List[Optional[float]]],
) -> List[float]:
    """Merge computed initial guesses with user overrides."""
    if override is None or len(override) != len(computed):
        return list(computed)
    return [float(ov) if ov is not None else comp for comp, ov in zip(computed, override)]


def merge_bounds(
    computed_bounds: Optional[Tuple[Sequence[float], Sequence[float]]],
    override_lower: Optional[List[Optional[float]]],
    override_upper: Optional[List[Optional[float]]],
    n_params: int,
) -> Optional[Tuple[Tuple[float, ...], Tuple[float, ...]]]:
    """Merge computed parameter bounds with user overrides."""
    if override_lower is None and override_upper is None:
        return (
            (tuple(float(x) for x in computed_bounds[0]), tuple(float(x) for x in computed_bounds[1]))
            if computed_bounds is not None
            else None
        )

    inf = float("-inf")
    pos_inf = float("inf")
    if computed_bounds is not None:
        base_lower = list(computed_bounds[0])
        base_upper = list(computed_bounds[1])
    else:
        base_lower = [inf] * n_params
        base_upper = [pos_inf] * n_params

    if override_lower is not None:
        for i, v in enumerate(override_lower):
            if i < n_params and v is not None:
                base_lower[i] = float(v)
    if override_upper is not None:
        for i, v in enumerate(override_upper):
            if i < n_params and v is not None:
                base_upper[i] = float(v)
    return (tuple(float(v) for v in base_lower), tuple(float(v) for v in base_upper))


def _merge_override_list(
    defaults: Optional[List[float]],
    override: Optional[List[Optional[float]]],
) -> Optional[List[Optional[float]]]:
    """Merge YAML defaults with user override list (None in user keeps default)."""
    if defaults is None and override is None:
        return None
    if defaults is None:
        return list(override) if override is not None else None
    if override is None:
        return [float(v) for v in defaults]
    if len(defaults) != len(override):
        return list(override)
    out: List[Optional[float]] = []
    for default_v, user_v in zip(defaults, override):
        out.append(float(default_v) if user_v is None else float(user_v))
    return out


def _merge_override_bounds(
    defaults: Optional[Tuple[List[Optional[float]], List[Optional[float]]]],
    override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]],
) -> Optional[Tuple[List[Optional[float]], List[Optional[float]]]]:
    """Merge YAML bounds defaults with user bounds override."""
    if defaults is None and override is None:
        return None
    if defaults is None:
        return override
    if override is None:
        return (list(defaults[0]), list(defaults[1]))

    low_def, up_def = defaults
    low_usr, up_usr = override
    if len(low_def) != len(low_usr) or len(up_def) != len(up_usr):
        return override

    low_out: List[Optional[float]] = []
    up_out: List[Optional[float]] = []
    for d, u in zip(low_def, low_usr):
        low_out.append(d if u is None else u)
    for d, u in zip(up_def, up_usr):
        up_out.append(d if u is None else u)
    return (low_out, up_out)


def _resolve_python_fit_callable(target: str) -> Callable[..., Any]:
    """Resolve python fit callable from legacy short names or module paths."""
    if ":" in target:
        module_name, attr_name = target.rsplit(":", 1)
        module = importlib.import_module(module_name)
        return getattr(module, attr_name)

    # Support dotted module path target (e.g. fitting.functions.special.fit_x)
    if "." in target and not target.startswith("fit_"):
        module_name, attr_name = target.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, attr_name)

    # Backward compatibility with exported symbols in fitting.fitting_functions
    from fitting import fitting_functions

    return getattr(fitting_functions, target)


def _build_expression_fit_callable(equation_meta: dict[str, Any]) -> Callable[..., Any]:
    """Build a fit callable from an expression-based equation entry."""
    from fitting.custom_function_evaluator import CustomFunctionEvaluator

    expression = str(equation_meta["expression"])
    param_names = list(equation_meta["param_names"])
    num_indep = int(equation_meta.get("num_independent_vars", 1))
    evaluator = CustomFunctionEvaluator(
        equation_str=expression,
        parameter_names=param_names,
        num_independent_vars=num_indep,
    )

    def _fit(
        data: Any,
        x_name: Union[str, List[str]],
        y_name: str,
        initial_guess_override: Optional[List[Optional[float]]] = None,
        bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
    ) -> Tuple[str, Any, str, Optional[dict]]:
        return evaluator.fit(
            data,
            x_name,
            y_name,
            initial_guess_override=initial_guess_override,
            bounds_override=bounds_override,
        )

    _fit.num_independent_vars = num_indep  # type: ignore[attr-defined]
    return _fit


def get_fitting_function(
    equation_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Optional[Callable]:
    """Get fitting function for equation id (supports python and expression types)."""
    logger.debug(t("log.getting_fitting_function", equation=equation_name))

    if equation_name == EXIT_SIGNAL:
        logger.debug(t("log.exit_signal_received"))
        return None

    equation_meta = EQUATIONS.get(equation_name)
    if equation_meta is None:
        logger.warning(t("log.unknown_equation_type", equation=equation_name))
        return None

    eq_type = str(equation_meta.get("type", "python")).lower()
    try:
        if eq_type == "expression":
            base_fit = _build_expression_fit_callable(equation_meta)
            function_name = str(equation_meta.get("target", f"expression::{equation_name}"))
        else:
            function_name = str(equation_meta.get("target") or equation_meta.get("function"))
            base_fit = _resolve_python_fit_callable(function_name)
    except (ImportError, AttributeError, KeyError, ValueError) as e:
        logger.error(
            t("log.error_importing_fitting_function", function=str(equation_meta.get("target", "<unknown>")), error=str(e)),
            exc_info=True,
        )
        return None

    logger.info(t("log.successfully_loaded_fitting_function", function=function_name))

    default_guess = equation_meta.get("initial_guess")
    defaults_guess_list = [float(v) for v in default_guess] if isinstance(default_guess, list) else None
    merged_initial_guess = _merge_override_list(defaults_guess_list, initial_guess_override)

    default_bounds = equation_meta.get("bounds")
    defaults_bounds_tuple: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None
    if (
        isinstance(default_bounds, (tuple, list))
        and len(default_bounds) == 2
        and isinstance(default_bounds[0], list)
        and isinstance(default_bounds[1], list)
    ):
        defaults_bounds_tuple = (list(default_bounds[0]), list(default_bounds[1]))
    merged_bounds = _merge_override_bounds(defaults_bounds_tuple, bounds_override)

    signature = inspect.signature(base_fit)
    accepts_initial = "initial_guess_override" in signature.parameters
    accepts_bounds = "bounds_override" in signature.parameters

    def fit_with_overrides(data: Any, x_name: Any, y_name: str) -> Tuple[str, Any, str, Optional[dict]]:
        kwargs: dict[str, Any] = {}
        if accepts_initial:
            kwargs["initial_guess_override"] = merged_initial_guess
        if accepts_bounds:
            kwargs["bounds_override"] = merged_bounds
        return base_fit(data, x_name, y_name, **kwargs)

    fit_with_overrides.num_independent_vars = int(equation_meta.get("num_independent_vars", getattr(base_fit, "num_independent_vars", 1)))  # type: ignore[attr-defined]
    return fit_with_overrides
