"""Data transforms: Fourier, DCT, Laplace, Hilbert, log, etc."""

from typing import Callable, List, Optional

import numpy as np
import pandas as pd

try:
    from scipy.fft import dct, idct
    _HAS_SCIPY_DCT = True
except ImportError:
    dct = None  # type: ignore[assignment, misc]
    idct = None  # type: ignore[assignment, misc]
    _HAS_SCIPY_DCT = False

try:
    from scipy.signal import hilbert
    _HAS_SCIPY_HILBERT = True
except ImportError:
    hilbert = None  # type: ignore[assignment, misc]
    _HAS_SCIPY_HILBERT = False

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
# Laplace, Hilbert, telecom
TRANSFORM_LAPLACE = 'laplace'
TRANSFORM_ILAPLACE = 'ilaplace'
TRANSFORM_HILBERT = 'hilbert'
TRANSFORM_IHILBERT = 'ihilbert'
TRANSFORM_CEPSTRUM = 'cepstrum'
TRANSFORM_HADAMARD = 'hadamard'
TRANSFORM_IHADAMARD = 'ihadamard'
TRANSFORM_ENVELOPE = 'envelope'
# Inverse transforms
TRANSFORM_IFFT = 'ifft'
TRANSFORM_IDCT = 'idct'

# Order: most important/common first (FFT/DCT, log/exp, normalize, Hilbert/Laplace, telecom)
TRANSFORM_OPTIONS: dict[str, str] = {
    TRANSFORM_FFT: 'FFT (complex)',
    TRANSFORM_FFT_MAGNITUDE: 'FFT magnitude',
    TRANSFORM_IFFT: 'Inverse FFT',
    TRANSFORM_DCT: 'DCT (cosine)',
    TRANSFORM_IDCT: 'Inverse DCT',
    TRANSFORM_LOG: 'Log (natural)',
    TRANSFORM_LOG10: 'Log10',
    TRANSFORM_EXP: 'Exp',
    TRANSFORM_SQRT: 'Square root',
    TRANSFORM_SQUARE: 'Square',
    TRANSFORM_STANDARDIZE: 'Standardize (z-score)',
    TRANSFORM_NORMALIZE: 'Normalize [0,1]',
    TRANSFORM_HILBERT: 'Hilbert',
    TRANSFORM_IHILBERT: 'Inverse Hilbert',
    TRANSFORM_ENVELOPE: 'Envelope (Hilbert)',
    TRANSFORM_LAPLACE: 'Laplace (discrete)',
    TRANSFORM_ILAPLACE: 'Inverse Laplace',
    TRANSFORM_CEPSTRUM: 'Cepstrum (real)',
    TRANSFORM_HADAMARD: 'Hadamard (Walsh)',
    TRANSFORM_IHADAMARD: 'Inverse Hadamard',
}


# ---------------------------------------------------------------------------
# Helper: build result Series preserving NaN positions
# ---------------------------------------------------------------------------

def _make_result(
    out: np.ndarray, nan_mask: np.ndarray, series: pd.Series,
) -> pd.Series:
    """Mask NaN positions back in and return a new Series."""
    return pd.Series(
        np.where(nan_mask, np.nan, out), index=series.index, name=series.name,
    )


# ---------------------------------------------------------------------------
# FFT-based Hilbert helper (shared by hilbert, ihilbert, envelope)
# ---------------------------------------------------------------------------

def _fft_hilbert_filter(n: int) -> np.ndarray:
    """Build the frequency-domain filter for the analytic signal."""
    h = np.zeros(n)
    h[0] = 1
    h[n // 2] = 1 if n % 2 == 0 else 0
    h[1 : n // 2] = 2
    return h


# ---------------------------------------------------------------------------
# Fast Walsh-Hadamard Transform (O(n log n) time, O(n) memory)
# ---------------------------------------------------------------------------

def _fast_walsh_hadamard(a: np.ndarray, normalize: bool = True) -> np.ndarray:
    """Vectorized Fast Walsh-Hadamard Transform. Input length must be power of 2."""
    a = a.astype(float).copy()
    n = len(a)
    h = 1
    while h < n:
        a_reshaped = a.reshape(-1, 2 * h)
        left = a_reshaped[:, :h].copy()
        right = a_reshaped[:, h:]
        a_reshaped[:, :h] = left + right
        a_reshaped[:, h:] = left - right
        h *= 2
    if normalize:
        a /= np.sqrt(n)
    return a


# ---------------------------------------------------------------------------
# Individual transform handlers
# Signature: (arr, nan_mask, valid, series) -> pd.Series
# ---------------------------------------------------------------------------

def _transform_fft(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    out = np.fft.fft(valid)
    return _make_result(np.real(out), nan_mask, series)


def _transform_fft_magnitude(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    return _make_result(np.abs(np.fft.fft(valid)), nan_mask, series)


def _transform_dct(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    if _HAS_SCIPY_DCT and dct is not None:
        out = dct(valid, type=2)
    else:
        out = np.fft.fft(valid).real  # fallback
    return _make_result(out, nan_mask, series)


def _transform_log(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    out = np.log(np.where(valid <= 0, np.nan, valid))
    return pd.Series(out, index=series.index, name=series.name)


def _transform_log10(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    out = np.log10(np.where(valid <= 0, np.nan, valid))
    return pd.Series(out, index=series.index, name=series.name)


def _transform_exp(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    return _make_result(np.exp(valid), nan_mask, series)


def _transform_sqrt(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    out = np.sqrt(np.where(valid < 0, np.nan, valid))
    return pd.Series(out, index=series.index, name=series.name)


def _transform_square(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    return _make_result(valid ** 2, nan_mask, series)


def _transform_standardize(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    valid_clean = arr[~nan_mask]
    if len(valid_clean) == 0:
        return pd.Series(np.full_like(arr, np.nan), index=series.index, name=series.name)
    mean, std = valid_clean.mean(), valid_clean.std()
    if std == 0:
        out = np.zeros_like(arr)
    else:
        out = (arr - mean) / std
    return _make_result(out, nan_mask, series)


def _transform_normalize(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    valid_clean = arr[~nan_mask]
    if len(valid_clean) == 0:
        return pd.Series(np.full_like(arr, np.nan), index=series.index, name=series.name)
    lo, hi = valid_clean.min(), valid_clean.max()
    if hi == lo:
        out = np.zeros_like(arr)
    else:
        out = (arr - lo) / (hi - lo)
    return _make_result(out, nan_mask, series)


def _transform_laplace(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    alpha = 0.1
    n = len(valid)
    exp_neg = np.exp(-alpha * np.arange(n, dtype=float))
    return _make_result(np.cumsum(valid * exp_neg), nan_mask, series)


def _transform_ilaplace(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    alpha = 0.1
    out = np.empty_like(valid)
    out[0] = valid[0]
    n = len(valid)
    if n > 1:
        out[1:] = (valid[1:] - valid[:-1]) * np.exp(alpha * np.arange(1, n, dtype=float))
    return _make_result(out, nan_mask, series)


def _transform_hilbert(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    if _HAS_SCIPY_HILBERT and hilbert is not None:
        out = np.imag(hilbert(valid))
    else:
        h = _fft_hilbert_filter(len(valid))
        out = np.real(np.fft.ifft(np.fft.fft(valid) * h))
    return _make_result(out, nan_mask, series)


def _transform_ihilbert(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    if _HAS_SCIPY_HILBERT and hilbert is not None:
        out = -np.imag(hilbert(valid))
    else:
        h = _fft_hilbert_filter(len(valid))
        out = -np.real(np.fft.ifft(np.fft.fft(valid) * h))
    return _make_result(out, nan_mask, series)


def _transform_cepstrum(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    spec = np.fft.fft(valid)
    eps = 1e-12
    log_spec = np.log(np.abs(spec) ** 2 + eps)
    return _make_result(np.real(np.fft.ifft(log_spec)), nan_mask, series)


def _transform_hadamard(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    n = len(valid)
    n2 = 1 << (n - 1).bit_length()  # next power of 2
    padded = np.zeros(n2)
    padded[:n] = valid
    out = _fast_walsh_hadamard(padded)[:n].copy()
    return _make_result(out, nan_mask, series)


def _transform_ihadamard(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    # The normalized WHT is its own inverse
    n = len(valid)
    n2 = 1 << (n - 1).bit_length()
    padded = np.zeros(n2)
    padded[:n] = valid
    out = _fast_walsh_hadamard(padded)[:n].copy()
    return _make_result(out, nan_mask, series)


def _transform_envelope(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    if _HAS_SCIPY_HILBERT and hilbert is not None:
        out = np.abs(hilbert(valid))
    else:
        h = _fft_hilbert_filter(len(valid))
        analytic = np.fft.ifft(np.fft.fft(valid) * h)
        out = np.abs(analytic)
    return _make_result(out, nan_mask, series)


def _transform_ifft(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    return _make_result(np.fft.ifft(valid).real, nan_mask, series)


def _transform_idct(
    arr: np.ndarray, nan_mask: np.ndarray, valid: np.ndarray, series: pd.Series,
) -> pd.Series:
    if _HAS_SCIPY_DCT and idct is not None:
        out = idct(valid, type=2)
    else:
        out = np.fft.ifft(valid).real  # fallback
    return _make_result(out, nan_mask, series)


# ---------------------------------------------------------------------------
# Dispatch table: transform_id -> handler
# ---------------------------------------------------------------------------

_TRANSFORM_DISPATCH: dict[str, Callable] = {
    TRANSFORM_FFT: _transform_fft,
    TRANSFORM_FFT_MAGNITUDE: _transform_fft_magnitude,
    TRANSFORM_DCT: _transform_dct,
    TRANSFORM_LOG: _transform_log,
    TRANSFORM_LOG10: _transform_log10,
    TRANSFORM_EXP: _transform_exp,
    TRANSFORM_SQRT: _transform_sqrt,
    TRANSFORM_SQUARE: _transform_square,
    TRANSFORM_STANDARDIZE: _transform_standardize,
    TRANSFORM_NORMALIZE: _transform_normalize,
    TRANSFORM_LAPLACE: _transform_laplace,
    TRANSFORM_ILAPLACE: _transform_ilaplace,
    TRANSFORM_HILBERT: _transform_hilbert,
    TRANSFORM_IHILBERT: _transform_ihilbert,
    TRANSFORM_CEPSTRUM: _transform_cepstrum,
    TRANSFORM_HADAMARD: _transform_hadamard,
    TRANSFORM_IHADAMARD: _transform_ihadamard,
    TRANSFORM_ENVELOPE: _transform_envelope,
    TRANSFORM_IFFT: _transform_ifft,
    TRANSFORM_IDCT: _transform_idct,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _apply_to_column(series: pd.Series, transform_id: str) -> pd.Series:
    """
    Apply a single transform to a numeric series.

    Args:
        series: Numeric pandas Series to transform.
        transform_id: One of TRANSFORM_* constants.

    Returns:
        New Series with transformed values (NaN preserved where present).
    """
    handler = _TRANSFORM_DISPATCH.get(transform_id)
    if handler is None:
        raise ValueError(f"Unknown transform: {transform_id}")

    arr = np.asarray(series, dtype=float)
    nan_mask = np.isnan(arr)
    valid = arr.copy()
    valid[nan_mask] = 0  # temporary for transforms that don't handle NaN

    return handler(arr, nan_mask, valid, series)


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
