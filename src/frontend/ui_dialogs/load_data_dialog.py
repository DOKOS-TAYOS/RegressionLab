"""Load data dialog using native file picker (replaces ask_file_type + ask_file_name)."""

from pathlib import Path
from typing import Optional, Tuple

from typing import Union

from tkinter import Tk, Toplevel, filedialog

from i18n import t
from loaders import get_default_save_directory


def open_load_dialog(parent: Union[Tk, Toplevel]) -> Tuple[Optional[str], Optional[str]]:
    """
    Open native file dialog to select a data file (CSV, TXT, XLSX).

    Replaces the two-step flow (file type + file name) with a single
    native OS dialog. Works on Windows, Linux, and macOS.

    Args:
        parent: Parent Tkinter window (Toplevel or Tk).

    Returns:
        Tuple (file_path, file_type) if user selects a file, or (None, None)
        if user cancels. file_type is one of 'csv', 'txt', 'xlsx'.
    """
    initial_dir = get_default_save_directory()
    path = filedialog.askopenfilename(
        parent=parent,
        initialdir=initial_dir,
        title=t('dialog.upload_file'),
        filetypes=[
            (
                t('dialog.all_data_files'),
                '*.csv *.txt *.xlsx',
            ),
            (t('data_analysis.filetype_csv'), '*.csv'),
            (t('data_analysis.filetype_txt'), '*.txt'),
            (t('data_analysis.filetype_xlsx'), '*.xlsx'),
        ],
    )
    if not path:
        return (None, None)
    ext = Path(path).suffix.lower().lstrip('.')
    if ext not in ('csv', 'txt', 'xlsx'):
        return (None, None)
    return (path, ext)
