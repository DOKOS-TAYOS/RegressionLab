#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom exceptions for the RegresionLab application.

This module defines specific exception types for different error scenarios,
providing better error handling and debugging capabilities.
"""


class RegresionLabError(Exception):
    """Base exception class for all RegresionLab-related errors."""
    pass


class DataLoadError(RegresionLabError):
    """Exception raised when data loading fails."""
    pass


class DataValidationError(RegresionLabError):
    """Exception raised when data validation fails."""
    pass


class FileNotFoundError(DataLoadError):
    """Exception raised when a requested file is not found."""
    pass


class InvalidFileTypeError(DataLoadError):
    """Exception raised when file type is not supported."""
    pass


class FittingError(RegresionLabError):
    """Exception raised when curve fitting fails."""
    pass


class EquationError(RegresionLabError):
    """Exception raised when equation evaluation fails."""
    pass


class ConfigurationError(RegresionLabError):
    """Exception raised when configuration is invalid."""
    pass


class ValidationError(RegresionLabError):
    """Exception raised when input validation fails."""
    pass
