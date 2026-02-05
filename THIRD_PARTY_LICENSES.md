### Third-Party Licenses for RegressionLab

RegressionLab (`regressionlab`) se distribuye bajo licencia **MIT** (ver `LICENSE` en la raíz del proyecto).

Este documento lista las bibliotecas de terceros utilizadas y sus licencias, para facilitar el cumplimiento
de sus términos cuando redistribuyas RegressionLab (como código fuente, paquete instalable, binario o instalador).

> Nota: Esta lista se basa en las dependencias declaradas en `pyproject.toml`, `requirements.txt`
> y `requirements-dev.txt`. Si añades o eliminas dependencias, recuerda actualizar este archivo.

---

### 1. Dependencias de ejecución (runtime)

Estas bibliotecas se usan en tiempo de ejecución de la aplicación.

| Biblioteca       | Rango de versión           | Tipo de licencia                             |
|------------------|----------------------------|----------------------------------------------|
| **numpy**        | `>=2.0,<3.0`               | BSD-3-Clause                                 |
| **matplotlib**   | `>=3.10,<4.0`              | Licencia Matplotlib (BSD-style + PSF)        |
| **scipy**        | `>=1.17,<2.0`              | BSD-3-Clause                                 |
| **pandas**       | `>=2.3,<3.0`               | BSD-3-Clause                                 |
| **openpyxl**     | `>=3.1,<4.0`               | MIT                                          |
| **python-dotenv**| `>=1.0,<2.0`               | BSD-3-Clause                                 |
| **colorama**     | `>=0.4,<1.0`               | BSD-3-Clause                                 |
| **Pillow**       | `>=10.0,<11.0`             | PIL License / HPND (permisiva, tipo MIT)     |
| **streamlit**    | `>=1.31,<2.0`              | Apache License 2.0                           |

---

### 2. Dependencias de documentación

Estas bibliotecas se usan para generar documentación (`docs`, `sphinx-docs`, etc.).

| Biblioteca                 | Rango de versión           | Tipo de licencia  |
|---------------------------|----------------------------|-------------------|
| **sphinx**                | `>=9.0.0`                  | BSD-2-Clause      |
| **sphinx-rtd-theme**      | `>=3.0.0`                  | MIT               |
| **myst-parser**           | `>=5.0.0`                  | MIT               |
| **sphinx-autodoc-typehints** | `>=3.0.0`              | MIT               |
| **linkify-it-py**         | `>=2.0.0`                  | MIT               |

---

### 3. Dependencias de desarrollo y tooling

Estas bibliotecas se usan sólo para desarrollo (tests, formateo, linting, hooks, etc.) y normalmente
no se distribuyen en binarios finales, aunque sí pueden estar presentes si publicas tu código fuente.

| Biblioteca       | Rango de versión           | Tipo de licencia  |
|------------------|----------------------------|-------------------|
| **pytest**       | `>=7.0` / `>=7.0,<8.0`     | MIT               |
| **pytest-cov**   | `>=4.0` / `>=4.0,<5.0`     | MIT               |
| **black**        | `>=23.0` / `>=23.0,<24.0`  | MIT               |
| **flake8**       | `>=6.0`                    | MIT               |
| **ruff**         | `>=0.1,<1.0`               | MIT               |
| **mypy**         | `>=1.0` / `>=1.0,<2.0`     | MIT               |
| **pre-commit**   | `>=3.0,<4.0`               | MIT               |

---

### 4. Notas de cumplimiento de licencias

- **MIT / BSD / PIL (HPND)**  
  - Permiten uso comercial, modificación, integración y redistribución, incluido en software propietario.  
  - Obligación principal: conservar el aviso de copyright y el texto
    de la licencia en copias sustanciales del software.

- **Apache License 2.0 (Streamlit)**  
  - Permite igualmente uso comercial, modificación, integración y redistribución.  
  - Añade una concesión explícita de patentes y requisitos adicionales de atribución.  
  - Al redistribuir RegressionLab, es recomendable:
    - Incluir el texto completo de la Apache License 2.0 (por ejemplo, en un fichero de licencias agregado).  
    - Incluir el fichero `NOTICE` de Streamlit si se requiere, sin modificar su contenido.

- **Buenas prácticas recomendadas en tus distribuciones**  
  - Mantener tu fichero `LICENSE` (MIT) en todos los paquetes / instaladores.  
  - Incluir este `THIRD_PARTY_LICENSES.md` o equivalente junto con tus binarios o código fuente.  
  - Si copias o modificas directamente código fuente de alguna de estas bibliotecas y lo redistribuyes,
    conservar sus cabeceras de licencia y añadir, si procede, una nota del tipo
    “Modificado por RegressionLab”.

