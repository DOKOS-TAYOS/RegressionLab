"""
Custom Function Evaluator Module.

This module provides safe runtime evaluation of custom mathematical functions
for curve fitting.
"""

# Standard library
import ast
import re
from typing import Any, Callable, List, Optional, Tuple, Union

# Third-party packages
import numpy as np
import pandas as pd
from numpy.typing import NDArray

# Local imports
from config import MATH_FUNCTION_REPLACEMENTS_COMPILED
from i18n import t
from utils import (
    EquationError,
    ValidationError,
    get_logger,
    validate_parameter_names,
)

logger = get_logger(__name__)

_ALLOWED_AST_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Attribute,
}
_ALLOWED_BIN_OPS = {
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
}
_ALLOWED_UNARY_OPS = {
    ast.UAdd,
    ast.USub,
}
_ALLOWED_NUMPY_MEMBERS = {
    "sin",
    "cos",
    "tan",
    "arcsin",
    "arccos",
    "arctan",
    "sinh",
    "cosh",
    "tanh",
    "arcsinh",
    "arccosh",
    "arctanh",
    "exp",
    "sqrt",
    "cbrt",
    "power",
    "log",
    "log10",
    "log2",
    "abs",
    "floor",
    "ceil",
    "round",
    "max",
    "min",
    "mean",
    "sum",
    "pi",
    "e",
}


class CustomFunctionEvaluator:
    """Evaluates custom mathematical functions safely at runtime."""

    def __init__(
        self,
        equation_str: str,
        parameter_names: List[str],
        num_independent_vars: int = 1,
    ):
        logger.info("Creating custom function evaluator: '%s'", equation_str)
        logger.debug(
            "Parameters: %s, Independent vars: %s",
            parameter_names,
            num_independent_vars,
        )

        if not equation_str or not equation_str.strip():
            logger.error("Empty equation string provided")
            raise ValidationError(t("error.equation_empty"))

        if num_independent_vars < 1:
            logger.error("Invalid number of independent variables: %s", num_independent_vars)
            raise ValidationError(t("error.invalid_independent_vars", num=num_independent_vars))

        validate_parameter_names(parameter_names)

        self.original_equation_str = equation_str
        self.parameter_names = parameter_names
        self.num_independent_vars = num_independent_vars

        try:
            self.equation_str = self._prepare_formula(equation_str)
            self._compiled_code = self._compile_and_validate_formula(self.equation_str)
            self.function = self._create_function()
            logger.info("Custom function evaluator created successfully")
        except Exception as e:
            logger.error("Failed to create custom function: %s", str(e), exc_info=True)
            raise EquationError(t("error.equation_create_error", error=str(e)))

    def _prepare_formula(self, equation_str: str) -> str:
        """Convert mathematical notation to NumPy function calls."""
        logger.debug("Preparing formula: %s", equation_str)
        try:
            prepared = equation_str
            for compiled_pattern, replacement in MATH_FUNCTION_REPLACEMENTS_COMPILED:
                prepared = compiled_pattern.sub(replacement, prepared)
            logger.debug("Formula prepared: %s", prepared)
            return prepared
        except Exception as e:
            logger.error("Error preparing formula: %s", str(e), exc_info=True)
            raise EquationError(t("error.equation_prepare_error", error=str(e)))

    def _compile_and_validate_formula(self, expression: str) -> Any:
        """Validate AST against a strict allowlist and compile to code object."""
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            logger.error("Formula has syntax error: %s", str(e))
            raise EquationError(t("error.equation_syntax_error", error=str(e)))

        allowed_names = set(self.parameter_names)
        allowed_names.add("np")
        if self.num_independent_vars == 1:
            allowed_names.add("x")
        else:
            allowed_names.update(f"x_{i}" for i in range(self.num_independent_vars))

        for node in ast.walk(tree):
            if type(node) not in _ALLOWED_AST_NODES and not isinstance(node, ast.operator) and not isinstance(node, ast.unaryop):
                raise EquationError(t("error.evaluation_error", error=f"Unsupported syntax: {type(node).__name__}"))

            if isinstance(node, ast.BinOp) and type(node.op) not in _ALLOWED_BIN_OPS:
                raise EquationError(t("error.evaluation_error", error=f"Unsupported operator: {type(node.op).__name__}"))

            if isinstance(node, ast.UnaryOp) and type(node.op) not in _ALLOWED_UNARY_OPS:
                raise EquationError(t("error.evaluation_error", error=f"Unsupported unary operator: {type(node.op).__name__}"))

            if isinstance(node, ast.Name):
                if node.id not in allowed_names:
                    raise EquationError(t("error.evaluation_error", error=f"Unknown identifier: {node.id}"))

            if isinstance(node, ast.Attribute):
                if not isinstance(node.value, ast.Name) or node.value.id != "np":
                    raise EquationError(t("error.evaluation_error", error="Only numpy attributes are allowed"))
                if node.attr not in _ALLOWED_NUMPY_MEMBERS:
                    raise EquationError(t("error.evaluation_error", error=f"Unsupported numpy member: np.{node.attr}"))

            if isinstance(node, ast.Call):
                if node.keywords:
                    raise EquationError(t("error.evaluation_error", error="Keyword arguments are not allowed"))
                if not isinstance(node.func, ast.Attribute):
                    raise EquationError(t("error.evaluation_error", error="Only numpy function calls are allowed"))
                if not isinstance(node.func.value, ast.Name) or node.func.value.id != "np":
                    raise EquationError(t("error.evaluation_error", error="Only numpy function calls are allowed"))
                if node.func.attr not in _ALLOWED_NUMPY_MEMBERS:
                    raise EquationError(t("error.evaluation_error", error=f"Unsupported numpy function: np.{node.func.attr}"))

            if isinstance(node, ast.Constant):
                if not isinstance(node.value, (int, float)):
                    raise EquationError(t("error.evaluation_error", error="Only numeric constants are allowed"))

        return compile(tree, "<custom_formula>", "eval")

    def _create_function(self) -> Callable:
        """Create callable function from validated expression."""
        num_indep = self.num_independent_vars

        def custom_func(x: NDArray, *params: float) -> NDArray:
            if len(params) != len(self.parameter_names):
                error_msg = f"Expected {len(self.parameter_names)} parameters, got {len(params)}"
                logger.error(error_msg)
                raise EquationError(error_msg)

            if num_indep == 1:
                namespace: dict[str, Any] = {
                    "np": np,
                    "x": x,
                    **dict(zip(self.parameter_names, params)),
                }
            else:
                if x.ndim == 1:
                    raise EquationError(
                        f"Expected 2D array for {num_indep} independent variables, got 1D"
                    )
                if x.shape[1] != num_indep:
                    raise EquationError(
                        f"Expected {num_indep} columns in x array, got {x.shape[1]}"
                    )
                namespace = {
                    "np": np,
                    **{f"x_{i}": x[:, i] for i in range(num_indep)},
                    **dict(zip(self.parameter_names, params)),
                }

            try:
                result = eval(self._compiled_code, {"__builtins__": {}}, namespace)
                return np.asarray(result)
            except ZeroDivisionError as e:
                logger.error("Division by zero in formula: %s", str(e))
                raise EquationError(t("error.equation_division_by_zero", error=str(e)))
            except OverflowError as e:
                logger.error("Overflow in formula evaluation: %s", str(e))
                raise EquationError(t("error.equation_overflow_error", error=str(e)))
            except Exception as e:
                logger.error("Error evaluating formula: %s", str(e), exc_info=True)
                raise EquationError(t("error.evaluation_error", error=str(e)))

        return custom_func

    def _generate_equation_template(self) -> str:
        """Generate equation template for displaying fitted parameters."""
        if not self.parameter_names:
            return "y=" + self.original_equation_str
        pattern = re.compile("|".join(r"\b" + re.escape(p) + r"\b" for p in self.parameter_names))
        template = pattern.sub(lambda m: "{" + m.group(0) + "}", self.original_equation_str)
        return "y=" + template

    def fit(
        self,
        data: Union[dict, pd.DataFrame],
        x_name: Union[str, List[str]],
        y_name: str,
        initial_guess_override: Optional[List[Optional[float]]] = None,
        bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
    ) -> Tuple[str, NDArray, str, Optional[dict]]:
        """Perform curve fitting using this custom expression."""
        logger.info("Performing custom fit: %s", self.original_equation_str)

        from fitting.fitting_utils import generic_fit, merge_bounds, merge_initial_guess

        try:
            equation_template = self._generate_equation_template()
            logger.debug("Equation template: %s", equation_template)

            computed_guess = [1.0] * len(self.parameter_names)
            initial_guess = merge_initial_guess(computed_guess, initial_guess_override)
            bounds = (
                merge_bounds(None, bounds_override[0], bounds_override[1], len(self.parameter_names))
                if bounds_override is not None
                else None
            )

            result = generic_fit(
                data=data,
                x_name=x_name,
                y_name=y_name,
                fit_func=self.function,
                param_names=self.parameter_names,
                equation_template=equation_template,
                equation_formula=self.original_equation_str,
                initial_guess=initial_guess,
                bounds=bounds,
            )
            logger.info("Custom fit completed successfully")
            return result
        except Exception as e:
            logger.error("Custom fit failed: %s", str(e), exc_info=True)
            raise

    def get_function(self) -> Callable:
        """Get generated callable function for direct use."""
        return self.function

    def __repr__(self) -> str:
        """String representation of evaluator."""
        return (
            f"CustomFunctionEvaluator(formula='{self.original_equation_str}', "
            f"params={self.parameter_names})"
        )
