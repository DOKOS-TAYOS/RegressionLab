"""Namespaced entrypoint for the desktop application.

This wrapper is robust for both invocation styles:
1. ``python -m regressionlab.main_program``
2. ``python src/regressionlab/main_program.py``
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Callable


def _load_main_callable() -> Callable[[], None]:
    """Load ``src/main_program.py`` without import-name collisions."""
    src_dir = Path(__file__).resolve().parents[1]
    package_dir = Path(__file__).resolve().parent
    main_program_path = src_dir / "main_program.py"

    # Ensure top-level modules like ``config`` and ``fitting`` are importable.
    # When this file is executed directly, sys.path[0] may be ".../src/regressionlab",
    # which would wrongly resolve "import config" to "regressionlab/config".
    package_dir_str = str(package_dir)
    if package_dir_str in sys.path:
        sys.path.remove(package_dir_str)

    src_dir_str = str(src_dir)
    if src_dir_str not in sys.path:
        sys.path.insert(0, src_dir_str)

    spec = importlib.util.spec_from_file_location(
        "_regressionlab_desktop_main_program",
        main_program_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {main_program_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    main_fn = getattr(module, "main", None)
    if not callable(main_fn):
        raise ImportError(f"Entry function 'main' not found in {main_program_path}")
    return main_fn


def main() -> None:
    """Run desktop RegressionLab entrypoint."""
    main_fn = _load_main_callable()
    main_fn()

__all__ = ["main"]


if __name__ == "__main__":
    main()
