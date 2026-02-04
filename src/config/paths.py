"""File paths and output directory configuration."""

import os
from pathlib import Path
from typing import Optional

from .env import get_env


def _normalize_plot_format(value: str) -> str:
    """Return a valid plot format extension (png, jpg, or pdf)."""
    v = (value or 'png').strip().lower()
    if v in ('jpg', 'jpeg'):
        return 'jpg'
    if v in ('png', 'pdf'):
        return v
    return 'png'


PLOT_FORMATS = ('png', 'jpg', 'jpeg', 'pdf')

FILE_CONFIG = {
    'input_dir': get_env('FILE_INPUT_DIR', 'input'),
    'output_dir': get_env('FILE_OUTPUT_DIR', 'output'),
    'filename_template': get_env('FILE_FILENAME_TEMPLATE', 'fit_{}.png'),
    'plot_format': _normalize_plot_format(get_env('FILE_PLOT_FORMAT', 'png')),
}


def get_project_root() -> Path:
    """Get the project root directory (parent of src/)."""
    # __file__ is src/config/paths.py -> parent=config, parent.parent=src, parent.parent.parent=project root
    return Path(__file__).resolve().parent.parent.parent


def ensure_output_directory(output_dir: Optional[str] = None) -> str:
    """Create output directory if it doesn't exist. Returns the output directory path."""
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']
    project_root = get_project_root()
    full_path = project_root / output_dir
    try:
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Could not create output directory: {e!s}") from e
    return str(full_path)


def get_output_path(fit_name: str, output_dir: Optional[str] = None) -> str:
    """Get the full output path for a plot."""
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']
    output_path = ensure_output_directory(output_dir)
    filename = FILE_CONFIG['filename_template'].format(fit_name)
    base, _ = os.path.splitext(filename)
    fmt = FILE_CONFIG.get('plot_format', 'png')
    filename = f"{base}.{fmt}"
    return os.path.join(output_path, filename)
