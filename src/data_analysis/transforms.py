"""Data transforms: Fourier, DCT, log, etc."""

from typing import List, Optional

import numpy as np
import pandas as pd

try:
    from scipy.fft import dct, idct
    _HAS_SCIPY_DCT = True
except ImportError:
    dct = None  # type: ignore[assignment, misc]
    idct = None  # type: ignore[assignment, misc]
    _HAS_SCIPY_DCT = False

from data_analysis._utils import get_numeric_columns
from utils import get_logger

logger = get_logger(__name__)

# Transform identifiers for UI
TRANSFORM_FFT = 'fft'
TRANSFORM_FFT_MAGNITUDE = 'fft_magnitude'
TRANSFORM_DCT = 'dct'
TRANSFORM_LOG = 'log'
TRANSFORM_LOG10 = 'log10'
TRANSFORM_EXP = 'exp'
TRANSFORM_SQRT = 'sqrt'
TRANSFORM_SQUARE = 'square'
TRANSFORM_STANDARDIZE = 'standardize'
TRANSFORM_NORMALIZE = 'normalize'
# Inverse transforms
TRANSFORM_IFFT = 'ifft'
TRANSFORM_IDCT = 'idct'

TRANSFORM_OPTIONS: dict[str, str] = {
    TRANSFORM_FFT: 'FFT (complex)',
    TRANSFORM_FFT_MAGNITUDE: 'FFT magnitude',
    TRANSFORM_DCT: 'DCT (cosine)',
    TRANSFORM_LOG: 'Log (natural)',
    TRANSFORM_LOG10: 'Log10',
    TRANSFORM_EXP: 'Exp',
    TRANSFORM_SQRT: 'Square root',
    TRANSFORM_SQUARE: 'Square',
    TRANSFORM_STANDARDIZE: 'Standardize (z-score)',
    TRANSFORM_NORMALIZE: 'Normalize [0,1]',
    TRANSFORM_IFFT: 'Inverse FFT',
    TRANSFORM_IDCT: 'Inverse DCT',
}


def _apply_to_column(series: pd.Series, transform_id: str) -> pd.Series:
    """
    Apply a single transform to a numeric series.

    Args:
        series: Numeric pandas Series to transform.
        transform_id: One of TRANSFORM_* constants.

    Returns:
        New Series with transformed values (NaN preserved where present).
    """
    arr = np.asarray(series, dtype=float)
    nan_mask = np.isnan(arr)
    valid = arr.copy()
    valid[nan_mask] = 0  # temporary for transforms that don't handle NaN

    if transform_id == TRANSFORM_FFT:
        out = np.fft.fft(valid)
        result = np.real(out)  # store real part in one column, could add imag
        result = np.where(nan_mask, np.nan, result)
        return pd.Series(result, index=series.index, name=series.name)

    if transform_id == TRANSFORM_FFT_MAGNITUDE:
        out = np.fft.fft(valid)
        mag = np.abs(out)
        mag = np.where(nan_mask, np.nan, mag)
        return pd.Series(mag, index=series.index, name=series.name)

    if transform_id == TRANSFORM_DCT:
        if _HAS_SCIPY_DCT and dct is not None:
            out = dct(valid, type=2)
        else:
            out = np.fft.fft(valid).real  # fallback
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_LOG:
        out = np.log(np.where(valid <= 0, np.nan, valid))
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_LOG10:
        out = np.log10(np.where(valid <= 0, np.nan, valid))
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_EXP:
        out = np.exp(valid)
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_SQRT:
        out = np.sqrt(np.where(valid < 0, np.nan, valid))
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_SQUARE:
        out = valid ** 2
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_STANDARDIZE:
        valid_clean = arr[~nan_mask]
        if len(valid_clean) == 0:
            return pd.Series(np.full_like(arr, np.nan), index=series.index, name=series.name)
        mean, std = valid_clean.mean(), valid_clean.std()  # z-score uses population std (ddof=0)
        if std == 0:
            out = np.zeros_like(arr)
        else:
            out = (arr - mean) / std
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_NORMALIZE:
        valid_clean = arr[~nan_mask]
        if len(valid_clean) == 0:
            return pd.Series(np.full_like(arr, np.nan), index=series.index, name=series.name)
        lo, hi = valid_clean.min(), valid_clean.max()
        if hi == lo:
            out = np.zeros_like(arr)
        else:
            out = (arr - lo) / (hi - lo)
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    # Inverse transforms
    if transform_id == TRANSFORM_IFFT:
        out = np.fft.ifft(valid).real
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    if transform_id == TRANSFORM_IDCT:
        if _HAS_SCIPY_DCT and idct is not None:
            out = idct(valid, type=2)
        else:
            out = np.fft.ifft(valid).real  # fallback
        out = np.where(nan_mask, np.nan, out)
        return pd.Series(out, index=series.index, name=series.name)

    raise ValueError(f"Unknown transform: {transform_id}")


def apply_transform(
    data: pd.DataFrame,
    transform_id: str,
    columns: Optional[List[str]] = None,
    in_place: bool = True,
) -> pd.DataFrame:
    """
    Apply a transform to selected numeric columns.

    Args:
        data: Input DataFrame.
        transform_id: One of TRANSFORM_* constants.
        columns: Columns to transform. If None, all numeric columns.
        in_place: If True, replace columns. If False, add new columns with suffix.

    Returns:
        New DataFrame with transformed columns.
    """
    cols = get_numeric_columns(data, columns)
    if not cols:
        logger.warning("No numeric columns to transform")
        return data.copy()

    result = data.copy()
    for col in cols:
        try:
            transformed = _apply_to_column(result[col], transform_id)
            if in_place:
                result[col] = transformed
            else:
                result[f"{col}_{transform_id}"] = transformed
        except Exception as e:
            logger.warning(f"Transform {transform_id} failed for column {col}: {e}")

    return result
