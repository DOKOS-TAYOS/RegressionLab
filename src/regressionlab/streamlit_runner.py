"""Namespaced Streamlit launcher."""

from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    """Run the Streamlit app using package-aware path resolution."""
    from streamlit.web import cli as stcli

    app_path = Path(__file__).resolve().parent.parent / "streamlit_app" / "app.py"
    sys.argv = ["streamlit", "run", str(app_path), *sys.argv[1:]]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())

