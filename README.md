<div align="center">

![RegressionLab Logo](images/RegressionLab_logo.png)

# RegressionLab

**A powerful and user-friendly curve fitting application for scientists, engineers, students, and data analysts**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.2-blue.svg?style=for-the-badge)](https://github.com/DOKOS-TAYOS/RegressionLab)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://regressionlab.streamlit.app/)
[![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)

[🌐 **Try Online**](https://regressionlab.streamlit.app/) • [📖 **Documentation**](docs/index.md) • [🐛 **Report Bug**](https://github.com/DOKOS-TAYOS/RegressionLab/issues) • [💡 **Request Feature**](https://github.com/DOKOS-TAYOS/RegressionLab/issues)

</div>

---

**RegressionLab** is a comprehensive curve fitting application that enables you to perform advanced curve fitting operations using multiple mathematical models with an intuitive interface. Whether you're analyzing experimental data, calibrating instruments, or exploring mathematical relationships, RegressionLab provides the tools you need.

## ✨ Features

<div align="center">

| 🖥️ **Dual Interface** | 📊 **Advanced Fitting** | 🎨 **Professional Plots** |
|:---:|:---:|:---:|
| Web (Streamlit) & Desktop (Tkinter) | Multiple mathematical models | Publication-ready visualizations |

</div>

### 🚀 Key Capabilities

- **🌐 Dual Interface**: Choose between web version (Streamlit) for instant access or desktop version (Tkinter) for offline use
- **📈 Multiple Fitting Functions**: Linear, polynomial, trigonometric, logarithmic, inverse, hyperbolic, and custom functions
- **📐 Multidimensional Fitting**: Support for regression with 2+ independent variables via custom formulas; 3D interactive plot for 2 variables, residuals plot for 3+
- **🔮 Prediction Window**: Evaluate fitted functions at user-specified inputs with uncertainty propagation (desktop version)
- **⚙️ Multiple Operation Modes**: Normal fitting, multiple datasets, checker mode, total fitting, and view data (with transform, clean, save)
- **📊 Professional Visualization**: Publication-ready plots with error bars and customizable styles
- **📏 Uncertainty Handling**: Automatic detection and visualization of measurement uncertainties
- **🔄 Batch Processing**: Fit multiple datasets or test all equations simultaneously
- **🌍 Internationalization**: Full support for English, Spanish, and German (easily extensible)
- **⚙️ Highly Configurable**: Customize every aspect through the `.env` file


## 📚 Documentation

<div align="center">

📖 **Complete documentation is available in the [`docs/`](docs/) directory**

</div>

| 📄 Document | 📝 Description |
|:---|:---|
| **[Getting Started](docs/index.md)** | Main documentation index |
| **[Introduction](docs/introduction.md)** | Project overview and benefits |
| **[Installation Guide](docs/installation.md)** | Detailed installation instructions |
| **[User Guide](docs/usage.md)** | How to use RegressionLab |
| **[Configuration](docs/configuration.md)** | Configuration options |
| **[API Documentation](docs/api/index.md)** | Technical reference for developers |

## 🚀 Quick Start

### 🌐 Web Version (Easiest)

<div align="center">

**[👉 Try RegressionLab Online Now 👈](https://regressionlab.streamlit.app/)**

*No installation required!*

</div>

### 💻 Desktop Installation

**Quick Installation (Recommended):**

**Windows:**
```batch
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**Manual Installation:**

1. Clone the repository:
   ```bash
   git clone https://github.com/DOKOS-TAYOS/RegressionLab.git
   cd RegressionLab
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   # Desktop version (Tkinter)
   python src/main_program.py
   # Or use the launcher: bin\run.bat (Windows) / ./bin/run.sh (Linux/macOS)

   # Web version (Streamlit)
   streamlit run src/streamlit_app/app.py
   # Or use: bin\run_streamlit.bat (Windows) / ./bin/run_streamlit.sh (Linux/macOS)
   ```


## 🎯 Use Cases

<div align="center">

| 🎓 **Academic Research** | 🔧 **Engineering** | 📊 **Data Science** | 📚 **Education** |
|:---:|:---:|:---:|:---:|
| Analyzing experimental data from physics, chemistry, or biology labs | Calibration curve generation, system identification, and modeling | Exploratory data analysis and model validation | Learning about mathematical functions and curve fitting concepts |

</div>

## 🛠️ Requirements

- Python 3.12 or higher (3.13 supported)
- Windows 10/11, macOS 10.14+, or Linux
- 4 GB RAM minimum (8 GB recommended)

## 📦 Dependencies

### Core Dependencies

| Package | Version | Purpose |
|:---|:---:|:---|
| **NumPy** | >= 2.0 | Numerical computations |
| **Matplotlib** | >= 3.10 | Plotting and visualization |
| **SciPy** | >= 1.17 | Scientific computing and curve fitting |
| **Pandas** | >= 2.3 | Data manipulation |
| **OpenPyXL** | >= 3.1 | Excel file handling |
| **Pillow** | >= 10.0 | Image handling (GUI, logos) |
| **Python-dotenv** | >= 1.0 | Environment configuration |
| **Colorama** | >= 0.4 | Terminal colors |
| **PyYAML** | >= 6.0 | YAML config (equations) |
| **Streamlit** | >= 1.31 | Web interface |

### Optional

- **Tkinter** – Desktop interface (usually included with Python)

## 🔧 Configuration

RegressionLab is highly configurable through the `.env` file. See the [Configuration Guide](docs/configuration.md) for all available options.

Copy `.env.example` to `.env` and customize:
```bash
cp .env.example .env
```

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guidelines](docs/contributing.md) for details on:
- Development setup
- Code standards
- Pull request process

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

For information about third-party libraries and their licenses, see
`THIRD_PARTY_LICENSES.md`.

## 👨‍💻 Author

<div align="center">

**Alejandro Mata Ali**

[📧 Email](mailto:alejandro.mata.ali@gmail.com) • [🐙 GitHub](https://github.com/DOKOS-TAYOS)

</div>

## 🔗 Links

<div align="center">

[🌐 Web Application](https://regressionlab.streamlit.app/) • [📦 GitHub Repository](https://github.com/DOKOS-TAYOS/RegressionLab) • [🐛 Issue Tracker](https://github.com/DOKOS-TAYOS/RegressionLab/issues)

</div>

## 💡 Need Help?

1. Check the [User Guide](docs/usage.md) for basic usage.
2. Review the [Troubleshooting Guide](docs/troubleshooting.md) for common issues.
3. Consult the [API Documentation](docs/api/index.md) for technical details.
4. Open an issue on GitHub.

---

<div align="center">

**Version**: 1.1.2 • **Last Updated**: February 2026

Made with ❤️ by [Alejandro Mata Ali](https://github.com/DOKOS-TAYOS)

[![GitHub stars](https://img.shields.io/github/stars/DOKOS-TAYOS/RegressionLab?style=social)](https://github.com/DOKOS-TAYOS/RegressionLab)
[![GitHub forks](https://img.shields.io/github/forks/DOKOS-TAYOS/RegressionLab?style=social)](https://github.com/DOKOS-TAYOS/RegressionLab)

</div>
