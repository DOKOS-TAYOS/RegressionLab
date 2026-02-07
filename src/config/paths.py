"""File paths and output directory configuration."""

import os
from pathlib import Path
from typing import Optional

from config.env import get_env


def _normalize_plot_format(value: str) -> str:
    """
    Normalize a plot format string to a supported extension.

    Accepts common variants like ``'jpeg'`` and coerces them to one of the
    supported values ``'png'``, ``'jpg'`` or ``'pdf'``. Any unknown value
    falls back to ``'png'``.

    Args:
        value: Raw plot format string (e.g. ``'PNG'``, ``'jpeg'``).

    Returns:
        Normalized extension without leading dot.

    Example:
        >>> _normalize_plot_format('PNG')
        'png'
        >>> _normalize_plot_format('jpeg')
        'jpg'
        >>> _normalize_plot_format('unknown')
        'png'
    """
    normalized = (value or 'png').strip().lower()
    
    # Map common variants to canonical formats
    format_mapping = {
        'jpg': 'jpg',
        'jpeg': 'jpg',
        'png': 'png',
        'pdf': 'pdf',
    }
    
    return format_mapping.get(normalized, 'png')


FILE_CONFIG = {
    'input_dir': get_env('FILE_INPUT_DIR', 'input'),
    'output_dir': get_env('FILE_OUTPUT_DIR', 'output'),
    'filename_template': get_env('FILE_FILENAME_TEMPLATE', 'fit_{}'),
    'plot_format': _normalize_plot_format(get_env('FILE_PLOT_FORMAT', 'png')),
}


def get_project_root() -> Path:
    """
    Get the project root directory (parent of ``src/``).

    The function resolves the path based on the current file location, so it
    works even when the package is installed or executed from another folder.

    Returns:
        Absolute :class:`pathlib.Path` to the project root.
    """
    # __file__ is src/config/paths.py -> parent=config, parent.parent=src, parent.parent.parent=project root
    return Path(__file__).resolve().parent.parent.parent


def ensure_output_directory(output_dir: Optional[str] = None) -> str:
    """
    Ensure that the output directory exists and return its absolute path.

    If ``output_dir`` is ``None``, the value from :data:`FILE_CONFIG` is used.
    The directory is created recursively when missing.

    Args:
        output_dir: Relative output directory name, usually from configuration.

    Returns:
        Absolute path to the output directory as a string.

    Raises:
        OSError: If the directory cannot be created.
    """
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
    """
    Build the full output file path for a plot image.

    The final filename is created from ``FILE_CONFIG['filename_template']``
    and the normalized plot format, ensuring a consistent extension.

    Args:
        fit_name: Base name for the plot (usually the fit or dataset name).
        output_dir: Optional relative output directory; if ``None``, the
            default from :data:`FILE_CONFIG` is used.

    Returns:
        Absolute path to the image file as a string.

    Example:
        >>> get_output_path("linear_fit")
        '.../output/fit_linear_fit.png'
    """
    if output_dir is None:
        output_dir = FILE_CONFIG['output_dir']
    output_path = ensure_output_directory(output_dir)
    filename = FILE_CONFIG['filename_template'].format(fit_name)
    base, _ = os.path.splitext(filename)
    fmt = FILE_CONFIG['plot_format']
    filename = f"{base}.{fmt}"
    return os.path.join(output_path, filename)
