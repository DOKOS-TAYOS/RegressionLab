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
# when parsing custom formulas (e.g., 'ln(x)' becomes 'np.log(x)')
MATH_FUNCTION_REPLACEMENTS: dict[str, str] = {
    # Logarithmic functions
    r'\bln\b': 'np.log',
    r'\blog\b': 'np.log10',
    r'\blog10\b': 'np.log10',
    r'\blog2\b': 'np.log2',
    
    # Trigonometric functions
    r'\bsin\b': 'np.sin',
    r'\bcos\b': 'np.cos',
    r'\btan\b': 'np.tan',
    r'\basin\b': 'np.arcsin',
    r'\bacos\b': 'np.arccos',
    r'\batan\b': 'np.arctan',
    r'\barcsin\b': 'np.arcsin',
    r'\barccos\b': 'np.arccos',
    r'\barctan\b': 'np.arctan',
    
    # Hyperbolic functions
    r'\bsinh\b': 'np.sinh',
    r'\bcosh\b': 'np.cosh',
    r'\btanh\b': 'np.tanh',
    r'\basinh\b': 'np.arcsinh',
    r'\bacosh\b': 'np.arccosh',
    r'\batanh\b': 'np.arctanh',
    r'\barcsinh\b': 'np.arcsinh',
    r'\barccosh\b': 'np.arccosh',
    r'\barctanh\b': 'np.arctanh',
    
    # Exponential and power functions
    r'\bexp\b': 'np.exp',
    r'\bsqrt\b': 'np.sqrt',
    r'\bcbrt\b': 'np.cbrt',
    r'\bpower\b': 'np.power',
    
    # Rounding and absolute value
    r'\babs\b': 'np.abs',
    r'\bfloor\b': 'np.floor',
    r'\bceil\b': 'np.ceil',
    r'\bround\b': 'np.round',
    
    # Statistical functions
    r'\bmax\b': 'np.max',
    r'\bmin\b': 'np.min',
    r'\bmean\b': 'np.mean',
    r'\bsum\b': 'np.sum',
    
    # Constants
    r'\bpi\b': 'np.pi',
    r'\be\b': 'np.e',
}

# ---------------------------------------------------------------------------
# File type and UI constants
# ---------------------------------------------------------------------------
# Supported data file extensions (without leading dot)
DATA_FILE_TYPES: tuple[str, ...] = ('csv', 'xlsx', 'txt')

# Signal value indicating user exit intent
EXIT_SIGNAL: str = 'Salir'
