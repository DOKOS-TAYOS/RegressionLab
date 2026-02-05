#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner script for RegressionLab project.

This script runs all tests using pytest.
"""

import sys
from pathlib import Path
import pytest

if __name__ == '__main__':
    # Run pytest with verbose output
    test_dir = Path(__file__).parent
    exit_code = pytest.main([str(test_dir), '-v', '--tb=short'])
    sys.exit(exit_code)
