"""Tests for the Electron desktop sidecar API."""

from __future__ import annotations

from pathlib import Path
import shutil
from uuid import uuid4

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from regressionlab import desktop_api


@pytest.fixture(autouse=True)
def clear_sidecar_state() -> None:
    """Clear in-memory dataset and fit stores between tests."""

    desktop_api.DATASET_STORE.clear()
    desktop_api.FIT_STORE.clear()


@pytest.fixture()
def client() -> TestClient:
    """Create a test client for the desktop API."""

    return TestClient(desktop_api.app)


@pytest.fixture()
def workspace_temp_dir() -> Path:
    """Create a scratch directory inside the repo to avoid system temp permissions."""

    temp_dir = Path(__file__).resolve().parent / ".tmp" / uuid4().hex
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def csv_dataset_path(workspace_temp_dir: Path) -> Path:
    """Create a simple linear dataset file."""

    dataset_path = workspace_temp_dir / "linear.csv"
    dataset_path.write_text("x,ux,y,uy\n1,0.1,2,0.2\n2,0.1,4,0.2\n3,0.1,6,0.2\n", encoding="utf-8")
    return dataset_path


def _load_dataset(client: TestClient, file_path: Path) -> dict:
    response = client.post("/datasets/load", json={"file_path": str(file_path), "include_records": True})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["rowCount"] == 3
    return payload


def test_load_transform_and_clean_dataset(client: TestClient, csv_dataset_path: Path) -> None:
    dataset = _load_dataset(client, csv_dataset_path)

    transformed = client.post(
        f"/datasets/{dataset['id']}/transform",
        json={"transform_id": "square", "include_records": True},
    )
    assert transformed.status_code == 200
    transformed_payload = transformed.json()["data"]
    assert transformed_payload["preview"][0]["x"] == 1.0
    assert transformed_payload["preview"][1]["y"] == 16.0

    cleaned = client.post(
        f"/datasets/{dataset['id']}/clean",
        json={"clean_id": "drop_duplicates", "include_records": True},
    )
    assert cleaned.status_code == 200
    assert cleaned.json()["data"]["rowCount"] == 3


def test_run_fit_and_predict(client: TestClient, csv_dataset_path: Path) -> None:
    dataset = _load_dataset(client, csv_dataset_path)

    fit_response = client.post(
        "/fits/run",
        json={
            "dataset_id": dataset["id"],
            "mode": "normal",
            "equation_id": "linear_function",
            "x_names": ["x"],
            "y_name": "y",
            "plot_name": "linear_fit",
            "export_plot": False,
        },
    )
    assert fit_response.status_code == 200
    fit_payload = fit_response.json()["data"]
    assert fit_payload["equationId"] == "linear_function"
    assert fit_payload["plot"]["kind"] == "curve2d"
    assert fit_payload["parameters"]

    prediction = client.post(
        "/predict",
        json={"fit_id": fit_payload["fitId"], "x_values": [5]},
    )
    assert prediction.status_code == 200
    prediction_payload = prediction.json()["data"]
    assert prediction_payload["y"] == pytest.approx(10.0, rel=1e-3)


def test_run_custom_formula_fit(client: TestClient, csv_dataset_path: Path) -> None:
    dataset = _load_dataset(client, csv_dataset_path)

    response = client.post(
        "/fits/run",
        json={
            "dataset_id": dataset["id"],
            "mode": "normal",
            "x_names": ["x"],
            "y_name": "y",
            "custom_equation": {
                "formula": "a*x",
                "parameter_names": ["a"],
                "num_independent_vars": 1,
            },
            "export_plot": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["equationId"] == "custom"
    assert payload["parameters"][0]["name"] == "a"


def test_config_write_uses_target_env_file(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    workspace_temp_dir: Path,
) -> None:
    env_path = workspace_temp_dir / ".env"
    monkeypatch.setattr(desktop_api, "_config_env_path", lambda: env_path)

    response = client.put("/config", json={"values": {"LANGUAGE": "en", "LOG_LEVEL": "DEBUG"}})
    assert response.status_code == 200
    assert env_path.exists()
    contents = env_path.read_text(encoding="utf-8")
    assert "LANGUAGE=en" in contents
    assert "LOG_LEVEL=DEBUG" in contents


def test_update_routes_respect_git_guard(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(desktop_api, "_git_supported", lambda: False)

    check_response = client.post("/updates/check")
    assert check_response.status_code == 200
    assert check_response.json()["data"]["supported"] is False

    apply_response = client.post("/updates/apply")
    assert apply_response.status_code == 400
    assert apply_response.json()["error"]["code"] == "update_not_supported"
