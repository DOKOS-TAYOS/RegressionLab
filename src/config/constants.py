"""Application constants, equation mappings, and version."""

import re as _re
import sys
from typing import Any

from config.equation_registry import get_equation_registry

# Application version number
__version__ = "1.1.2"

# Application metadata
__author__ = "Alejandro Mata Ali"
__copyright__ = "Public content for science use"
__credits__ = ["Alejandro Mata Ali"]
__maintainer__ = "Alejandro Mata Ali"
__email__ = "alejandro.mata.ali@gmail.com"
__status__ = "Production"

# ---------------------------------------------------------------------------
# Equations configuration (base + optional user extensions)
# ---------------------------------------------------------------------------
try:
    _raw_equations = get_equation_registry()
except (FileNotFoundError, ValueError, RuntimeError) as e:
    # Log error if logger is available, otherwise print
    try:
        from utils import get_logger
        logger = get_logger(__name__)
        logger.critical(f"Failed to load equations.yaml: {e}", exc_info=True)
    except ImportError:
        # Logger not available, print to stderr
        print(f"CRITICAL ERROR: Failed to load equations.yaml: {e}", file=sys.stderr)
    
    # Re-raise to prevent application from starting with invalid configuration
    raise

# Main equations dictionary: eq_id -> normalized equation metadata
EQUATIONS: dict[str, dict[str, Any]] = _raw_equations
AVAILABLE_EQUATION_TYPES: tuple[str, ...] = tuple(EQUATIONS.keys())

# Reverse lookup: python-target -> eq_id for O(1) lookup by function name/path
FUNCTION_TO_EQUATION: dict[str, str] = {
    str(name): eq_id
    for eq_id, meta in EQUATIONS.items()
    if str(meta.get("type", "python")) == "python" and meta.get("target")
    for name in {meta.get("target"), meta.get("function")}
    if isinstance(name, str) and name
}
# Reverse lookup: format_template -> formula for O(1) lookup in generic_fit
FORMAT_TO_FORMULA: dict[str, str] = {
    meta["format"]: meta.get("formula", "")
    for meta in EQUATIONS.values()
    if "format" in meta
}

# ---------------------------------------------------------------------------
# Mathematical function replacements
# ---------------------------------------------------------------------------
# Regex patterns for converting user-friendly math notation to NumPy equivalents
# when parsing custom formulas (e.g., 'ln(x)' becomes 'np.log(x)').
# The (?<!np\.) lookbehind prevents re-matching names already inside "np.xxx".
_MATH_FUNCTION_REPLACEMENTS: dict[str, str] = {
    # Logarithmic functions
    r'\bln\b': 'np.log',
    r'(?<!np\.)\blog\b': 'np.log10',
    r'(?<!np\.)\blog10\b': 'np.log10',
    r'(?<!np\.)\blog2\b': 'np.log2',
    
    # Trigonometric functions
    r'(?<!np\.)\bsin\b': 'np.sin',
    r'(?<!np\.)\bcos\b': 'np.cos',
    r'(?<!np\.)\btan\b': 'np.tan',
    r'(?<!np\.)\basin\b': 'np.arcsin',
    r'(?<!np\.)\bacos\b': 'np.arccos',
    r'(?<!np\.)\batan\b': 'np.arctan',
    r'(?<!np\.)\barcsin\b': 'np.arcsin',
    r'(?<!np\.)\barccos\b': 'np.arccos',
    r'(?<!np\.)\barctan\b': 'np.arctan',
    
    # Trigonometric functions (Spanish variants)
    r'(?<!np\.)\bsen\b': 'np.sin',  # Spanish: seno
    r'(?<!np\.)\btg\b': 'np.tan',  # Spanish: tangente
    r'(?<!np\.)\barcsen\b': 'np.arcsin',  # Spanish: arcoseno
    r'(?<!np\.)\barctg\b': 'np.arctan',  # Spanish: arcotangente
    
    # Hyperbolic functions
    r'(?<!np\.)\bsinh\b': 'np.sinh',
    r'(?<!np\.)\bcosh\b': 'np.cosh',
    r'(?<!np\.)\btanh\b': 'np.tanh',
    r'(?<!np\.)\basinh\b': 'np.arcsinh',
    r'(?<!np\.)\bacosh\b': 'np.arccosh',
    r'(?<!np\.)\batanh\b': 'np.arctanh',
    r'(?<!np\.)\barcsinh\b': 'np.arcsinh',
    r'(?<!np\.)\barccosh\b': 'np.arccosh',
    r'(?<!np\.)\barctanh\b': 'np.arctanh',
    
    # Hyperbolic functions (Spanish variants)
    r'(?<!np\.)\bsenh\b': 'np.sinh',  # Spanish: seno hiperbólico
    r'(?<!np\.)\btgh\b': 'np.tanh',  # Spanish: tangente hiperbólica
    r'(?<!np\.)\barcsenh\b': 'np.arcsinh',  # Spanish: arcoseno hiperbólico
    r'(?<!np\.)\barctgh\b': 'np.arctanh',  # Spanish: arcotangente hiperbólica
    
    # Exponential and power functions
    r'(?<!np\.)\bexp\b': 'np.exp',
    r'(?<!np\.)\bsqrt\b': 'np.sqrt',
    r'(?<!np\.)\bcbrt\b': 'np.cbrt',
    r'(?<!np\.)\bpower\b': 'np.power',
    
    # Rounding and absolute value
    r'(?<!np\.)\babs\b': 'np.abs',
    r'(?<!np\.)\bfloor\b': 'np.floor',
    r'(?<!np\.)\bceil\b': 'np.ceil',
    r'(?<!np\.)\bround\b': 'np.round',
    
    # Statistical functions
    r'(?<!np\.)\bmax\b': 'np.max',
    r'(?<!np\.)\bmin\b': 'np.min',
    r'(?<!np\.)\bmean\b': 'np.mean',
    r'(?<!np\.)\bsum\b': 'np.sum',
    
    # Constants
    r'(?<!np\.)\bpi\b': 'np.pi',
    r'(?<!np\.)\be\b': 'np.e',
}

# Pre-compiled version of _MATH_FUNCTION_REPLACEMENTS for use in hot paths.
# Each entry is (compiled_regex, replacement_string).
MATH_FUNCTION_REPLACEMENTS_COMPILED: list[tuple[_re.Pattern[str], str]] = [
    (_re.compile(pattern), replacement)
    for pattern, replacement in _MATH_FUNCTION_REPLACEMENTS.items()
]

# ---------------------------------------------------------------------------
# Language (i18n) constants
# ---------------------------------------------------------------------------
# Canonical language codes supported by the app. Add new codes here when
# adding a language; then add aliases to LANGUAGE_ALIASES and translation
# files under locales/.
SUPPORTED_LANGUAGE_CODES: tuple[str, ...] = ('es', 'en', 'de')
DEFAULT_LANGUAGE: str = 'es'

# Aliases accepted in .env LANGUAGE (lowercase). Map alias -> canonical code.
# Canonical codes (es, en, de) are valid by themselves and need not be here.
LANGUAGE_ALIASES: dict[str, str] = {
    'español': 'es',
    'spanish': 'es',
    'esp': 'es',
    'english': 'en',
    'ingles': 'en',
    'inglés': 'en',
    'eng': 'en',
    'german': 'de',
    'deutsch': 'de',
    'ger': 'de',
}

# All accepted values for LANGUAGE (canonical codes + aliases), for validation.
VALID_LANGUAGE_INPUTS: frozenset[str] = frozenset(SUPPORTED_LANGUAGE_CODES) | frozenset(LANGUAGE_ALIASES.keys())

# ---------------------------------------------------------------------------
# File type and UI constants
# ---------------------------------------------------------------------------
# Supported data file extensions (without leading dot)
DATA_FILE_TYPES: tuple[str, ...] = ('csv', 'xlsx', 'txt')

# Signal value indicating user exit intent
EXIT_SIGNAL: str = 'Exit'
