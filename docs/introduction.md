# Introduction to RegressionLab

## 🎯 What is RegressionLab?

**RegressionLab** is a comprehensive curve fitting application designed to help you analyze experimental data and find the mathematical relationships within your datasets. Whether you're a student learning about data analysis, a researcher processing experimental results, or an engineer validating models, RegressionLab provides the tools you need.

### For Everyone

At its core, RegressionLab helps you answer a simple question: **"What mathematical equation best describes my data?"**

Imagine you've collected measurements from an experiment - maybe you're measuring how the temperature of water changes over time, or how the speed of a car varies with the force applied. RegressionLab takes your data points and tries different mathematical formulas to find the one that best fits your observations. It then shows you:

- The equation that describes your data
- A graph comparing your actual measurements with the predicted values
- How accurate the fit is (using statistical measures)

You don't need to be a programmer or mathematician to use RegressionLab - the interface is designed to be intuitive and user-friendly.

### For Technical Users

RegressionLab is a Python-based scientific application that implements curve fitting using non-linear least squares optimization (via SciPy's `curve_fit`). It provides:

- **Multiple fitting algorithms**: Linear, polynomial, trigonometric, logarithmic, inverse, hyperbolic, and custom functions
- **Statistical analysis**: Automatic calculation of fit quality metrics (R²), parameter uncertainties, and covariance matrices
- **Flexible data formats**: Support for CSV and Excel files with automatic uncertainty column detection
- **Batch processing**: Fit multiple datasets or equations simultaneously
- **Extensible architecture**: Easy to add new fitting functions or replace the optimization backend

## 🌟 Key Benefits

### 1. **Dual Interface**
Choose the interface that works best for you:
- **Web version** (Streamlit): Access from any browser, no installation required
- **Desktop version** (Tkinter): Full-featured native application with advanced options

### 2. **Multiple Operation Modes**
RegressionLab offers four different fitting modes to match your workflow:

- **Normal Fitting**: Fit one equation to one dataset (with optional loop mode for iterative refinement)
- **Multiple Datasets**: Apply the same equation to multiple datasets simultaneously
- **Checker Mode**: Test multiple equations on the same dataset to find the best fit
- **Total Fitting**: Automatically try all available equations on your data

### 3. **Wide Range of Fitting Functions**
Built-in support for:
- Linear functions (with and without intercept)
- Polynomial functions (quadratic, quartic, complete polynomials)
- Trigonometric functions (sine, cosine, with phase shifts)
- Hyperbolic functions (sinh, cosh)
- Logarithmic functions
- Inverse functions (1/x, 1/x²)
- **Custom formulas**: Define your own mathematical expressions

### 4. **Professional Visualization**
- High-quality publication-ready plots
- Error bars for measurement uncertainties
- Customizable plot styles and themes
- Automatic equation and parameter display
- Export plots as PNG images

### 5. **Uncertainty Handling**
Automatic detection and visualization of measurement uncertainties:
- Supports uncertainty columns with `u` prefix (e.g., `ux`, `uy`)
- Weighted fitting based on uncertainties
- Error bar visualization

### 6. **Batch Processing**
Save time by:
- Fitting multiple datasets with one click
- Testing all available equations automatically
- Loop mode for iterative data refinement

### 7. **Internationalization**
Full support for multiple languages:
- Spanish (es) – default
- English (en)
- German (de)
- Easy to add more languages via JSON files in `src/locales/`

### 8. **Highly Configurable**
Customize every aspect through the `.env` file:
- UI colors and themes
- Plot styles and fonts
- Input/output directories
- Logging levels
- And much more

### 9. **Extensible and Open Source**
- MIT License - free for academic and commercial use
- Well-documented codebase
- Easy to add new fitting functions
- Modular architecture for customization

### 10. **Cross-Platform**
Works on:
- Windows
- macOS
- Linux

## 🌐 Getting RegressionLab

### Option 1: Web Version (Easiest)

Access RegressionLab instantly through your web browser:

**[https://regressionlab.streamlit.app/](https://regressionlab.streamlit.app/)**

No installation required! Just:
1. Open the link
2. Upload your data file
3. Select your fitting options
4. Download the results

> **Note**: If the app is sleeping, click "Start" and wait a moment for it to wake up.

### Option 2: Desktop Version (Most Features)

Install RegressionLab on your computer for:
- Faster performance
- Offline use
- Advanced customization options
- Access to all features

See the [Installation Guide](installation.md) for detailed instructions.

## 📊 Use Cases

### Academic Research
- Analyzing experimental data from physics, chemistry, or biology labs
- Validating theoretical models with empirical data
- Teaching data analysis and curve fitting concepts

### Engineering
- Calibration curve generation
- System identification and modeling
- Quality control and process optimization

### Data Science
- Exploratory data analysis
- Feature engineering
- Model validation

### Education
- Learning about different mathematical functions
- Understanding least squares fitting
- Visualizing how equations relate to data

## 🎓 What You'll Learn

By using RegressionLab, you'll gain experience with:
- **Curve fitting techniques**: Understanding how to match mathematical models to data
- **Statistical analysis**: Interpreting R² values and parameter uncertainties
- **Data visualization**: Creating publication-quality plots
- **Scientific computing**: Working with numerical analysis tools
- **Best practices**: Proper data formatting and uncertainty handling

## 🚀 Next Steps

Ready to get started?

1. **Install RegressionLab**: Follow the [Installation Guide](installation.md)
2. **Learn the basics**: Read the [User Guide](usage.md)
3. **Customize**: Configure your preferences in the [Configuration Guide](configuration.md)
4. **Explore**: Try different fitting modes with your data

Or jump straight to the web version and start fitting curves immediately!

---

*RegressionLab: Making curve fitting accessible to everyone.*
