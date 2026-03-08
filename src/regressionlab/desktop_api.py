"""FastAPI sidecar for the Electron desktop frontend."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import UTC, datetime
import math
import os
from pathlib import Path
from typing import Any, Literal, Optional
from uuid import uuid4

import numpy as np
import pandas as pd

from config import (
    AVAILABLE_EQUATION_TYPES,
    DONATIONS_URL,
    ENV_SCHEMA,
    EQUATIONS,
    SUPPORTED_LANGUAGE_CODES,
    UI_STYLE,
    __version__,
    get_current_env_values,
    get_project_root,
    initialize_and_validate_config,
    write_env_file,
)
from data_analysis import CLEAN_OPTIONS, TRANSFORM_OPTIONS, apply_cleaning, apply_transform
from fitting import CustomFunctionEvaluator, format_parameter, format_scientific, get_fitting_function
from fitting.fitting_utils import _build_confidence_intervals, _compute_fit_statistics
from i18n import initialize_i18n
from loaders import get_variable_names, load_data, save_dataframe
from plotting import create_3d_plot, create_plot, create_residual_plot
from utils import (
    EquationError,
    FittingError,
    RegressionLabError,
    ValidationError,
    get_logger,
    setup_logging,
)
from utils.update_checker import is_update_available, perform_git_pull

try:
    from fastapi import FastAPI
    from fastapi.exceptions import RequestValidationError
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, model_validator
    import uvicorn
except ImportError as exc:  # pragma: no cover - guarded by runtime dependency
    raise RuntimeError(
        "FastAPI desktop sidecar dependencies are missing. "
        "Install fastapi and uvicorn to use regressionlab.desktop_api."
    ) from exc


initialize_and_validate_config()
initialize_i18n()
setup_logging()
logger = get_logger(__name__)


HELP_SECTIONS: list[dict[str, Any]] = [
    {
        "id": "objective",
        "headerKey": "help.objective_title",
        "contentKeys": ["help.objective_description"],
    },
    {
        "id": "advantages",
        "headerKey": "help.advantages_title",
        "contentKeys": [f"help.advantage_{i}" for i in range(1, 10)],
    },
    {
        "id": "fitting_modes",
        "headerKey": "help.fitting_modes",
        "contentKeys": [
            "help.normal_fitting",
            "help.multiple_datasets",
            "help.checker_fitting",
            "help.total_fitting",
            "help.view_data",
            "help.loop_mode",
        ],
    },
    {
        "id": "view_data_options",
        "headerKey": "help.view_data_options_title",
        "contentKeys": [
            "help.view_data_pair_plots",
            "help.view_data_transform",
            "help.view_data_clean",
            "help.view_data_save",
        ],
    },
    {
        "id": "custom_functions",
        "headerKey": "help.custom_functions_title",
        "contentKeys": ["help.custom_functions_how"],
    },
    {
        "id": "data_format",
        "headerKey": "help.data_format_title",
        "contentKeys": [
            "help.data_format_named",
            "help.data_format_u_prefix",
            "help.data_format_non_negative",
        ],
    },
    {
        "id": "data_location",
        "headerKey": "help.data_location",
        "contentKeys": ["help.data_input", "help.data_formats"],
    },
    {
        "id": "output_location",
        "headerKey": "help.output_location",
        "contentKeys": ["help.output_plots", "help.output_logs"],
    },
    {
        "id": "updates",
        "headerKey": "help.updates_title",
        "contentKeys": ["help.updates_description", "help.updates_configure"],
    },
    {
        "id": "stats",
        "headerKey": "help.stats_title",
        "contentKeys": [
            "help.r_squared_desc",
            "help.r_squared_formula",
            "help.rmse_desc",
            "help.rmse_formula",
            "help.chi_squared_desc",
            "help.chi_squared_formula",
            "help.reduced_chi_squared_desc",
            "help.reduced_chi_squared_formula",
            "help.dof_desc",
            "help.dof_formula",
            "help.param_ci_95_desc",
            "help.param_ci_95_formula",
        ],
    },
]

DATA_VIEW_HELP_SECTIONS: list[dict[str, Any]] = [
    {
        "id": "pair_plots",
        "headerKey": "help.view_data_pair_plots_header",
        "contentKeys": ["help.view_data_pair_plots_body"],
    },
    {
        "id": "transforms",
        "headerKey": "help.view_data_transform_header",
        "contentKeys": [
            "help.view_data_transform_fft",
            "help.view_data_transform_fft_magnitude",
            "help.view_data_transform_ifft",
            "help.view_data_transform_dct",
            "help.view_data_transform_idct",
            "help.view_data_transform_log",
            "help.view_data_transform_log10",
            "help.view_data_transform_exp",
            "help.view_data_transform_sqrt",
            "help.view_data_transform_square",
            "help.view_data_transform_standardize",
            "help.view_data_transform_normalize",
            "help.view_data_transform_hilbert",
            "help.view_data_transform_ihilbert",
            "help.view_data_transform_envelope",
            "help.view_data_transform_laplace",
            "help.view_data_transform_ilaplace",
            "help.view_data_transform_cepstrum",
            "help.view_data_transform_hadamard",
            "help.view_data_transform_ihadamard",
        ],
    },
    {
        "id": "cleaning",
        "headerKey": "help.view_data_clean_header",
        "contentKeys": [
            "help.view_data_clean_drop_na",
            "help.view_data_clean_drop_duplicates",
            "help.view_data_clean_fill_na_mean",
            "help.view_data_clean_fill_na_median",
            "help.view_data_clean_fill_na_zero",
            "help.view_data_clean_remove_outliers_iqr",
            "help.view_data_clean_remove_outliers_zscore",
        ],
    },
    {
        "id": "save",
        "headerKey": "help.view_data_save_header",
        "contentKeys": ["help.view_data_save_body"],
    },
]


class DesktopApiError(Exception):
    """Structured API error surfaced to the renderer."""

    def __init__(
        self,
        *,
        code: str,
        message_key: str,
        status_code: int = 400,
        message_params: Optional[dict[str, Any]] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message_key)
        self.code = code
        self.message_key = message_key
        self.status_code = status_code
        self.message_params = message_params or {}
        self.details = details


class BoundsOverrideModel(BaseModel):
    """Optional parameter bounds override."""

    lower: Optional[list[Optional[float]]] = None
    upper: Optional[list[Optional[float]]] = None


class CustomEquationModel(BaseModel):
    """Expression-based equation definition."""

    formula: str
    parameter_names: list[str] = Field(default_factory=list)
    num_independent_vars: int = 1


class DatasetLoadRequest(BaseModel):
    """Dataset load request."""

    file_path: str
    file_type: Optional[str] = None
    include_records: bool = True
    preview_rows: int = 200


class DatasetTransformRequest(BaseModel):
    """Dataset transform request."""

    transform_id: str
    columns: Optional[list[str]] = None
    in_place: bool = True
    include_records: bool = True
    preview_rows: int = 200


class DatasetCleanRequest(BaseModel):
    """Dataset cleaning request."""

    clean_id: str
    columns: Optional[list[str]] = None
    include_records: bool = True
    preview_rows: int = 200


class DatasetSaveRequest(BaseModel):
    """Dataset save request."""

    file_path: str
    file_type: Optional[str] = None


class PairPlotRequest(BaseModel):
    """Pair plot request for the data view."""

    variables: Optional[list[str]] = None
    max_variables: int = 10


class FitRunRequest(BaseModel):
    """Run a single fit against one dataset."""

    dataset_id: str
    mode: Literal["normal", "multiple", "checker", "total"] = "normal"
    x_names: list[str]
    y_name: str
    plot_name: Optional[str] = None
    equation_id: Optional[str] = None
    custom_equation: Optional[CustomEquationModel] = None
    initial_guess_override: Optional[list[Optional[float]]] = None
    bounds_override: Optional[BoundsOverrideModel] = None
    export_plot: bool = True

    @model_validator(mode="after")
    def _validate_equation_choice(self) -> "FitRunRequest":
        if not self.equation_id and not self.custom_equation:
            raise ValueError("Either equation_id or custom_equation must be provided.")
        return self


class RunAllFitsRequest(BaseModel):
    """Run many equations against one dataset."""

    dataset_id: str
    mode: Literal["checker", "total"] = "checker"
    x_names: list[str]
    y_name: str
    plot_name_base: Optional[str] = None
    equation_ids: Optional[list[str]] = None
    export_plot: bool = True
    stop_on_error: bool = False


class PredictionRequest(BaseModel):
    """Prediction request based on a previously computed fit."""

    fit_id: str
    x_values: list[float]


class ConfigUpdateRequest(BaseModel):
    """Configuration update payload."""

    values: dict[str, str]


@dataclass
class DatasetSession:
    """Stored dataset in the sidecar session."""

    dataset_id: str
    dataframe: pd.DataFrame
    file_path: str
    file_type: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class FitSession:
    """Stored fit metadata for prediction and history."""

    fit_id: str
    dataset_id: str
    equation_id: str
    x_names: list[str]
    y_name: str
    fit_info: dict[str, Any]
    plot_name: str
    plot_path: Optional[str]
    equation_string: str
    result_text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


DATASET_STORE: dict[str, DatasetSession] = {}
FIT_STORE: dict[str, FitSession] = {}


def _error_payload(exc: DesktopApiError) -> dict[str, Any]:
    """Serialize structured API error."""

    return {
        "ok": False,
        "error": {
            "code": exc.code,
            "messageKey": exc.message_key,
            "messageParams": exc.message_params,
            "details": exc.details,
        },
    }


def _sanitize_scalar(value: Any) -> Any:
    """Convert numpy and pandas scalars to JSON-safe values."""

    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if pd.isna(value):
        return None
    return value


def _sanitize_sequence(values: Any) -> list[Any]:
    """Sanitize any array-like to a JSON-safe list."""

    return [_sanitize_scalar(value) for value in np.asarray(values, dtype=object).tolist()]


def _infer_file_type(file_path: str) -> str:
    """Infer dataset file type from a path."""

    ext = Path(file_path).suffix.lower().lstrip(".")
    if ext not in {"csv", "txt", "xlsx"}:
        raise DesktopApiError(
            code="unsupported_file_type",
            message_key="error.unsupported_file_type",
            status_code=400,
            message_params={"file_type": ext or "unknown"},
        )
    return ext


def _ensure_dataset(dataset_id: str) -> DatasetSession:
    """Get a stored dataset or raise a 404."""

    dataset = DATASET_STORE.get(dataset_id)
    if dataset is None:
        raise DesktopApiError(
            code="dataset_not_found",
            message_key="error.data_is_null",
            status_code=404,
            details={"datasetId": dataset_id},
        )
    return dataset


def _ensure_fit(fit_id: str) -> FitSession:
    """Get a stored fit or raise a 404."""

    fit_session = FIT_STORE.get(fit_id)
    if fit_session is None:
        raise DesktopApiError(
            code="fit_not_found",
            message_key="error.fitting_failed",
            status_code=404,
            details={"fitId": fit_id},
        )
    return fit_session


def _dataset_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Serialize a DataFrame into JSON-safe row records."""

    records: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        records.append({key: _sanitize_scalar(value) for key, value in row.items()})
    return records


def _column_metadata(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Build column metadata consumed by the renderer."""

    numeric_columns = set(df.select_dtypes(include="number").columns)
    all_columns = set(df.columns)
    metadata: list[dict[str, Any]] = []
    for column in df.columns:
        is_uncertainty = len(column) > 1 and column.startswith("u") and column[1:] in all_columns
        metadata.append(
            {
                "name": column,
                "dtype": str(df[column].dtype),
                "isNumeric": column in numeric_columns,
                "isUncertainty": is_uncertainty,
                "baseColumn": column[1:] if is_uncertainty else None,
            }
        )
    return metadata


def _dataset_payload(
    session: DatasetSession,
    *,
    include_records: bool = True,
    preview_rows: int = 200,
) -> dict[str, Any]:
    """Serialize dataset session to frontend DTO."""

    df = session.dataframe
    records = _dataset_records(df) if include_records else None
    preview = _dataset_records(df.head(preview_rows))
    variable_names = get_variable_names(df)
    base_variables = get_variable_names(df, filter_uncertainty=True)
    uncertainty_pairs = {
        column[1:]: column
        for column in df.columns
        if len(column) > 1 and column.startswith("u") and column[1:] in df.columns
    }
    return {
        "id": session.dataset_id,
        "filePath": session.file_path,
        "fileType": session.file_type,
        "rowCount": int(len(df)),
        "columns": _column_metadata(df),
        "variableNames": variable_names,
        "baseVariables": base_variables,
        "uncertaintyPairs": uncertainty_pairs,
        "previewRows": preview_rows,
        "preview": preview,
        "records": records,
        "pairPlotVariables": base_variables,
        "updatedAt": session.updated_at.isoformat(),
    }


def _pair_plot_payload(session: DatasetSession, variables: Optional[list[str]], max_variables: int) -> dict[str, Any]:
    """Build a Plotly-friendly scatter-matrix payload."""

    df = session.dataframe
    available = get_variable_names(df, filter_uncertainty=True)
    selected = list(variables or available)
    if not selected:
        raise DesktopApiError(
            code="no_pair_plot_variables",
            message_key="dialog.pair_plots_select_variables",
            status_code=400,
        )
    selected = selected[:max_variables]
    numeric_df = df[selected].select_dtypes(include="number")
    if numeric_df.empty:
        raise DesktopApiError(
            code="no_numeric_data",
            message_key="error.column_must_be_numeric",
            status_code=400,
            details={"variables": selected},
        )
    dimensions = [
        {"label": column, "values": _sanitize_sequence(numeric_df[column].to_numpy())}
        for column in numeric_df.columns
    ]
    return {"kind": "splom", "dimensions": dimensions, "variables": list(numeric_df.columns)}


def _result_param_payload(
    param_names: list[str],
    params: list[float],
    cov: np.ndarray,
    fit_stats: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build parameter DTOs with formatting and confidence intervals."""

    uncertainties = list(np.sqrt(np.diag(cov)))
    confidence_intervals = fit_stats.get("confidence_intervals", {})
    result: list[dict[str, Any]] = []
    for name, value, uncertainty in zip(param_names, params, uncertainties):
        rounded_value, formatted_uncertainty = format_parameter(float(value), float(uncertainty))
        ci = confidence_intervals.get(name, {"available": False, "low": None, "high": None})
        result.append(
            {
                "name": name,
                "value": float(value),
                "uncertainty": None if not np.isfinite(uncertainty) else float(uncertainty),
                "displayValue": rounded_value,
                "displayUncertainty": formatted_uncertainty,
                "confidenceInterval": {
                    "available": bool(ci.get("available", False)),
                    "low": _sanitize_scalar(ci.get("low")),
                    "high": _sanitize_scalar(ci.get("high")),
                    "displayLow": format_scientific(ci["low"]) if ci.get("available") else None,
                    "displayHigh": format_scientific(ci["high"]) if ci.get("available") else None,
                },
            }
        )
    return result


def _fit_stats_payload(fit_stats: dict[str, Any]) -> dict[str, Any]:
    """Serialize fit statistics with raw and formatted values."""

    payload: dict[str, Any] = {}
    for key in ("r_squared", "rmse", "chi_squared", "reduced_chi_squared"):
        value = float(fit_stats[key])
        payload[key] = {"value": value, "display": format_scientific(value)}
    payload["dof"] = {"value": int(fit_stats["dof"]), "display": str(fit_stats["dof"])}
    return payload


def _split_equation_string(equation_string: str) -> tuple[str, str]:
    """Split equation string into formula and formatted display."""

    if "\n" not in equation_string:
        return equation_string, equation_string
    formula, display = equation_string.split("\n", 1)
    return formula, display


def _curve_plot_payload(
    data: pd.DataFrame,
    x_name: str,
    y_name: str,
    y_fitted: np.ndarray,
    fit_info: dict[str, Any],
) -> dict[str, Any]:
    """Build 2D curve DTO for Plotly."""

    x = np.asarray(data[x_name], dtype=float)
    y = np.asarray(data[y_name], dtype=float)
    ux = np.asarray(data.get(f"u{x_name}", np.zeros_like(x)), dtype=float)
    uy = np.asarray(data.get(f"u{y_name}", np.zeros_like(y)), dtype=float)

    x_plot = x
    y_plot = np.asarray(y_fitted, dtype=float)
    fit_func = fit_info.get("fit_func")
    params = fit_info.get("params")
    if fit_func is not None and params is not None and len(x) > 1:
        try:
            x_plot = np.linspace(float(x.min()), float(x.max()), 300)
            y_plot = np.asarray(fit_func(x_plot, *params), dtype=float)
        except Exception:
            x_plot = x
            y_plot = np.asarray(y_fitted, dtype=float)

    return {
        "kind": "curve2d",
        "xLabel": x_name,
        "yLabel": y_name,
        "traces": [
            {
                "name": "data",
                "mode": "markers",
                "x": _sanitize_sequence(x),
                "y": _sanitize_sequence(y),
                "errorX": _sanitize_sequence(ux),
                "errorY": _sanitize_sequence(uy),
            },
            {
                "name": "fit",
                "mode": "lines",
                "x": _sanitize_sequence(x_plot),
                "y": _sanitize_sequence(y_plot),
            },
        ],
    }


def _surface_plot_payload(
    data: pd.DataFrame,
    x_names: list[str],
    y_name: str,
    y_fitted: np.ndarray,
    fit_info: dict[str, Any],
) -> dict[str, Any]:
    """Build 3D surface DTO for Plotly."""

    grid_size = 50
    x = np.asarray(data[x_names[0]], dtype=float)
    y = np.asarray(data[x_names[1]], dtype=float)
    z = np.asarray(data[y_name], dtype=float)
    x_axis = np.linspace(float(x.min()), float(x.max()), grid_size)
    y_axis = np.linspace(float(y.min()), float(y.max()), grid_size)
    mesh_x, mesh_y = np.meshgrid(x_axis, y_axis)

    surface_z: Optional[np.ndarray] = None
    fit_func = fit_info.get("fit_func")
    params = fit_info.get("params")
    if fit_func is not None and params is not None:
        try:
            grid_points = np.column_stack([mesh_x.ravel(), mesh_y.ravel()])
            surface_z = np.asarray(fit_func(grid_points, *params), dtype=float).reshape(mesh_x.shape)
        except Exception:
            surface_z = None

    return {
        "kind": "surface3d",
        "xLabel": x_names[0],
        "yLabel": x_names[1],
        "zLabel": y_name,
        "scatter": {
            "x": _sanitize_sequence(x),
            "y": _sanitize_sequence(y),
            "z": _sanitize_sequence(z),
        },
        "surface": {
            "x": _sanitize_sequence(x_axis),
            "y": _sanitize_sequence(y_axis),
            "z": [_sanitize_sequence(row) for row in surface_z.tolist()] if surface_z is not None else None,
        },
        "fittedPoints": {
            "x": _sanitize_sequence(x),
            "y": _sanitize_sequence(y),
            "z": _sanitize_sequence(y_fitted),
        },
    }


def _residual_plot_payload(y: np.ndarray, y_fitted: np.ndarray) -> dict[str, Any]:
    """Build residual plot DTO for multi-dimensional fits."""

    residuals = np.asarray(y, dtype=float) - np.asarray(y_fitted, dtype=float)
    indices = np.arange(len(residuals))
    return {
        "kind": "residuals",
        "xLabel": "Point Index",
        "yLabel": "Residuals (y - y_fitted)",
        "traces": [
            {
                "name": "residuals",
                "mode": "markers",
                "x": _sanitize_sequence(indices),
                "y": _sanitize_sequence(residuals),
            },
            {
                "name": "baseline",
                "mode": "lines",
                "x": _sanitize_sequence([int(indices.min()) if len(indices) else 0, int(indices.max()) if len(indices) else 1]),
                "y": [0.0, 0.0],
            },
        ],
    }


def _create_plot_export(
    *,
    data: pd.DataFrame,
    x_names: list[str],
    y_name: str,
    y_fitted: np.ndarray,
    plot_name: str,
    fit_info: dict[str, Any],
) -> str:
    """Reuse the existing plotting backend for exported artifacts."""

    if len(x_names) == 1:
        x = data[x_names[0]]
        ux = data.get(f"u{x_names[0]}", [0.0] * len(x))
        y = data[y_name]
        uy = data.get(f"u{y_name}", [0.0] * len(y))
        return create_plot(x, y, ux, uy, y_fitted, plot_name, x_names[0], y_name, fit_info=fit_info)
    if len(x_names) == 2:
        output = create_3d_plot(
            data[x_names[0]],
            data[x_names[1]],
            data[y_name],
            y_fitted,
            plot_name,
            x_names[0],
            x_names[1],
            y_name,
            fit_info=fit_info,
        )
        if isinstance(output, tuple):
            return str(output[0])
        return str(output)
    residuals = np.asarray(data[y_name], dtype=float) - np.asarray(y_fitted, dtype=float)
    return create_residual_plot(residuals, list(range(len(residuals))), plot_name)


def _fit_payload(
    *,
    dataset: DatasetSession,
    equation_id: str,
    plot_name: str,
    x_names: list[str],
    y_name: str,
    text: str,
    y_fitted: np.ndarray,
    equation_string: str,
    fit_info: dict[str, Any],
    plot_path: Optional[str],
    param_names: list[str],
) -> dict[str, Any]:
    """Build a structured fit response."""

    params = [float(value) for value in fit_info["params"]]
    cov = np.asarray(fit_info["cov"], dtype=float)
    y_values = np.asarray(dataset.dataframe[y_name], dtype=float)
    uy = np.asarray(dataset.dataframe.get(f"u{y_name}", np.zeros_like(y_values)), dtype=float)
    fit_stats = _compute_fit_statistics(y_values, np.asarray(y_fitted, dtype=float), uy, params, param_names)
    _build_confidence_intervals(fit_stats, params, list(np.sqrt(np.diag(cov))), param_names)
    formula, formatted_equation = _split_equation_string(equation_string)

    if len(x_names) == 1:
        plot = _curve_plot_payload(dataset.dataframe, x_names[0], y_name, np.asarray(y_fitted), fit_info)
    elif len(x_names) == 2:
        plot = _surface_plot_payload(dataset.dataframe, x_names, y_name, np.asarray(y_fitted), fit_info)
    else:
        plot = _residual_plot_payload(y_values, np.asarray(y_fitted))

    return {
        "datasetId": dataset.dataset_id,
        "equationId": equation_id,
        "plotName": plot_name,
        "xNames": x_names,
        "yName": y_name,
        "rawText": text,
        "formula": formula,
        "formattedEquation": formatted_equation,
        "equationString": equation_string,
        "parameters": _result_param_payload(param_names, params, cov, fit_stats),
        "stats": _fit_stats_payload(fit_stats),
        "plot": plot,
        "exports": {
            "plotPath": plot_path,
            "outputDir": str(Path(plot_path).parent) if plot_path else None,
        },
    }


def _build_equation_catalog() -> list[dict[str, Any]]:
    """Expose equation metadata to the renderer."""

    catalog: list[dict[str, Any]] = []
    for equation_id, meta in EQUATIONS.items():
        catalog.append(
            {
                "id": equation_id,
                "labelKey": f"equations.{equation_id}",
                "descriptionKey": f"equations_descriptions.{equation_id}",
                "formula": meta.get("formula", ""),
                "paramNames": list(meta.get("param_names", [])),
                "type": str(meta.get("type", "python")),
                "numIndependentVars": int(meta.get("num_independent_vars", 1)),
                "initialGuess": list(meta.get("initial_guess", [])) if isinstance(meta.get("initial_guess"), list) else None,
                "bounds": meta.get("bounds"),
            }
        )
    return catalog


def _serialized_env_schema() -> list[dict[str, Any]]:
    """Convert ENV_SCHEMA items to JSON-safe dictionaries."""

    cast_type_names = {str: "str", int: "int", float: "float", bool: "bool"}
    serialized: list[dict[str, Any]] = []
    for item in ENV_SCHEMA:
        serialized.append(
            {
                "key": item["key"],
                "default": _sanitize_scalar(item["default"]),
                "cast_type": cast_type_names.get(item["cast_type"], "str"),
                "options": [_sanitize_scalar(option) for option in item.get("options", [])]
                if item.get("options")
                else None,
            }
        )
    return serialized


def _bootstrap_payload() -> dict[str, Any]:
    """Payload used to initialize the renderer."""

    current_env = get_current_env_values()
    return {
        "version": __version__,
        "supportedLanguages": list(SUPPORTED_LANGUAGE_CODES),
        "activeLanguage": current_env.get("LANGUAGE", "es"),
        "theme": {
            "fontFamily": UI_STYLE["font_family"],
            "fontSize": UI_STYLE["font_size"],
            "fontSizeLarge": UI_STYLE["font_size_large"],
            "colors": {
                "bg": UI_STYLE["bg"],
                "fg": UI_STYLE["fg"],
                "buttonBg": UI_STYLE["button_bg"],
                "activeBg": UI_STYLE["active_bg"],
                "accept": UI_STYLE["button_fg_accept"],
                "cancel": UI_STYLE["button_fg_cancel"],
                "accent": UI_STYLE["button_fg_accent2"],
                "fieldBg": UI_STYLE["field_bg"],
                "hoverBg": UI_STYLE["widget_hover_bg"],
                "textBg": UI_STYLE["text_bg"],
                "textFg": UI_STYLE["text_fg"],
                "selectionBg": UI_STYLE["text_select_bg"],
            },
            "spacing": {
                "padding": UI_STYLE["padding"],
                "borderWidth": UI_STYLE["border_width"],
            },
        },
        "config": {
            "schema": _serialized_env_schema(),
            "values": current_env,
            "restartRequired": True,
        },
        "equations": _build_equation_catalog(),
        "availableEquationTypes": list(AVAILABLE_EQUATION_TYPES),
        "dataAnalysis": {
            "transforms": list(TRANSFORM_OPTIONS.keys()),
            "cleaning": list(CLEAN_OPTIONS.keys()),
        },
        "modes": [
            {"id": "normal", "labelKey": "menu.normal_fitting"},
            {"id": "multiple", "labelKey": "menu.multiple_datasets"},
            {"id": "checker", "labelKey": "menu.checker_fitting"},
            {"id": "total", "labelKey": "menu.total_fitting"},
            {"id": "data", "labelKey": "menu.view_data"},
        ],
        "links": {"donationsUrl": DONATIONS_URL},
    }


def _config_env_path() -> Path:
    """Return the managed .env path."""

    return get_project_root() / ".env"


def _git_supported() -> bool:
    """Whether update actions are meaningful in this checkout."""

    git_dir = get_project_root() / ".git"
    return git_dir.exists() and git_dir.is_dir()


def _map_backend_exception(exc: Exception) -> DesktopApiError:
    """Translate backend exceptions into renderer-friendly payloads."""

    if isinstance(exc, DesktopApiError):
        return exc
    if isinstance(exc, ValidationError):
        return DesktopApiError(
            code="validation_error",
            message_key="desktop.error.validation",
            status_code=400,
            details=str(exc),
        )
    if isinstance(exc, EquationError):
        return DesktopApiError(
            code="equation_error",
            message_key="desktop.error.equation",
            status_code=400,
            details=str(exc),
        )
    if isinstance(exc, FittingError):
        return DesktopApiError(
            code="fitting_error",
            message_key="desktop.error.fitting",
            status_code=400,
            details=str(exc),
        )
    if isinstance(exc, RegressionLabError):
        return DesktopApiError(
            code="backend_error",
            message_key="desktop.error.backend",
            status_code=400,
            details=str(exc),
        )
    return DesktopApiError(
        code="internal_error",
        message_key="desktop.error.internal",
        status_code=500,
        message_params={"error": str(exc)},
        details={"exceptionType": type(exc).__name__},
    )


def _execute_fit(request: FitRunRequest) -> tuple[dict[str, Any], FitSession]:
    """Run a fit using the existing scientific backend."""

    dataset = _ensure_dataset(request.dataset_id)
    x_names = list(request.x_names)
    if not x_names:
        raise DesktopApiError(
            code="missing_x_variables",
            message_key="dialog.independent_variable",
            status_code=400,
        )

    bounds_override = None
    if request.bounds_override is not None:
        bounds_override = (request.bounds_override.lower, request.bounds_override.upper)

    equation_id = request.equation_id or "custom"
    if request.custom_equation is not None:
        evaluator = CustomFunctionEvaluator(
            equation_str=request.custom_equation.formula,
            parameter_names=request.custom_equation.parameter_names,
            num_independent_vars=request.custom_equation.num_independent_vars,
        )
        text, y_fitted, equation_string, fit_info = evaluator.fit(
            dataset.dataframe,
            x_names if len(x_names) > 1 else x_names[0],
            request.y_name,
            initial_guess_override=request.initial_guess_override,
            bounds_override=bounds_override,
        )
        param_names = list(request.custom_equation.parameter_names)
        equation_id = "custom"
    else:
        fitter = get_fitting_function(
            equation_id,
            initial_guess_override=request.initial_guess_override,
            bounds_override=bounds_override,
        )
        if fitter is None:
            raise DesktopApiError(
                code="unknown_equation_type",
                message_key="dialog.select_equation",
                status_code=400,
                details={"equationId": equation_id},
            )
        text, y_fitted, equation_string, fit_info = fitter(
            dataset.dataframe,
            x_names if len(x_names) > 1 else x_names[0],
            request.y_name,
        )
        param_names = list(EQUATIONS[equation_id].get("param_names", []))

    if fit_info is None:
        raise DesktopApiError(
            code="missing_fit_info",
            message_key="error.fitting_failed",
            status_code=500,
        )

    plot_name = request.plot_name or f"{equation_id}_{request.y_name}"
    plot_path = None
    if request.export_plot:
        plot_path = _create_plot_export(
            data=dataset.dataframe,
            x_names=x_names,
            y_name=request.y_name,
            y_fitted=np.asarray(y_fitted),
            plot_name=plot_name,
            fit_info=fit_info,
        )

    fit_payload = _fit_payload(
        dataset=dataset,
        equation_id=equation_id,
        plot_name=plot_name,
        x_names=x_names,
        y_name=request.y_name,
        text=text,
        y_fitted=np.asarray(y_fitted),
        equation_string=equation_string,
        fit_info=fit_info,
        plot_path=plot_path,
        param_names=param_names,
    )

    fit_session = FitSession(
        fit_id=str(uuid4()),
        dataset_id=dataset.dataset_id,
        equation_id=equation_id,
        x_names=x_names,
        y_name=request.y_name,
        fit_info=fit_info,
        plot_name=plot_name,
        plot_path=plot_path,
        equation_string=equation_string,
        result_text=text,
    )
    FIT_STORE[fit_session.fit_id] = fit_session
    fit_payload["fitId"] = fit_session.fit_id
    fit_payload["mode"] = request.mode
    return fit_payload, fit_session


def create_app() -> FastAPI:
    """Create the desktop API application."""

    app = FastAPI(title="RegressionLab Desktop API", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "null",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DesktopApiError)
    async def _handle_desktop_api_error(_: Any, exc: DesktopApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=_error_payload(exc))

    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation_error(_: Any, exc: RequestValidationError) -> JSONResponse:
        mapped = DesktopApiError(
            code="request_validation_error",
            message_key="desktop.error.request_validation",
            status_code=422,
            details=exc.errors(),
        )
        return JSONResponse(status_code=mapped.status_code, content=_error_payload(mapped))

    @app.exception_handler(Exception)
    async def _handle_unexpected_error(_: Any, exc: Exception) -> JSONResponse:
        logger.error("Unexpected desktop API error: %s", exc, exc_info=True)
        mapped = _map_backend_exception(exc)
        return JSONResponse(status_code=mapped.status_code, content=_error_payload(mapped))

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"ok": True, "status": "healthy", "version": __version__}

    @app.get("/bootstrap")
    async def bootstrap() -> dict[str, Any]:
        return {"ok": True, "data": _bootstrap_payload()}

    @app.get("/help")
    async def help_content() -> dict[str, Any]:
        return {
            "ok": True,
            "data": {
                "sections": HELP_SECTIONS,
                "dataViewSections": DATA_VIEW_HELP_SECTIONS,
                "sectionsHintKey": "help.sections_hint",
            },
        }

    @app.post("/datasets/load")
    async def dataset_load(request: DatasetLoadRequest) -> dict[str, Any]:
        file_type = request.file_type or _infer_file_type(request.file_path)
        dataframe = load_data(request.file_path, file_type)
        dataset_id = str(uuid4())
        session = DatasetSession(
            dataset_id=dataset_id,
            dataframe=dataframe,
            file_path=request.file_path,
            file_type=file_type,
        )
        DATASET_STORE[dataset_id] = session
        return {
            "ok": True,
            "data": _dataset_payload(
                session,
                include_records=request.include_records,
                preview_rows=request.preview_rows,
            ),
        }

    @app.get("/datasets/{dataset_id}")
    async def dataset_get(dataset_id: str, include_records: bool = True, preview_rows: int = 200) -> dict[str, Any]:
        dataset = _ensure_dataset(dataset_id)
        return {
            "ok": True,
            "data": _dataset_payload(dataset, include_records=include_records, preview_rows=preview_rows),
        }

    @app.post("/datasets/{dataset_id}/transform")
    async def dataset_transform(dataset_id: str, request: DatasetTransformRequest) -> dict[str, Any]:
        dataset = _ensure_dataset(dataset_id)
        if request.transform_id not in TRANSFORM_OPTIONS:
            raise DesktopApiError(
                code="unknown_transform",
                message_key="data_analysis.select_transform",
                status_code=400,
                details={"transformId": request.transform_id},
            )
        dataset.dataframe = apply_transform(
            dataset.dataframe,
            request.transform_id,
            columns=request.columns,
            in_place=request.in_place,
        )
        dataset.updated_at = datetime.now(UTC)
        return {
            "ok": True,
            "data": _dataset_payload(
                dataset,
                include_records=request.include_records,
                preview_rows=request.preview_rows,
            ),
        }

    @app.post("/datasets/{dataset_id}/clean")
    async def dataset_clean(dataset_id: str, request: DatasetCleanRequest) -> dict[str, Any]:
        dataset = _ensure_dataset(dataset_id)
        if request.clean_id not in CLEAN_OPTIONS:
            raise DesktopApiError(
                code="unknown_cleaning",
                message_key="data_analysis.select_clean",
                status_code=400,
                details={"cleanId": request.clean_id},
            )
        dataset.dataframe = apply_cleaning(
            dataset.dataframe,
            request.clean_id,
            columns=request.columns,
        )
        dataset.updated_at = datetime.now(UTC)
        return {
            "ok": True,
            "data": _dataset_payload(
                dataset,
                include_records=request.include_records,
                preview_rows=request.preview_rows,
            ),
        }

    @app.post("/datasets/{dataset_id}/save")
    async def dataset_save(dataset_id: str, request: DatasetSaveRequest) -> dict[str, Any]:
        dataset = _ensure_dataset(dataset_id)
        saved_path = save_dataframe(dataset.dataframe, request.file_path, request.file_type)
        return {"ok": True, "data": {"savedPath": saved_path}}

    @app.post("/datasets/{dataset_id}/pair-plot")
    async def dataset_pair_plot(dataset_id: str, request: PairPlotRequest) -> dict[str, Any]:
        dataset = _ensure_dataset(dataset_id)
        return {"ok": True, "data": _pair_plot_payload(dataset, request.variables, request.max_variables)}

    @app.post("/fits/run")
    async def fit_run(request: FitRunRequest) -> dict[str, Any]:
        payload, _ = _execute_fit(request)
        return {"ok": True, "data": payload}

    @app.post("/fits/run-all")
    async def fit_run_all(request: RunAllFitsRequest) -> dict[str, Any]:
        equation_ids = list(request.equation_ids or AVAILABLE_EQUATION_TYPES)
        results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        for equation_id in equation_ids:
            try:
                payload, _ = _execute_fit(
                    FitRunRequest(
                        dataset_id=request.dataset_id,
                        mode="checker" if request.mode == "checker" else "total",
                        x_names=request.x_names,
                        y_name=request.y_name,
                        plot_name=f"{request.plot_name_base}_{equation_id}" if request.plot_name_base else equation_id,
                        equation_id=equation_id,
                        export_plot=request.export_plot,
                    )
                )
                results.append(payload)
            except Exception as exc:
                mapped = _map_backend_exception(exc)
                errors.append(
                    {
                        "equationId": equation_id,
                        "error": _error_payload(mapped)["error"],
                    }
                )
                if request.stop_on_error:
                    raise mapped
        return {"ok": True, "data": {"results": results, "errors": errors}}

    @app.post("/predict")
    async def predict(request: PredictionRequest) -> dict[str, Any]:
        fit_session = _ensure_fit(request.fit_id)
        fit_func = fit_session.fit_info["fit_func"]
        params = list(fit_session.fit_info["params"])
        cov = np.asarray(fit_session.fit_info["cov"])
        x_names = fit_session.fit_info["x_names"]

        x_values = np.asarray(request.x_values, dtype=float)
        if len(x_names) == 1:
            point = x_values.reshape(-1)
        else:
            if len(request.x_values) != len(x_names):
                raise DesktopApiError(
                    code="invalid_prediction_dimension",
                    message_key="dialog.prediction_invalid_input",
                    status_code=400,
                    details={"expected": len(x_names), "received": len(request.x_values)},
                )
            point = x_values.reshape(1, -1)

        y_pred = float(np.squeeze(fit_func(point, *params)))
        sigma_y: Optional[float] = None
        if cov.size > 0 and np.all(np.isfinite(cov)):
            eps = np.sqrt(np.finfo(float).eps) * np.maximum(np.abs(params), 1.0)
            jacobian = np.zeros(len(params))
            for index in range(len(params)):
                p_plus = list(params)
                p_minus = list(params)
                p_plus[index] = params[index] + eps[index]
                p_minus[index] = params[index] - eps[index]
                y_plus = float(np.squeeze(fit_func(point, *p_plus)))
                y_minus = float(np.squeeze(fit_func(point, *p_minus)))
                jacobian[index] = (y_plus - y_minus) / (2.0 * eps[index])
            variance = float(jacobian @ cov @ jacobian)
            sigma_y = float(np.sqrt(max(variance, 0.0)))

        return {
            "ok": True,
            "data": {
                "fitId": fit_session.fit_id,
                "xNames": x_names,
                "xValues": request.x_values,
                "y": y_pred,
                "displayY": format_scientific(y_pred, ".6g"),
                "uncertainty": sigma_y,
                "displayUncertainty": format_scientific(sigma_y, ".6g") if sigma_y is not None else None,
            },
        }

    @app.get("/config")
    async def config_get() -> dict[str, Any]:
        return {
            "ok": True,
            "data": {
                "schema": _serialized_env_schema(),
                "values": get_current_env_values(),
                "restartRequired": True,
            },
        }

    @app.put("/config")
    async def config_put(request: ConfigUpdateRequest) -> dict[str, Any]:
        existing = get_current_env_values()
        merged = {**existing, **request.values}
        env_path = _config_env_path()
        env_path.parent.mkdir(parents=True, exist_ok=True)
        write_env_file(env_path, merged)
        for key, value in merged.items():
            os.environ[key] = value
        return {
            "ok": True,
            "data": {
                "values": merged,
                "restartRequired": True,
            },
        }

    @app.post("/updates/check")
    async def updates_check() -> dict[str, Any]:
        if not _git_supported():
            return {
                "ok": True,
                "data": {
                    "supported": False,
                    "available": False,
                    "latestVersion": None,
                },
            }
        latest_version = is_update_available(__version__)
        return {
            "ok": True,
            "data": {
                "supported": True,
                "available": latest_version is not None,
                "latestVersion": latest_version,
                "currentVersion": __version__,
            },
        }

    @app.post("/updates/apply")
    async def updates_apply() -> dict[str, Any]:
        if not _git_supported():
            raise DesktopApiError(
                code="update_not_supported",
                message_key="update.no_git_repo",
                status_code=400,
            )
        success, message = perform_git_pull()
        return {
            "ok": True,
            "data": {
                "supported": True,
                "success": success,
                "messageKey": message if message.startswith("update.") else None,
                "message": None if message.startswith("update.") else message,
                "restartRequired": success,
            },
        }

    return app


app = create_app()


def main() -> None:
    """Run the desktop API using uvicorn."""

    parser = argparse.ArgumentParser(description="RegressionLab desktop API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
