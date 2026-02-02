#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner script for RegresionLab project.

This script discovers and runs all tests in the tests directory.
"""

# Standard library
import sys
import unittest
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))


def run_all_tests() -> int:
    """
    Discover and run all tests.
    
    Returns:
        Exit code (0 for success, 1 for failures)
    """
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
