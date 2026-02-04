# Contributing to RegressionLab

Thank you for your interest in contributing to RegressionLab! This guide will help you get started with contributing code, documentation, or other improvements to the project.

## Ways to Contribute

There are many ways to contribute to RegressionLab:

- 🐛 **Report bugs**: Help us identify issues
- 💡 **Suggest features**: Share your ideas for improvements
- 📝 **Improve documentation**: Fix typos, add examples, clarify explanations
- 🔧 **Fix bugs**: Submit patches for known issues
- ✨ **Add features**: Implement new functionality
- 🧪 **Write tests**: Improve code coverage
- 🌍 **Add translations**: Support more languages
- 📊 **Add equations**: Contribute new fitting functions
- 🎨 **Improve UI/UX**: Enhance user experience

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub (click "Fork" button)

# Clone your fork
git clone https://github.com/DOKOS-TAYOS/RegressionLab.git
cd RegressionLab

# Add upstream remote
git remote add upstream https://github.com/DOKOS-TAYOS/RegressionLab.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies including development tools
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

### 3. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

**Branch Naming Conventions**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

## Development Guidelines

### Code Style

RegressionLab follows PEP 8 with some project-specific conventions:

#### 1. Line Length
- Maximum 100 characters per line
- For long strings, use implicit concatenation or `textwrap`

```python
# Good
message = (
    "This is a very long message that spans "
    "multiple lines for better readability."
)

# Bad
message = "This is a very long message that spans multiple lines for better readability."
```

#### 2. Type Hints

Always include type hints for function signatures:

```python
from typing import Optional, Tuple
from numpy.typing import NDArray
import numpy as np

def process_data(
    data: NDArray[np.floating],
    threshold: float = 0.5,
    normalize: bool = True
) -> Tuple[NDArray[np.floating], float]:
    """Process data with optional normalization."""
    ...
```

#### 3. Docstrings

Use Google-style docstrings:

```python
def fit_curve(data: pd.DataFrame, equation: str) -> Tuple[np.ndarray, float]:
    """
    Fit a curve to the provided data.
    
    This function performs nonlinear least squares fitting using
    scipy.optimize.curve_fit with automatic initial parameter estimation.
    
    Args:
        data: DataFrame containing x, y, and optional uncertainty columns
        equation: Name of the equation to fit (e.g., 'linear_function')
        
    Returns:
        Tuple containing:
            - Fitted parameters as ndarray
            - R-squared value as float
            
    Raises:
        FittingError: If the fitting algorithm fails to converge
        ValueError: If equation name is not recognized
        
    Examples:
        >>> data = pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 6]})
        >>> params, r2 = fit_curve(data, 'linear_function')
        >>> params
        array([2.0])
        >>> r2
        1.0
    """
    ...
```

#### 4. Imports

Organize imports in three groups, separated by blank lines:

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Optional, List

# Third-party packages
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# Local imports
from config import AVAILABLE_EQUATION_TYPES
from fitting.fitting_utils import generic_fit
from utils.exceptions import FittingError
from utils.logger import get_logger
```

#### 5. Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

```python
# Good
MAX_ITERATIONS = 1000

class DataLoader:
    def __init__(self):
        self._cache = {}
    
    def load_file(self, file_path: str) -> pd.DataFrame:
        ...
    
    def _parse_header(self, line: str) -> List[str]:
        ...
```

#### 6. Comments

- Use comments sparingly - prefer self-documenting code
- Comments should explain *why*, not *what*
- Keep comments up-to-date when code changes

```python
# Good - explains why
# Use absolute_sigma=True to treat uncertainties as absolute values,
# not relative weights, which is correct for experimental data
popt, pcov = curve_fit(func, x, y, sigma=uy, absolute_sigma=True)

# Bad - states the obvious
# Call curve_fit function
popt, pcov = curve_fit(func, x, y)
```

### Testing

#### Writing Tests

1. **Location**: Place tests in `tests/` directory
2. **Naming**: Test files should match source files: `test_<module>.py`
3. **Structure**: Use pytest conventions

```python
# tests/test_fitting_functions.py
import numpy as np
import pandas as pd
import pytest
from fitting.fitting_functions import func_lineal, ajlineal


class TestFuncLineal:
    """Tests for func_lineal mathematical function."""
    
    def test_scalar_input(self):
        """Test with scalar input."""
        result = func_lineal(5.0, 2.0)
        assert result == 10.0
    
    def test_array_input(self):
        """Test with array input."""
        t = np.array([1, 2, 3])
        result = func_lineal(t, 2.0)
        expected = np.array([2, 4, 6])
        np.testing.assert_array_equal(result, expected)
    
    @pytest.mark.parametrize("t,m,expected", [
        (0, 5, 0),
        (3, 2, 6),
        (-2, 4, -8),
    ])
    def test_various_inputs(self, t, m, expected):
        """Test with various parameter combinations."""
        assert func_lineal(t, m) == expected


class TestAjlineal:
    """Tests for ajlineal fitting function."""
    
    def test_perfect_linear_fit(self):
        """Test fitting with perfect linear data."""
        x = np.linspace(0, 10, 50)
        y = 3.0 * x  # Perfect linear relationship
        
        data = pd.DataFrame({'x': x, 'y': y})
        
        param_text, y_fitted, equation, r_squared = ajlineal(data, 'x', 'y')
        
        # R² should be nearly 1 for perfect fit
        assert r_squared > 0.9999
        
        # Fitted values should match original data
        np.testing.assert_array_almost_equal(y_fitted, y, decimal=10)
    
    def test_noisy_data(self):
        """Test fitting with noisy data."""
        np.random.seed(42)  # Reproducibility
        x = np.linspace(0, 10, 100)
        y = 2.5 * x + np.random.normal(0, 0.5, 100)
        
        data = pd.DataFrame({'x': x, 'y': y})
        
        param_text, y_fitted, equation, r_squared = ajlineal(data, 'x', 'y')
        
        # Should still get good fit despite noise
        assert r_squared > 0.95
    
    def test_with_uncertainties(self):
        """Test fitting with uncertainty columns."""
        x = np.linspace(0, 10, 50)
        y = 3.0 * x
        
        data = pd.DataFrame({
            'x': x,
            'y': y,
            'ux': np.ones_like(x) * 0.1,
            'uy': np.ones_like(y) * 0.2
        })
        
        param_text, y_fitted, equation, r_squared = ajlineal(data, 'x', 'y')
        
        assert r_squared > 0.99
    
    def test_raises_on_invalid_data(self):
        """Test that appropriate errors are raised for invalid data."""
        with pytest.raises(KeyError):
            # Missing column
            data = pd.DataFrame({'x': [1, 2, 3]})
            ajlineal(data, 'x', 'y')
```

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_fitting_functions.py

# Run specific test
pytest tests/test_fitting_functions.py::TestFuncLineal::test_scalar_input

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run tests in parallel
pytest tests/ -n auto
```

Check coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Adding New Fitting Functions

See [Extending RegressionLab](extending.md) for detailed guide.

Summary:
1. Add function in `src/fitting/functions/` (e.g. `special.py`, `polynomials.py`)
2. Register in `src/config/constants.py` (AVAILABLE_EQUATION_TYPES, EQUATION_FUNCTION_MAP)
3. Add to `src/fitting/fitting_utils.py`
4. Add translations to `src/locales/`
5. Write tests in `tests/test_fitting_functions.py`
6. Update documentation

### Adding Translations

To add a new language:

1. **Create locale file**: `src/locales/<language_code>.json`

```json
{
  "menu": {
    "normal_fitting": "Your translation",
    "multiple_datasets": "Your translation",
    ...
  },
  "dialog": {
    "select_file": "Your translation",
    ...
  },
  ...
}
```

2. **Update i18n.py**: Add language code to `initialize_i18n`

3. **Test thoroughly**: Check all UI elements in both interfaces

4. **Update documentation**: Add language to README and docs

### Documentation

#### Updating Documentation

- Documentation is in `docs/` directory
- Use Markdown format
- Follow existing structure and style
- Include code examples where appropriate
- Add screenshots for UI changes (place in `docs/images/`)

#### Building Documentation

```bash
# Install documentation dependencies
pip install -r sphinx-docs/requirements.txt

# Build HTML documentation
cd sphinx-docs
./build_docs.sh  # Linux/macOS
build_docs.bat   # Windows

# View documentation
./open_docs.sh   # Linux/macOS
open_docs.bat    # Windows
```

## Submitting Changes

### 1. Commit Your Changes

Write clear, descriptive commit messages:

```bash
# Good commit messages
git commit -m "Add exponential decay fitting function"
git commit -m "Fix unicode encoding issue in CSV loader"
git commit -m "Improve error message for missing uncertainty columns"
git commit -m "Update installation instructions for Windows"

# Bad commit messages (too vague)
git commit -m "Fixed stuff"
git commit -m "Update"
git commit -m "WIP"
```

**Commit Message Format**:
```
<type>: <short summary>

<detailed description (optional)>

<issue reference (if applicable)>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example**:
```
feat: Add logistic growth fitting function

Implements sigmoid/logistic growth curve fitting with
three parameters: carrying capacity (L), growth rate (k),
and midpoint (t0).

Closes #42
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the pull request template:
   - **Title**: Clear, concise summary
   - **Description**: What changes were made and why
   - **Testing**: How you tested the changes
   - **Screenshots**: For UI changes
   - **Closes**: Reference any related issues

### Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest tests/`)
- [ ] New tests added for new functionality
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files included (check `.gitignore`)
- [ ] Type hints included
- [ ] Docstrings added for new functions
- [ ] Translations added (if UI changes)
- [ ] CHANGELOG.md updated (for significant changes)

### Review Process

1. **Automated checks**: CI/CD runs tests automatically
2. **Code review**: Maintainer reviews your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, changes are merged
5. **Cleanup**: Delete your branch after merge

## Development Setup

### Recommended Tools

- **IDE**: Visual Studio Code, PyCharm, or your preference
- **Git Client**: Command line, GitKraken, or GitHub Desktop
- **Python Version**: 3.10 or higher
- **Virtual Environment**: Always use virtual environments

### VS Code Setup

Recommended extensions:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- GitLens
- Markdown All in One

Workspace settings (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.rulers": [100],
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}
```

## Project Structure

Understanding the codebase:

```
RegressionLab/
├── src/                          # Source code
│   ├── config/                  # Configuration package (env, theme, paths, constants)
│   ├── i18n.py                  # Internationalization functions
│   ├── main_program.py          # Tkinter main entry point
│   ├── fitting/                 # Curve fitting logic and models
│   ├── frontend/                # Tkinter UI
│   ├── loaders/                 # Data loaders, CSV/Excel importers
│   ├── plotting/                # Visualization and plotting utilities
│   ├── streamlit_app/           # Streamlit web app frontend
│   └── utils/                   # Miscellaneous utilities
├── tests/                       # Automated test suite (pytest)
├── docs/                        # User documentation (Markdown)
├── sphinx-docs/                 # Sphinx documentation sources (reStructuredText)
├── input/                       # Sample datasets for testing/demo
├── output/                      # Generated plots and output files
├── bin/                         # Command line/launcher scripts
├── scripts/                     # Helper scripts (install, setup, maintenance, data prep)
├── install.bat                  # Windows installation script
├── install.sh                   # Linux/macOS installation script
├── setup.bat                    # Windows setup script
├── setup.sh                     # Linux/macOS setup script
├── .env.example                 # Sample environment configuration (dotenv)
├── .gitignore                   # git ignore rules
├── requirements.txt             # Python dependencies (minimal set)
├── requirements-dev.txt         # Developer dependencies (tests, linting, docs)
├── pyproject.toml               # Modern Python project metadata and build config
├── README.md                    # Project overview/readme
├── CHANGELOG.md                 # Project changelog
└── LICENSE                      # License file
```

## Communication

### Asking Questions

- **GitHub Discussions**: For general questions and ideas
- **GitHub Issues**: For bug reports and feature requests
- **Email**: For private inquiries

### Reporting Bugs

Use the GitHub issue template and include:

1. **Title**: Clear, specific description
2. **Version**: RegressionLab version
3. **Environment**: OS, Python version
4. **Steps to reproduce**: Exact steps
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: Full traceback
8. **Sample data**: If possible
9. **Screenshots**: For UI issues

### Suggesting Features

Use the GitHub feature request template:

1. **Problem description**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other solutions considered
4. **Additional context**: Examples, mockups, etc.

## Code of Conduct

### Our Standards

- **Be respectful**: Treat everyone with respect
- **Be constructive**: Provide helpful feedback
- **Be patient**: Everyone is learning
- **Be professional**: Keep discussions on-topic

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Trolling or inflammatory comments
- Publishing private information
- Other unprofessional conduct

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report issues to: alejandro.mata.ali@gmail.com

## License

By contributing to RegressionLab, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Documentation credits

Thank you for contributing to RegressionLab! 🎉

---

*Questions about contributing? Open a GitHub Discussion or email alejandro.mata.ali@gmail.com*
