"""
Fitting functions and operations for curve fitting.

This package re-exports all model functions and fitting wrappers from
fitting.functions so that existing code using getattr(fitting_functions, name)
continues to work.

Provides:
    1. Mathematical functions for curve fitting (linear_function, sin_function, etc.)
    2. High-level fitting wrappers (fit_linear_function, fit_sin_function, etc.)
    3. Factory functions to generate custom fitting functions dynamically
"""

from fitting.functions import (
    __all__ as _functions_all,
)
from fitting.functions import *  # noqa: F401, F403

__all__ = _functions_all
