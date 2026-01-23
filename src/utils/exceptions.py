#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom exceptions for the RegressionLab application.

This module defines specific exception types for different error scenarios,
providing better error handling and debugging capabilities.
"""


class RegressionLabError(Exception):
    """Base exception class for all RegressionLab-related errors."""
    pass


class DataLoadError(RegressionLabError):
    """Exception raised when data loading fails."""
    pass


class DataValidationError(RegressionLabError):
    """Exception raised when data validation fails."""
    pass


class FileNotFoundError(DataLoadError):
    """Exception raised when a requested file is not found."""
    pass


class InvalidFileTypeError(DataLoadError):
    """Exception raised when file type is not supported."""
    pass


class FittingError(RegressionLabError):
    """Exception raised when curve fitting fails."""
    pass


class EquationError(RegressionLabError):
    """Exception raised when equation evaluation fails."""
    pass


class ConfigurationError(RegressionLabError):
    """Exception raised when configuration is invalid."""
    pass


class ValidationError(RegressionLabError):
    """Exception raised when input validation fails."""
    pass
