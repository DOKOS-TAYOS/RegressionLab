#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom Function Evaluator Module

This module provides safe runtime evaluation of custom mathematical functions
for curve fitting.

Key features:

    - Safe evaluation with restricted namespace
    - Automatic conversion of mathematical notation to NumPy functions
    - Integration with the generic_fit function
    - No dynamic file generation required
"""

# Standard library
import re
from typing import Callable, List, Tuple

# Third-party packages
import numpy as np
from numpy.typing import NDArray

# Local imports
from config import MATH_FUNCTION_REPLACEMENTS
from utils.exceptions import EquationError, ValidationError
from utils.logger import get_logger
from utils.validators import validate_parameter_names

logger = get_logger(__name__)


class CustomFunctionEvaluator:
    """
    Evaluates custom mathematical functions safely at runtime.
    
    This class takes a user-defined mathematical formula and parameter names,
    converts it to a NumPy-compatible function, and provides methods for
    curve fitting operations.
    
    Example:
        >>> evaluator = CustomFunctionEvaluator("a*x**2 + b*x + c", ["a", "b", "c"])
        >>> texto, y_ajus, ecuacion = evaluator.fit(datos, "x", "y")
    """
    
    def __init__(self, equation_str: str, parameter_names: List[str]):
        """
        Initialize the custom function evaluator.
        
        Args:
            equation_str: Mathematical formula as string (e.g., "a*sin(x) + b")
            parameter_names: List of parameter names used in the formula
            
        Raises:
            ValidationError: If parameter names are invalid
            EquationError: If equation cannot be parsed
        """
        logger.info(f"Creating custom function evaluator: '{equation_str}'")
        logger.debug(f"Parameters: {parameter_names}")
        
        # Validate inputs
        if not equation_str or not equation_str.strip():
            logger.error("Empty equation string provided")
            raise ValidationError("La ecuación no puede estar vacía")
        
        validate_parameter_names(parameter_names)
        
        self.original_equation_str = equation_str
        self.parameter_names = parameter_names
        
        try:
            self.equation_str = self._prepare_formula(equation_str)
            logger.debug(f"Prepared formula: {self.equation_str}")
            self.function = self._create_function()
            logger.info("Custom function evaluator created successfully")
        except Exception as e:
            logger.error(f"Failed to create custom function: {str(e)}", exc_info=True)
            raise EquationError(f"Error al crear la función personalizada: {str(e)}")
    
    def _prepare_formula(self, equation_str: str) -> str:
        """
        Convert mathematical notation to NumPy function calls.
        
        This method replaces standard mathematical function names with their
        NumPy equivalents using the mappings from config.MATH_FUNCTION_REPLACEMENTS.
        For example, 'ln(x)' becomes 'np.log(x)'.
        
        Args:
            equation_str: Original formula string
            
        Returns:
            Formula string with NumPy function calls
            
        Raises:
            EquationError: If formula preparation fails
        """
        logger.debug(f"Preparing formula: {equation_str}")
        
        try:
            prepared = equation_str
            for pattern, replacement in MATH_FUNCTION_REPLACEMENTS.items():
                prepared = re.sub(pattern, replacement, prepared)
            
            logger.debug(f"Formula prepared: {prepared}")
            return prepared
        except Exception as e:
            logger.error(f"Error preparing formula: {str(e)}", exc_info=True)
            raise EquationError(f"Error al preparar la fórmula: {str(e)}")
    
    def _create_function(self) -> Callable:
        """
        Create a callable function from the prepared formula.
        
        This method creates a function that can be used with scipy.optimize.curve_fit.
        The function evaluates the formula in a restricted namespace for security.
        
        Returns:
            Callable function that takes (x, *params) as arguments
            
        Raises:
            EquationError: If function creation fails
        """
        logger.debug("Creating callable function from formula")
        
        # Test the formula syntax by trying to compile it
        try:
            compile(self.equation_str, '<string>', 'eval')
            logger.debug("Formula syntax validation passed")
        except SyntaxError as e:
            logger.error(f"Formula has syntax error: {str(e)}")
            raise EquationError(f"Error de sintaxis en la fórmula: {str(e)}")
        
        def custom_func(x: NDArray, *params: float) -> NDArray:
            """
            Custom function generated from user formula.
            
            Args:
                x: Independent variable (array)
                *params: Parameter values
                
            Returns:
                Evaluated function values
                
            Raises:
                EquationError: If evaluation fails
            """
            # Validate parameter count
            if len(params) != len(self.parameter_names):
                error_msg = (f"Expected {len(self.parameter_names)} parameters, "
                           f"got {len(params)}")
                logger.error(error_msg)
                raise EquationError(error_msg)
            
            # Create safe namespace with only allowed functions and variables
            namespace = {
                'np': np,
                'x': x,
                **dict(zip(self.parameter_names, params))
            }
            
            # Evaluate with restricted builtins for security
            try:
                result = eval(self.equation_str, {"__builtins__": {}}, namespace)
                return result
            except ZeroDivisionError as e:
                logger.error(f"Division by zero in formula: {str(e)}")
                raise EquationError(f"División por cero en la fórmula: {str(e)}")
            except OverflowError as e:
                logger.error(f"Overflow in formula evaluation: {str(e)}")
                raise EquationError(f"Desbordamiento en la evaluación: {str(e)}")
            except Exception as e:
                logger.error(f"Error evaluating formula: {str(e)}", exc_info=True)
                raise EquationError(f"Error al evaluar la fórmula '{self.equation_str}': {str(e)}")
        
        return custom_func
    
    def _generate_equation_template(self) -> str:
        """
        Generate an equation template for displaying fitted parameters.
        
        Returns:
            Template string with parameter placeholders
        """
        # Replace parameter names with format placeholders
        template = self.original_equation_str
        for param in self.parameter_names:
            # Use word boundaries to avoid replacing substrings
            template = re.sub(r'\b' + param + r'\b', '{' + param + '}', template)
        
        return 'y=' + template
    
    def fit(self, data: dict, x_name: str, y_name: str) -> Tuple[str, NDArray, str]:
        """
        Perform curve fitting using the custom function.
        
        This method uses the generic_fit function from fitting_utils to perform
        the actual curve fitting with error propagation.
        
        Args:
            data: Data dictionary containing x, y and their uncertainties
            x_name: Name of the independent variable
            y_name: Name of the dependent variable
            
        Returns:
            Tuple of (text, y_fitted, equation):
                - text: Formatted text with parameters and uncertainties (includes R²)
                - y_fitted: Array with fitted y values
                - equation: Formatted equation with parameter values
                
        Raises:
            FittingError: If fitting fails
        """
        logger.info(f"Performing custom fit: {self.original_equation_str}")
        
        from fitting.fitting_utils import generic_fit
        
        try:
            equation_template = self._generate_equation_template()
            logger.debug(f"Equation template: {equation_template}")
            
            result = generic_fit(
                data=data,
                x_name=x_name,
                y_name=y_name,
                fit_func=self.function,
                param_names=self.parameter_names,
                equation_template=equation_template
            )
            
            logger.info("Custom fit completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Custom fit failed: {str(e)}", exc_info=True)
            raise
    
    def get_function(self) -> Callable:
        """
        Get the generated function for direct use.
        
        Returns:
            The callable function that evaluates the formula
        """
        return self.function
    
    def __repr__(self) -> str:
        """String representation of the evaluator."""
        return (
            f"CustomFunctionEvaluator(formula='{self.original_equation_str}', "
            f"params={self.parameter_names})"
        )
