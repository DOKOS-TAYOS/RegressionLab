"""Application constants, equation mappings, and version."""

from pathlib import Path
from typing import Any

import yaml

# Application version number
__version__ = "0.8.3"

# ---------------------------------------------------------------------------
# Equations configuration
# ---------------------------------------------------------------------------
# Single source of truth loaded from equations.yaml.
# Each entry contains:
#   - function: name of the fitting function to call
#   - formula: LaTeX or display string for the equation
#   - param_names: list of parameter names used in the fit

_EQUATIONS_PATH = Path(__file__).resolve().parent / "equations.yaml"

with open(_EQUATIONS_PATH, encoding="utf-8") as _f:
    _raw_equations: dict[str, Any] = yaml.safe_load(_f)

# Main equations dictionary: eq_id -> { function, formula, param_names }
EQUATIONS: dict[str, dict[str, Any]] = _raw_equations
AVAILABLE_EQUATION_TYPES: list[str] = list(EQUATIONS.keys())

# ---------------------------------------------------------------------------
# Mathematical function replacements
# ---------------------------------------------------------------------------
# Regex patterns for converting user-friendly math notation to NumPy equivalents
# when parsing custom formulas (e.g., 'ln(x)' becomes 'np.log(x)').
# The (?<!np\.) lookbehind prevents re-matching names already inside "np.xxx".
MATH_FUNCTION_REPLACEMENTS: dict[str, str] = {
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

# ---------------------------------------------------------------------------
# File type and UI constants
# ---------------------------------------------------------------------------
# Supported data file extensions (without leading dot)
DATA_FILE_TYPES: tuple[str, ...] = ('csv', 'xlsx', 'txt')

# Signal value indicating user exit intent
EXIT_SIGNAL: str = 'Salir'
