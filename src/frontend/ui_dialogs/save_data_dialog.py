"""Save data dialog for the data view window."""

from pathlib import Path
from typing import Callable

import pandas as pd
from tkinter import Toplevel, filedialog, messagebox

from i18n import t
from loaders import get_default_save_directory, save_dataframe


def open_save_dialog(
    parent: Toplevel,
    data: pd.DataFrame,
    on_focus_data: Callable[[], None],
) -> None:
    """Open save file dialog for the current data."""
    initial_dir = get_default_save_directory()
    path = filedialog.asksaveasfilename(
        parent=parent,
        initialdir=initial_dir,
        defaultextension='.csv',
        filetypes=[
            (t('data_analysis.filetype_csv'), '*.csv'),
            (t('data_analysis.filetype_txt'), '*.txt'),
            (t('data_analysis.filetype_xlsx'), '*.xlsx'),
        ],
    )
    if not path:
        on_focus_data()
        return
    try:
        ext = Path(path).suffix.lower().lstrip('.')
        save_dataframe(data, path, ext if ext in ('csv', 'txt', 'xlsx') else 'csv')
        messagebox.showinfo(t('dialog.data'), t('data_analysis.saved_ok', path=path))
    except Exception as e:
        messagebox.showerror(t('dialog.data'), str(e))
    on_focus_data()
