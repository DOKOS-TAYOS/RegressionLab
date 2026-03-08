# User Guide

This guide explains how to use RegressionLab with the current Electron desktop frontend and the optional Streamlit frontend.

## Overview

RegressionLab provides two interfaces built on the same Python fitting core:

- **Desktop Version (Electron)**: the main desktop workflow in this branch. It includes a home screen with the RegressionLab logo and version, a collapsible left sidebar, interactive Plotly charts, in-app configuration, and a local FastAPI sidecar.
- **Web Version (Streamlit)**: optional browser frontend for quick access without the desktop shell.

## Choosing Your Version

### Use the Desktop Version (Electron) if:

- You want the main maintained desktop workflow for this branch.
- You need offline use.
- You want the integrated configuration screen.
- You want batch result galleries, plot comparison, and in-window plot expansion.
- You want the data inspection workflow in the same desktop shell.

### Use the Web Version (Streamlit) if:

- You want quick access in a browser.
- You are sharing the tool with other users.
- You do not need the Electron desktop shell.

## Getting Started

### Desktop Version (Electron)

Run the desktop app with:

Windows:

```batch
bin\run.bat
```

macOS/Linux:

```bash
./bin/run.sh
```

Development mode:

Windows:

```batch
bin\run.bat --dev
```

macOS/Linux:

```bash
./bin/run.sh --dev
```

The main sidebar contains:

- `RegressionLab`
- `Mirar datos` / `View Data`
- `Information`
- `Configure`

The sidebar can be collapsed to the left if you want more space for plots and tables.

### Web Version (Streamlit)

Run Streamlit locally:

```bash
streamlit run src/streamlit_app/app.py
```

Or use the launch scripts:

Windows:

```batch
bin\run_streamlit.bat
```

macOS/Linux:

```bash
./bin/run_streamlit.sh
```

## Desktop Home Screen

The Electron home screen shows:

- the RegressionLab logo in large format
- the current app version
- shortcuts into the fitting workflow

From there you can go directly into the fitting pages, inspect data, open the information page, or edit configuration.

## Operation Modes

RegressionLab offers four fitting modes plus a dedicated data-inspection page.

### 1. Normal Fitting

Use this when you want to fit one equation to one dataset.

Typical flow:

1. Select an equation or choose a custom formula.
2. Optionally enable loop mode.
3. Load the dataset.
4. Choose X and Y variables.
5. Run the fitting.
6. Inspect the results, plot, statistics, and prediction panel.

Loop mode lets you keep the workflow configured and run the fit again after editing the dataset, without rebuilding the whole setup.

### 2. Multiple Datasets

Use this when you want to apply the same equation to several datasets.

Typical flow:

1. Select the equation once.
2. Open the file picker and select several files at once.
3. Review the dataset cards.
4. Choose variables for each dataset.
5. Run the fits.
6. Browse the result gallery and open the desired result.
7. Optionally compare two results side by side.

This is useful for repeated experiments, calibration sets, or comparing the same model across different samples.

### 3. Checker Fitting

Use this when you want to try several equations on the same dataset.

Typical flow:

1. Load one dataset.
2. Choose X and Y once.
3. Select the candidate equations with checkboxes.
4. Run the fitting.
5. Compare the results from the gallery.

This is the best mode when you do not know in advance which model will fit best.

### 4. Total Fitting

Use this when you want to try all available built-in equations on one dataset.

Typical flow:

1. Load one dataset.
2. Choose X and Y.
3. Run total fitting.
4. Review the gallery of results.
5. Open the most interesting plots and compare them.

### 5. View Data / Mirar datos

Use this page when you want to inspect and prepare data before fitting.

The page shows:

- the loaded file path
- a data table using most of the available width
- a large pair plot directly below the table
- transform, clean, and save actions
- data help inside the same page

This lets you inspect columns, check data quality, transform signals, clean problematic rows, and save processed datasets before moving into a fitting mode.

## Custom Formulas

If the predefined equations are not enough, choose the custom formula option.

You can define:

- the formula expression
- the parameter names
- the number of independent variables

Examples:

- `a*x**2 + b*x + c`
- `a*np.exp(-b*x)`
- `a*x_0 + b*x_1 + c`

For multidimensional fits:

- with 2 independent variables, the desktop app shows an interactive 3D plot
- with 3 or more independent variables, the desktop app shows a residual-style plot

## Data Format

Your files should contain:

- column headers
- numeric values
- consistent units within each column

Basic CSV example:

```text
time,temperature
0,20
1,25
2,30
3,35
4,40
```

Uncertainty columns are detected when they use the `u<variable>` convention:

```text
time,utime,temperature,utemperature
0,0.1,20,0.5
1,0.1,25,0.5
2,0.1,30,0.5
3,0.1,35,0.5
4,0.1,40,0.5
```

Supported formats:

- `.csv`
- `.txt`
- `.xlsx`

## Understanding Results

The desktop result view contains:

- **Equation block**: the selected formula and the formatted fitted equation
- **Interactive plot**: preview of the fit, 3D view, or residual plot depending on the case
- **Statistics cards**: R2, RMSE, chi-squared, reduced chi-squared, and degrees of freedom
- **Parameter cards**: each parameter value and uncertainty shown next to its 95% confidence interval
- **Solution text block**: a read-only text area with the backend output and a copy button
- **Prediction panel**: inputs for evaluating the fitted function without opening a separate dialog

### Plot Controls

In the desktop app you can:

- expand the selected plot to a larger in-window view
- reveal the exported plot file from the result panel
- compare two batch results side by side in a dedicated comparison view

### Prediction Panel

Prediction is integrated into the result page.

You do not need to press a button:

1. Enter the values for the independent variables.
2. Wait briefly for the automatic recalculation.
3. Read the predicted `y` value.
4. If uncertainty propagation is available, the result also includes the propagated uncertainty.

## Batch Result Gallery

Multiple datasets, checker fitting, and total fitting use a gallery view on the right side of the results page.

That gallery provides:

- thumbnail previews of each solution plot
- the dataset or plot name below each thumbnail
- one-click selection to show a result in large format
- a comparison button to place two selected results side by side

## Information and Configuration

### Information

The `Information` page is a single vertical page in the Electron app.

It includes:

- general help
- project information
- update checking at the bottom of the page

### Configuration

The `Configure` page edits `.env` settings from the desktop UI.

Boolean options are shown as checkboxes, while other values use the appropriate inputs from the schema.

## Tips for Better Results

- Start with simple equations before trying complex ones.
- Use uncertainty columns when available.
- Inspect the pair plot in `Mirar datos` before fitting.
- Use checker mode when you are unsure which equation to trust.
- Use batch comparison when several fits are close and you want to compare them visually.
- Use loop mode when you are iterating on the same dataset.

## Common Workflows

### Quick Analysis

1. Open the desktop app.
2. Choose normal fitting.
3. Load one dataset.
4. Select a simple equation such as linear with intercept.
5. Inspect R2, RMSE, and the plot.

### Finding the Best Model

1. Open checker fitting.
2. Load one dataset.
3. Select several candidate equations with checkboxes.
4. Run the fit.
5. Browse the gallery and compare the best candidates.

### Batch Processing

1. Open multiple datasets.
2. Select the common equation.
3. Pick several files in one file dialog.
4. Run the fit.
5. Review the gallery and compare two results if needed.

### Iterative Refinement

1. Open normal fitting.
2. Enable loop mode.
3. Fit the dataset.
4. Edit the file to remove outliers or adjust the data.
5. Run the fit again with the same setup.

## Next Steps

- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)
- [Streamlit Guide](streamlit-guide.md)
- [Tkinter Guide](tkinter-guide.md) - legacy reference
- [Troubleshooting Guide](troubleshooting.md)
