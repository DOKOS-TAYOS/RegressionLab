### Third-Party Licenses for RegressionLab

RegressionLab (`regressionlab`) is distributed under the **MIT** license (see `LICENSE` in the project root).

This document lists the third-party libraries used and their licenses, to facilitate compliance with their terms when redistributing RegressionLab (as source code, installable package, binary, or installer).

> Note: This list is based on the dependencies declared in `pyproject.toml`, `requirements.txt`
> and `requirements-dev.txt`. If you add or remove dependencies, remember to update this file.

---

### 1. Runtime Dependencies

These libraries are used at application runtime.

| Library       | Version Range           | License Type                             |
|------------------|----------------------------|----------------------------------------------|
| **numpy**        | `>=2.0,<3.0`               | BSD-3-Clause                                 |
| **matplotlib**   | `>=3.10,<4.0`              | Matplotlib License (BSD-style + PSF)        |
| **scipy**        | `>=1.17,<2.0`              | BSD-3-Clause                                 |
| **pandas**       | `>=2.3,<3.0`               | BSD-3-Clause                                 |
| **openpyxl**     | `>=3.1,<4.0`               | MIT                                          |
| **python-dotenv**| `>=1.0,<2.0`               | BSD-3-Clause                                 |
| **colorama**     | `>=0.4,<1.0`               | BSD-3-Clause                                 |
| **PyYAML**       | `>=6.0,<7.0`               | MIT                                          |
| **Pillow**       | `>=10.0,<11.0`             | PIL License / HPND (permissive, MIT-like)     |
| **streamlit**    | `>=1.31,<2.0`              | Apache License 2.0                           |

---

### 2. Documentation Dependencies

These libraries are used to generate documentation (`docs`, `sphinx-docs`, etc.).

| Library                 | Version Range           | License Type  |
|---------------------------|----------------------------|-------------------|
| **sphinx**                | `>=9.0.0`                  | BSD-2-Clause      |
| **sphinx-rtd-theme**      | `>=3.0.0`                  | MIT               |
| **myst-parser**           | `>=5.0.0`                  | MIT               |
| **sphinx-autodoc-typehints** | `>=3.0.0`              | MIT               |
| **linkify-it-py**         | `>=2.0.0`                  | MIT               |

---

### 3. Development and Tooling Dependencies

These libraries are used only for development (tests, formatting, linting, hooks, etc.) and normally
are not distributed in final binaries, although they may be present if you publish your source code.

| Library       | Version Range           | License Type  |
|------------------|----------------------------|-------------------|
| **pytest**       | `>=7.0` / `>=7.0,<8.0`     | MIT               |
| **pytest-cov**   | `>=4.0` / `>=4.0,<5.0`     | MIT               |
| **black**        | `>=23.0` / `>=23.0,<24.0`  | MIT               |
| **flake8**       | `>=6.0`                    | MIT               |
| **ruff**         | `>=0.1,<1.0`               | MIT               |
| **mypy**         | `>=1.0` / `>=1.0,<2.0`     | MIT               |
| **pre-commit**   | `>=3.0,<4.0`               | MIT               |

---

### 4. Full License Texts (Selected)

The following third-party components are used for YAML configuration (e.g. `equations.yaml`). Full license text is included for compliance when redistributing.

#### PyYAML (MIT)

PyYAML is used for loading equation and configuration files in YAML format.

```
Copyright (c) 2017-2021 Ingy döt Net
Copyright (c) 2006-2016 Kirill Simonov

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

For the full, up-to-date license and list of all third-party licenses, see the
respective project repositories (e.g. <https://github.com/yaml/pyyaml> for PyYAML).

---

### 5. License Compliance Notes

- **MIT / BSD / PIL (HPND)**  
  - Allow commercial use, modification, integration, and redistribution, including in proprietary software.  
  - Main requirement: preserve the copyright notice and license text
    in substantial copies of the software.

- **Apache License 2.0 (Streamlit)**  
  - Also allows commercial use, modification, integration, and redistribution.  
  - Adds an explicit patent grant and additional attribution requirements.  
  - When redistributing RegressionLab, it is recommended to:
    - Include the full text of the Apache License 2.0 (for example, in an aggregated licenses file).  
    - Include Streamlit's `NOTICE` file if required, without modifying its content.

- **Recommended Best Practices for Your Distributions**  
  - Keep your `LICENSE` (MIT) file in all packages / installers.  
  - Include this `THIRD_PARTY_LICENSES.md` or equivalent along with your binaries or source code.  
  - If you copy or directly modify source code from any of these libraries and redistribute it,
    preserve their license headers and add, if applicable, a note such as
    "Modified by RegressionLab".
