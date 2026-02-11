# User Guide

This guide explains how to use RegressionLab to fit curves to your data. Whether you're using the web version or the desktop version, this guide will help you get started.

## Overview

RegressionLab provides two interfaces for curve fitting:

- **Web Version (Streamlit)**: Browser-based, easy to use, accessible from anywhere. The sidebar lets you choose language and operation mode; the main area handles file upload, variable and equation selection, and results. Configuration is done by editing the `.env` file (no in-app config dialog).

- **Desktop Version (Tkinter)**: Native application with full features and advanced options. The main menu offers mode buttons (Normal Fitting, Multiple Datasets, Checker Fitting, Total Fitting, Watch Data), **Information** (help with collapsible sections and optional Donations link), **Configure** (edit .env options in a dialog; saving restarts the app), and Exit.

Both versions share the same core functionality but have different user interfaces optimized for their platform.

## Choosing Your Version

### Use the Web Version (Streamlit) if:
- You want quick access without installation.
- You're working from different computers.
- You prefer a modern, streamlined interface.
- You're new to curve fitting.
- You need to share the tool with others easily.

### Use the Desktop Version (Tkinter) if:
- You need offline access.
- You want faster performance with large datasets.
- You prefer a traditional desktop application.
- You need advanced customization options.
- You're working with sensitive data that can't be uploaded.

## Getting Started

### Web Version (Streamlit)

#### Option 1: Online (Recommended for Quick Start)

1. **Access the Application**
   - Open your web browser.
   - Navigate to: [https://regressionlab.streamlit.app/](https://regressionlab.streamlit.app/).
   - If the app is sleeping, click "Start" and wait a moment for it to wake up.

2. **Upload Your Data** (or choose "View Data" in the sidebar to only inspect data without fitting)
   - Click "Browse files" or drag and drop your file.
   - Supported formats: CSV, XLSX, TXT.

3. **Select Variables and Equation**
   - Choose your X (independent) variable.
   - Choose your Y (dependent) variable.
   - Select the equation type to fit.
   - In Normal Fitting you can enable "loop fitting" to fit another file with the same equation later.

4. **Run the Fitting**
   - Click the fitting button.
   - Results show in three columns (Equation, Parameters, Statistics), then the plot, then the download button.
   - Download the plot (PNG/JPG or PDF if configured; when PDF is used, the in-app preview is PNG).

#### Option 2: Local Streamlit

If you've installed RegressionLab locally, you can run Streamlit on your machine:

**Windows:**
```batch
bin\run_streamlit.bat
```

**macOS/Linux:**
```bash
./bin/run_streamlit.sh
```

**Direct Command:**
```bash
streamlit run src/streamlit_app/app.py
```

The application will open in your default browser, usually at `http://localhost:8501`.

### Desktop Version (Tkinter)

#### Launching the Application

**Method 1: Desktop Shortcut**
- Double-click the "RegressionLab" shortcut created during installation

![Desktop Shortcut](../images/en_documentation/tkinter_docs/shortcut.png)


**Method 2: Shell Scripts**

Windows:
```batch
bin\run.bat
```

macOS/Linux:
```bash
./bin/run.sh
```

**Method 3: Direct Execution**
```bash
python src/main_program.py
```

## Operation Modes

RegressionLab offers four different operation modes to match your workflow. Each mode is designed for specific use cases.

### 1. Normal Fitting

**Use when**: You want to fit one equation to one dataset.

**How it works**:
1. Select an equation type (or define a custom formula).
2. Choose whether to enable loop mode.
3. Load your data file.
4. Select X and Y variables.
5. View the fitting results.

**Loop Mode**: 
- Allows you to modify the data file and refit without restarting.
- Useful for iterative data cleaning or exploring different data subsets.
- After each fit, you can edit the file and reload it.

**Example workflow**:
```
1. Select "Linear with intercept" equation
2. Enable loop mode
3. Load "experiment1.xlsx"
4. Select X="time", Y="temperature"
5. View fit → Notice outlier
6. Edit Excel file to remove outlier
7. Click "Continue" to reload and refit
8. Repeat until satisfied
```

### 2. Multiple Datasets (Single Fit Multiple Datasets)

**Use when**: You want to apply the same equation to multiple different datasets.

**How it works**:
1. Select an equation type once.
2. Specify how many datasets you want to fit.
3. Load each dataset one by one.
4. Choose variables for each dataset.
5. All fits are performed and results displayed.

**Example use case**:
- Fitting the same calibration curve to data from different instruments.
- Analyzing similar experiments performed on different days.
- Comparing the same relationship across different samples.

**Example workflow**:
```
1. Select "Quadratic" equation
2. Enter "3" datasets
3. Load "sample1.csv" → Select X="concentration", Y="absorbance"
4. Load "sample2.csv" → Select X="concentration", Y="absorbance"
5. Load "sample3.csv" → Select X="concentration", Y="absorbance"
6. View all three fits together
```

### 3. Checker Fitting (Multiple Fits Single Dataset)

**Use when**: You want to try multiple equations on the same dataset to find the best fit.

**How it works**:
1. Load your dataset once.
2. Select variables once.
3. Choose multiple equation types to test.
4. All selected equations are fitted sequentially.
5. Compare results to find the best model.

**Example use case**:
- Exploratory data analysis when you're not sure which model fits best.
- Model selection based on R² values.
- Understanding which mathematical relationships might describe your data.

**Example workflow**:
```
1. Load "unknown_data.xlsx"
2. Select X="voltage", Y="current"
3. Select equations to test:
   - Linear
   - Quadratic
   - Exponential
   - Inverse
4. View all fits and compare R² values
5. Choose the best-fitting model
```

### 4. Total Fitting (All Fits Single Dataset)

**Use when**: You want to automatically try ALL available equations on your dataset.

**How it works**:
1. Load your dataset.
2. Select variables.
3. Click "Total Fitting".
4. All predefined equations are fitted automatically.
5. Review all results to find the best fit.

**Example use case**:
- Comprehensive analysis when you have no prior model expectations.
- Creating a complete fitting report.
- Teaching/learning about different function types.

**Example workflow**:
```
1. Load "experimental_data.csv"
2. Select X="x", Y="y"
3. Click "Total Fitting"
4. Wait for all equations to be fitted
5. Review results:
   - Linear: R²=0.85
   - Quadratic: R²=0.98 ← Best fit!
   - Sine: R²=0.45
   - Logarithmic: R²=0.72
   - ...etc.
```

## Understanding Your Data Format

RegressionLab expects data in a specific format for optimal results.

### Multidimensional Data

For regression with 2 or more independent variables (custom formulas with `num_independent_vars > 1`), your data must have columns for each variable. During variable selection you will pick multiple X columns (e.g. `temperature`, `pressure`) and one Y column. The fitting uses all selected X columns together.

### Required Format

Your data file should contain:
- **Column headers**: Each column must have a name (e.g., "time", "voltage", "temperature"). You can use LaTeX with `$` for variable names (e.g. `$\alpha$`, `$\sigma$`) if you need Greek letters or other symbols.
- **Numeric data**: All data values should be numbers.
- **Consistent units**: Use the same units throughout each column.

### Basic Example (CSV)

```text
time,temperature
0,20
1,25
2,30
3,35
4,40
```

### With Uncertainties

RegressionLab automatically detects uncertainty columns if they follow the naming convention: `u<variablename>`

```text
time,utime,temperature,utemperature
0,0.1,20,0.5
1,0.1,25,0.5
2,0.1,30,0.5
3,0.1,35,0.5
4,0.1,40,0.5
```

- `utime`: Uncertainty in time measurements
- `utemperature`: Uncertainty in temperature measurements

**Rules for uncertainty columns**:
- Uncertainties must be non-negative.
- If present, they will be used for weighted fitting.
- They will be displayed as error bars in plots.

### Supported File Formats
- **CSV** (`.csv`): Comma-separated values.
  - Can use comma, semicolon, or tab as delimiters.
  - UTF-8 encoding recommended.

- **Excel** (`.xlsx`): Microsoft Excel files.
  - Data should be in the first sheet.
  - Column headers in the first row.

- **TXT** (`.txt`): Tab-separated or space-separated text files.
  - Plain text format.
  - UTF-8 encoding recommended.

## Interpreting Results

When you perform a fit, RegressionLab displays a results window showing:

![Results Window](../images/en_documentation/tkinter_docs/result.png)

The results window contains:
- **Fitted equation**: The mathematical expression with your fitted parameters.
- **Parameter values**: Each parameter with its uncertainty.
- **Statistical measures**: R², RMSE, χ², and reduced χ².
- **Plot preview**: Visual representation of your data and the fitted curve. For 2 independent variables: interactive 3D plot; for 3+ variables: residuals plot.
- **Prediction button** (desktop): Opens a dialog to evaluate the fitted function at user-specified inputs, with uncertainty propagation when available.


### 1. Fitted Parameters

The values of the parameters in your equation, with uncertainties:

```
Parameter Results:
m = 5.123 ± 0.045
n = 2.456 ± 0.123
```

### 2. Equation

The mathematical equation with your fitted parameters. Always x is the independent variable and y the dependent one.

```
y = 5.123·x + 2.456
```

### 3. Statistical Measures

RegressionLab provides comprehensive statistical information about your fit:

#### R² (Coefficient of Determination)

A statistical measure of how well the fit matches the data:

$$
R^2 = 1 - \frac{SS_{\mathrm{res}}}{SS_{\mathrm{tot}}}, \qquad
SS_{\mathrm{res}} = \sum_{i=1}^{n}(y_i - \hat{y}_i)^2, \qquad
SS_{\mathrm{tot}} = \sum_{i=1}^{n}(y_i - \bar{y})^2
$$

Where $y_i$ = observed values, $\hat{y}_i$ = fitted values, $\bar{y}$ = mean of $y$.

- **R² = 1.0**: Perfect fit
- **R² > 0.95**: Excellent fit
- **R² > 0.85**: Good fit
- **R² > 0.70**: Acceptable fit
- **R² < 0.70**: Poor fit - consider trying a different equation

#### RMSE (Root Mean Square Error)

The average magnitude of residuals. Lower values indicate better fit; expressed in the same units as the dependent variable.

$$
\mathrm{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}
$$

#### χ² (Chi-squared)

Sum of squared residuals weighted by uncertainties. Lower values indicate better fit when uncertainties are well estimated. Only calculated when uncertainty data is available.

$$
\chi^2 = \sum_{i=1}^{n} \frac{(y_i - \hat{y}_i)^2}{\sigma_i^2}
$$

Where $\sigma_i$ = uncertainty (standard deviation) of the $i$-th measurement.

#### χ²_red (Reduced Chi-squared)

Chi-squared divided by degrees of freedom. A value close to 1 suggests uncertainties are consistent with the fit.

$$
\chi^2_{\mathrm{red}} = \frac{\chi^2}{\nu}
$$

#### ν (Degrees of Freedom)

Number of data points minus the number of fitted parameters. Used in statistical calculations and confidence intervals.

$$
\nu = n - p
$$

Where $n$ = number of data points, $p$ = number of fitted parameters.

#### 95% Confidence Intervals (IC 95%)

For each fitted parameter, the range within which the true value is expected with 95% confidence, calculated using the t-distribution. These intervals help assess the reliability of your parameter estimates.

$$
\theta_k \pm t_{0.975,\,\nu} \cdot \sigma_{\theta_k}
$$

Where $\theta_k$ = estimated parameter, $\sigma_{\theta_k}$ = its standard error (from the fit covariance matrix), $t_{0.975,\,\nu}$ = critical value of the t-distribution for 97.5% (two-tailed 95%) with $\nu$ degrees of freedom.

### 4. Plot

A visualization showing:
- **Red points with error bars**: Your original data (error bars appear if uncertainties are provided).
- **Black line**: The fitted curve.
- **Axis labels**: Your variable names.
- **Legend**: Equation and R² value.

### 5. Output File

The plot is automatically saved as a PNG image (or JPG/PDF if configured) in the output directory (default: `output/`).

## Tips for Better Results

### Data Quality

1. **Remove outliers**: Outliers can significantly affect the fit. Use loop mode to iteratively remove them.

2. **Check data range**: Ensure your data covers the range of interest. Extrapolation beyond your data range can be unreliable.

3. **Use uncertainties**: If you have measurement uncertainties, include them. This provides more accurate parameter estimates.

4. **Sufficient data points**: More data points generally give better fits. Aim for at least 10-20 points for simple equations.

### Choosing Equations

1. **Physical basis**: If you know the underlying physics/chemistry, choose an equation that matches the theory.

2. **Visual inspection**: Plot your data first to get an idea of the shape (linear, curved, oscillating, etc.).

3. **Start simple**: Try simpler equations (linear, quadratic) before complex ones.

4. **Compare R² values**: When testing multiple equations, the one with the highest R² generally fits best.

5. **Be cautious of overfitting**: A complex equation with many parameters might fit better but may not generalize well.

### Custom Formulas

If none of the predefined equations work, you can define your own:

1. Select "Custom Formula" as the equation type.
2. Specify the number of parameters.
3. Specify the number of independent variables (1 for standard y=f(x), 2+ for multidimensional regression).
4. Name your parameters (e.g., `a`, `b`, `c`). You can also use special characters.
5. Enter your formula using Python syntax.
   - `a*x**2 + b*x + c` (quadratic, 1 variable).
   - `a*np.exp(-b*x)` (exponential decay).
   - `a/(1 + b*x)` (hyperbola).
   - `a*x_0 + b*x_1 + c` (multidimensional, 2 variables: use `x_0`, `x_1`, etc.).

For multidimensional (2+ variables), you will select multiple X columns during variable selection. With 2 variables you get an interactive 3D plot; with 3+ you get a residuals plot.

### Prediction Window (Desktop)

After fitting, the result window shows a **Prediction** button. Click it to open a dialog where you can:

1. Enter values for each independent variable (x, x_0, x_1, etc.).
2. See the predicted y value updated in real time.
3. When parameter covariance is available, the predicted uncertainty is shown as well.

This works for single fits, multiple datasets, checker mode, and total fitting. It supports both 1D and multidimensional fits.

## Common Workflows

### Workflow 1: Quick Analysis

```
Goal: Quickly check if data follows a linear relationship

1. Use web version (online)
2. Upload CSV file
3. Select "Linear with intercept"
4. Check R² value:
   - R² > 0.95? Linear model is good!
   - R² < 0.85? Try other equations
```

### Workflow 2: Finding the Best Model

```
Goal: Determine which equation best describes the data

1. Use desktop version (or Streamlit Checker mode)
2. Load data
3. Use "Checker Fitting" mode
4. Select several candidate equations
5. Compare R² values
6. Choose the best-fitting equation
```

### Workflow 3: Batch Processing

```
Goal: Fit the same equation to 10 similar datasets

1. Use desktop version (or Streamlit Multiple Datasets mode)
2. Select "Multiple Datasets" mode
3. Choose equation (e.g., "Quadratic")
4. Enter "10" for number of datasets
5. Load each file
6. View all results together
```

### Workflow 4: Iterative Refinement

```
Goal: Remove outliers and improve fit quality

1. Use desktop version with loop mode
2. Select "Normal Fitting" → Enable loop mode
3. Perform initial fit
4. Identify outliers in the plot
5. Edit data file to remove/correct outliers
6. Click "Continue" to reload and refit
7. Repeat until satisfied with R² value
```

## Next Steps

Now that you understand the basics:

- **Streamlit Guide**: For detailed information on the web interface, see [Streamlit Guide](streamlit-guide.md).
- **Tkinter Guide**: For detailed information on the desktop interface, see [Tkinter Guide](tkinter-guide.md).
- **Configuration**: Customize appearance and behavior in the [Configuration Guide](configuration.md).
- **Advanced Usage**: Learn how to add custom functions in [Extending RegressionLab](extending.md).

---

*Need help? Check the [Troubleshooting Guide](troubleshooting.md) for common issues and solutions.*
