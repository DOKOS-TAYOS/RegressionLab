## Third-Party Licenses for RegressionLab

RegressionLab is distributed under the **MIT** license. See [LICENSE](LICENSE).

This file summarizes the main third-party dependencies used by the project in the current Electron desktop branch. It is based on:

- `requirements.txt`
- `requirements-dev.txt`
- `desktop/package.json`
- `desktop/package-lock.json`

For redistributed source archives, binaries, or installers, keep this file together with the main project license and any upstream notices required by bundled software.

---

## 1. Python Runtime Dependencies


| Library         | Version Range  | License                                         |
| --------------- | -------------- | ----------------------------------------------- |
| `numpy`         | `>=2.0,<3.0`   | BSD-3-Clause                                    |
| `matplotlib`    | `>=3.10,<4.0`  | Matplotlib License (BSD-style / PSF-compatible) |
| `scipy`         | `>=1.17,<2.0`  | BSD-3-Clause                                    |
| `pandas`        | `>=2.3,<3.0`   | BSD-3-Clause                                    |
| `openpyxl`      | `>=3.1,<4.0`   | MIT                                             |
| `Pillow`        | `>=10.0,<11.0` | HPND / PIL Software License                     |
| `python-dotenv` | `>=1.0,<2.0`   | BSD-3-Clause                                    |
| `colorama`      | `>=0.4,<1.0`   | BSD-3-Clause                                    |
| `PyYAML`        | `>=6.0,<7.0`   | MIT                                             |
| `streamlit`     | `>=1.31,<2.0`  | Apache-2.0                                      |
| `fastapi`       | `>=0.116,<1.0` | MIT                                             |
| `uvicorn`       | `>=0.35,<1.0`  | BSD-3-Clause                                    |


---

## 2. Desktop Frontend Runtime Dependencies

Locked versions below come from `desktop/package-lock.json`.


| Library              | Locked Version | License |
| -------------------- | -------------- | ------- |
| `electron`           | `35.7.5`       | MIT     |
| `plotly.js-dist-min` | `3.4.0`        | MIT     |
| `react`              | `19.2.4`       | MIT     |
| `react-dom`          | `19.2.4`       | MIT     |
| `react-plotly.js`    | `2.6.0`        | MIT     |
| `react-router-dom`   | `7.13.1`       | MIT     |
| `zustand`            | `5.0.11`       | MIT     |


---

## 3. Development Dependencies

### Python development tooling


| Library      | Version Range  | License      |
| ------------ | -------------- | ------------ |
| `pytest`     | `>=7.0,<8.0`   | MIT          |
| `pytest-cov` | `>=4.0,<5.0`   | MIT          |
| `httpx`      | `>=0.28,<1.0`  | BSD-3-Clause |
| `black`      | `>=23.0,<24.0` | MIT          |
| `ruff`       | `>=0.1,<1.0`   | MIT          |
| `mypy`       | `>=1.0,<2.0`   | MIT          |
| `pre-commit` | `>=3.0,<4.0`   | MIT          |


### Desktop frontend development tooling


| Library                     | Locked Version | License    |
| --------------------------- | -------------- | ---------- |
| `@playwright/test`          | `1.58.2`       | Apache-2.0 |
| `@testing-library/jest-dom` | `6.9.1`        | MIT        |
| `@testing-library/react`    | `16.3.2`       | MIT        |
| `@types/node`               | `22.19.15`     | MIT        |
| `@types/react`              | `19.2.14`      | MIT        |
| `@types/react-dom`          | `19.2.3`       | MIT        |
| `@vitejs/plugin-react`      | `4.7.0`        | MIT        |
| `concurrently`              | `9.2.1`        | MIT        |
| `jsdom`                     | `26.1.0`       | MIT        |
| `typescript`                | `5.9.3`        | Apache-2.0 |
| `vite`                      | `6.4.1`        | MIT        |
| `vitest`                    | `3.2.4`        | MIT        |
| `wait-on`                   | `8.0.5`        | MIT        |


---

## 4. Documentation Dependencies


| Library                    | Version Range | License      |
| -------------------------- | ------------- | ------------ |
| `sphinx`                   | `>=9.0.0`     | BSD-2-Clause |
| `sphinx-rtd-theme`         | `>=3.0.0`     | MIT          |
| `myst-parser`              | `>=5.0.0`     | MIT          |
| `sphinx-autodoc-typehints` | `>=3.0.0`     | MIT          |
| `linkify-it-py`            | `>=2.0.0`     | MIT          |


---

## 5. Compliance Notes

### Permissive licenses

Most project dependencies use permissive licenses such as:

- MIT
- BSD-2-Clause / BSD-3-Clause
- Apache-2.0
- HPND / PIL-style terms

These are generally compatible with RegressionLab's MIT license.

### Electron distributions

Electron itself is MIT-licensed, but packaged Electron apps also bundle Chromium/Node components with their own notices.

If you later ship installers or packaged desktop binaries, include:

1. the main [LICENSE](LICENSE)
2. this `THIRD_PARTY_LICENSES.md`
3. any upstream notices required by the packaged Electron runtime

### Transitive dependencies

This document summarizes the main direct dependencies and the versions currently locked in the desktop workspace.

Transitive dependencies installed through `pip` or `npm` may add further notices. For packaged distributions, review:

- `desktop/package-lock.json`
- installed `node_modules/*/package.json`
- Python package metadata in the active environment

---

## 6. Redistribution Checklist

When redistributing RegressionLab:

1. include [LICENSE](LICENSE)
2. include `THIRD_PARTY_LICENSES.md`
3. preserve any required upstream notices
4. recheck this file when Python or desktop frontend dependencies change

