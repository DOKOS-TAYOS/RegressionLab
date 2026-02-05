#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for custom exceptions.
"""

import pytest

from utils.exceptions import (
    RegressionLabError,
    DataLoadError,
    DataValidationError,
    FileNotFoundError,
    InvalidFileTypeError,
    FittingError,
    EquationError,
    ConfigurationError,
    ValidationError
)


@pytest.mark.parametrize("exception_class,parent_class", [
    (RegressionLabError, Exception),
    (DataLoadError, RegressionLabError),
    (DataValidationError, RegressionLabError),
    (FileNotFoundError, DataLoadError),
    (InvalidFileTypeError, DataLoadError),
    (FittingError, RegressionLabError),
    (EquationError, RegressionLabError),
    (ConfigurationError, RegressionLabError),
    (ValidationError, RegressionLabError),
])
def test_exception_hierarchy(exception_class: type, parent_class: type) -> None:
    """Test exception class hierarchy."""
    assert issubclass(exception_class, parent_class)


@pytest.mark.parametrize("exception_class", [
    RegressionLabError,
    DataLoadError,
    FittingError,
])
def test_exception_raising(exception_class: type) -> None:
    """Test raising exceptions."""
    with pytest.raises(exception_class):
        raise exception_class("Test error")


def test_catch_specific_as_base() -> None:
    """Test catching specific error as base class."""
    with pytest.raises(RegressionLabError) as exc_info:
        raise FittingError("Test error")
    assert isinstance(exc_info.value, FittingError)


def test_error_message() -> None:
    """Test error message is preserved."""
    test_message = "This is a test error message"
    with pytest.raises(DataValidationError) as exc_info:
        raise DataValidationError(test_message)
    assert str(exc_info.value) == test_message
