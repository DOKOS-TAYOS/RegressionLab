"""Tests that backend imports stay non-interactive."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def test_backend_imports_do_not_create_tk_root() -> None:
    """Core/backend imports should not create a Tk root window."""
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"

    script = """
import importlib
import sys

for module_name in [
    "config",
    "i18n",
    "utils.logger",
    "utils.update_checker",
    "utils.validators",
    "loaders.saving_utils",
    "fitting.fitting_utils",
]:
    importlib.import_module(module_name)

try:
    import tkinter as _tk
    root_created = getattr(_tk, "_default_root", None) is not None
except Exception:
    root_created = False

print("root_created" if root_created else "ok")
"""

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_path) + (os.pathsep + existing if existing else "")

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
