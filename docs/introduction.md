# Introduction to RegressionLab

## 🎯 What is RegressionLab?

**RegressionLab** is a comprehensive curve fitting application designed to help you analyze experimental data and find the mathematical relationships within your datasets. Whether you're a student learning about data analysis, a researcher processing experimental results, or an engineer validating models, RegressionLab provides the tools you need.

![RegressionLab Main Interface](../images/en_documentation/tkinter_docs/main.png)


### For Everyone

At its core, RegressionLab helps you answer a simple question: **"What mathematical equation best describes my data?"**

Imagine you've collected measurements from an experiment - maybe you're measuring how the temperature of water changes over time, or how the speed of a car varies with the force applied. RegressionLab takes your data points and tries different mathematical formulas to find the one that best fits your observations. It then shows you:

- The equation that describes your data.
- A graph comparing your actual measurements with the predicted values.
- How accurate the fit is (using statistical measures).

You don't need to be a programmer or mathematician to use RegressionLab - the interface is designed to be intuitive and user-friendly.

### For Technical Users

RegressionLab is a Python-based scientific application that implements curve fitting using non-linear least squares optimization (via SciPy's `curve_fit`). It provides:

- **Multiple fitting functions**: Linear, polynomial, trigonometric (including tangent), logarithmic, exponential, inverse, hyperbolic, Gaussian, sigmoid, and custom formulas.
- **Multidimensional regression**: Custom formulas can use 2 or more independent variables. With 2 independent variables, an interactive 3D plot is shown; with more than 2, a residuals plot is displayed.
- **Prediction window**: In the desktop version, a "Prediction" button in the result window lets you evaluate the fitted function at user-specified inputs, with uncertainty propagation when parameter covariance is available.
- **Statistical analysis**: Automatic calculation of R², RMSE, chi-squared, reduced chi-squared, degrees of freedom, parameter uncertainties (from the fit covariance), and 95% confidence intervals for parameters.
- **Flexible data formats**: Support for CSV, TXT (whitespace or tab-separated), and Excel (.xlsx) files with automatic uncertainty column detection.
- **Batch processing**: Fit multiple datasets or equations simultaneously.
- **Extensible architecture**: Easy to add new fitting functions or replace the optimization backend.

## 🌟 Key Benefits

### 1. **Dual Interface**
Choose the interface that works best for you:
- **Web version** (Streamlit): Access from any browser, no installation required.
- **Desktop version** (Tkinter): Full-featured native application with advanced options.

### 2. **Interfaces**
- **Tkinter (desktop)**: Main menu with mode buttons (Normal Fitting, Multiple Datasets, Checker Fitting, Total Fitting, Watch Data), **Information** (help with collapsible sections), **Configure** (edit .env options in a dialog; saving restarts the app), and Exit.
- **Streamlit (web)**: Sidebar for language and mode; main area for upload, variables, equation, and results. Configuration is done via the `.env` file (no in-app config dialog).

### 3. **Multiple Operation Modes**
RegressionLab offers five operation modes so you can match the workflow to your task:

- **Normal fitting**: Fits one equation to one dataset. Ideal when you already know the model and want a single, precise fit. Optionally use **loop mode** (Tkinter) or **loop fitting** (Streamlit: fit another file with the same equation without changing mode) for iterative refits.
- **Fit multiple datasets**: Applies the *same* equation to several datasets at once. Use it when you want to test the same hypothesis on different data series (e.g., the same experiment on different days) and compare results systematically.
- **Fit multiple functions**: Tests *different* equations on the *same* dataset. Lets you explore which model (e.g., linear vs. quadratic vs. exponential) best describes your data.
- **Fit all functions**: Applies every available equation to one dataset. Use it for hypothesis exploration when you want to see which built-in or custom function fits best in one go.
- **View data**: Inspect data from a file (table and pair plots) without performing any fitting.

### 4. **Wide Range of Fitting Functions**
Built-in support for:
- Linear functions (with and without intercept).
- Polynomial functions (quadratic, quartic, complete polynomials).
- Trigonometric functions (sine, cosine, tangent, with phase shifts).
- Hyperbolic functions (sinh, cosh).
- Logarithmic and exponential functions.
- Inverse functions (1/x, 1/x²).
- Additional models: Gaussian, sigmoid (logistic), square pulse, Hermite polynomials.
- **Custom formulas**: Define your own mathematical expressions. Custom formulas can have multiple independent variables (e.g. `x_0`, `x_1`) for multidimensional regression.

### 5. **Professional Visualization**
- High-quality publication-ready plots.
- Error bars for measurement uncertainties.
- Customizable plot styles and themes.
- Automatic equation and parameter display.
- Export plots as PNG, JPG, or PDF (configurable).

### 6. **Uncertainty Handling**
Automatic detection and visualization of measurement uncertainties:
- Supports uncertainty columns with `u` prefix (e.g., `ux`, `uy`).
- Weighted fitting based on uncertainties.
- Error bar visualization.

### 7. **Multidimensional Regression and Predictions**
- **Multidimensional fitting**: Use custom formulas with 2 or more independent variables. With 2 variables you get an interactive 3D surface plot; with 3+ you get a residuals plot.
- **Prediction window** (desktop): Evaluate the fitted function at any point. Enter values for each independent variable and see the predicted value with propagated uncertainty when available.

### 8. **Batch Processing**
Save time by:
- Fitting multiple datasets with one click (same equation, many files).
- Testing all available equations on one dataset automatically (fit all functions).
- Loop mode for iterative data refinement (add data, refit, repeat without reconfiguring).

### 9. **Internationalization**
Full support for multiple languages:
- Spanish (es) – default.
- English (en).
- German (de).
- Easy to add more languages via JSON files in `src/locales/`.

### 10. **Highly Configurable**
Customize through the **Configure** dialog (Tkinter) or the `.env` file:
- **Language**: Spanish, English, German.
- **UI (Tkinter)**: Colors, fonts, padding, button sizes, data-preview text style.
- **Plots**: Size, DPI, line/marker style, colors, title on/off.
- **Fonts in plots**: Family, title/axis/tick size and style.
- **Paths**: Input/output directories, filename template, plot format (PNG/JPG/PDF).
- **Links**: Donations URL (optional).
- **Logging**: Level, file path, console output.

### 11. **Extensible and Open Source**
- MIT License - free for academic and commercial use.
- Well-documented codebase.
- Easy to add new fitting functions.
- Modular architecture for customization.

### 12. **Cross-Platform**
Works on:
- Windows.
- macOS.
- Linux.

## 🌐 Getting RegressionLab

### Option 1: Web Version (Easiest)

Access RegressionLab instantly through your web browser:

**[https://regressionlab.streamlit.app/](https://regressionlab.streamlit.app/)**

No installation required! Just:
1. Open the link.
2. Upload your data file.
3. Select your fitting options.
4. Download the results.

> **Note**: If the app is sleeping, click "Start" and wait a moment for it to wake up.

### Option 2: Desktop Version (Most Features)

Install RegressionLab on your computer for:
- Faster performance.
- Offline use.
- Advanced customization options.
- Access to all features.

See the [Installation Guide](installation.md) for detailed instructions.

## 📊 Use Cases

### Academic Research
- Analyzing experimental data from physics, chemistry, or biology labs.
- Validating theoretical models with empirical data.
- Teaching data analysis and curve fitting concepts.

### Engineering
- Calibration curve generation.
- System identification and modeling.
- Quality control and process optimization.

### Data Science
- Exploratory data analysis.
- Feature engineering.
- Model validation.

### Education
- Learning about different mathematical functions.
- Understanding least squares fitting.
- Visualizing how equations relate to data.

## 🎓 What You'll Learn

By using RegressionLab, you'll gain experience with:
- **Curve fitting techniques**: Understanding how to match mathematical models to data.
- **Statistical analysis**: Interpreting R², RMSE, chi-squared, and parameter uncertainties.
- **Data visualization**: Creating publication-quality plots.
- **Scientific computing**: Working with numerical analysis tools.
- **Best practices**: Proper data formatting and uncertainty handling.

## 🚀 Next Steps

Ready to get started?

1. **Install RegressionLab**: Follow the [Installation Guide](installation.md).
2. **Learn the basics**: Read the [User Guide](usage.md).
3. **Customize**: Configure your preferences in the [Configuration Guide](configuration.md).
4. **Explore**: Try different fitting modes with your data.

Or jump straight to the web version and start fitting curves immediately!

---

*RegressionLab: Making curve fitting accessible to everyone.*
