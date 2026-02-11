# Configuration Guide

RegressionLab is highly customizable through a single `.env` file. This guide describes every option, where it applies (desktop, web, or both), and how to change it safely.

## Getting Started with Configuration

### Configuring from Tkinter (Desktop App)

If you use the **Tkinter desktop application**, you can change settings without editing files: from the main menu, click **Configure** (or **Configurar** in Spanish). A configuration dialog opens with **collapsible sections**:

- **Language**: Interface language (Spanish, English, German).
- **UI**: Window and text colors, button colors (normal, cancel, accent), spacing, button width, font family and size, spinbox/entry widths, and data-preview selection color.
- **Plot**: Figure dimensions, DPI, title visibility, and line/marker style and colors for generated plots.
- **Font**: Font family and sizes for plot title, axis labels, and tick labels.
- **Paths**: Default input and output folders, filename template for saved plots, and export format (PNG, JPG, PDF).
- **Links**: Optional URL for the “Donations” link in the Information dialog.
- **Logging**: Log level (e.g. DEBUG, INFO), log file path, and whether messages are also printed to the console.

![Configuration Dialog](../images/en_documentation/tkinter_docs/configuration.png)

Each option shows a short description. When you click **Accept**, the values are written to `.env` and the application restarts so the new settings take effect. **Cancel** discards changes. This is the easiest way to customize RegressionLab when using the desktop version.

### Locating the Configuration File

The configuration file lives in the **root directory** of the RegressionLab project:
```
RegressionLab/
  .env               ← Your configuration file
  .env.example       ← Template with all options (desktop)
  .env_mobile.example ← Optional template for mobile (e.g. termux); copy to .env if needed
```

### First-time setup

If `.env` does not exist yet:

```bash
# Copy the example file
cp .env.example .env

# Or on Windows
copy .env.example .env
```

Then open and edit `.env` with any text editor, for example:
- **Visual Studio Code**: `code .env`.
- **Nano** (Linux/macOS): `nano .env`.
- **Notepad** (Windows): `notepad .env`.
- **Vim**: `vim .env`.

## Configuration Sections

The `.env` file is grouped into sections that match the Tkinter **Configure** dialog:

1. [Language Configuration](#1-language-configuration)
2. [UI Theme Configuration](#2-ui-theme-configuration)
3. [Plot Style Configuration](#3-plot-style-configuration)
4. [Font Configuration](#4-font-configuration)
5. [File Path Configuration](#5-file-path-configuration)
6. [Links (Optional)](#6-links-optional)
7. [Logging Configuration](#7-logging-configuration)

---

## 1. Language Configuration

### Setting the Application Language

```ini
LANGUAGE="es"
```

**Available Languages**:
- `es`, `español`, `spanish`, `esp` → Spanish (default)
- `en`, `english`, `ingles`, `inglés`, `eng` → English
- `de`, `german`, `deutsch`, `ger` → German

**Example**:
```ini
# Use Spanish (default)
LANGUAGE="es"

# Use English
LANGUAGE="en"

# Use German
LANGUAGE="de"
```

**Effect**:
- Changes menus, buttons, dialogs, and all other interface text to the selected language.
- Applies to both the Tkinter desktop app and the Streamlit web interface.
- Does not change column names, file contents, or text you type (e.g. axis labels you enter yourself).

---

## 2. UI Theme Configuration

These settings control the look of the Tkinter desktop app (window, buttons, fonts, spacing). The Streamlit web interface uses them where applicable; behavior may differ. Hover and active (click) colors are derived automatically from the base colors you set.

### Color Settings

#### Background and Foreground

```ini
UI_BACKGROUND="#181818"
UI_FOREGROUND="#CCCCCC"
```

- **UI_BACKGROUND**: Background color of the main window and most panels.
- **UI_FOREGROUND**: Default text color for labels, entries, and other UI text.

**Color options**:
- **Named colors**: `"white"`, `"black"`, `"navy"`, `"crimson"`, etc.
- **Hex codes**: `"#2C3E50"`, `"#FF5733"`, etc.

#### Button Colors

```ini
UI_BUTTON_BG="#1F1F1F"
UI_BUTTON_FG="lime green"
UI_BUTTON_FG_CANCEL="red2"
UI_BUTTON_FG_ACCENT2="yellow"
```

- **UI_BUTTON_BG**: Background color of all buttons.
- **UI_BUTTON_FG**: Text color for standard action buttons.
- **UI_BUTTON_FG_CANCEL**: Text color for cancel, exit, or destructive buttons.
- **UI_BUTTON_FG_ACCENT2**: Text color for secondary accent buttons (e.g. “Accept” in dialogs).

### Layout and Widget Sizes

#### Padding and Button Width

```ini
UI_PADDING=8
UI_BUTTON_WIDTH=12
```

- **UI_PADDING**: Spacing in pixels between widgets, applied both horizontally and vertically.
- **UI_BUTTON_WIDTH**: Nominal width of buttons in character units. “Wide” buttons use 2.5× this value.

#### Font Settings

```ini
UI_FONT_FAMILY="Bahnschrift"
UI_FONT_SIZE=18
```

- **UI_FONT_FAMILY**: Font used for all UI text (menus, labels, buttons).
- **UI_FONT_SIZE**: Base font size in points for the desktop interface.

**Common font families**:
- **Monospace**: `"Courier"`, `"Courier New"`, `"Menlo"`, `"Monaco"`.
- **Sans-serif**: `"Arial"`, `"Helvetica"`, `"Verdana"`, `"Tahoma"`.
- **Serif**: `"Times New Roman"`, `"Georgia"`, `"Palatino"`.

#### Input Widget Sizes

```ini
UI_SPINBOX_WIDTH=10
UI_ENTRY_WIDTH=25
```

- **UI_SPINBOX_WIDTH**: Width of numeric spinbox fields in character units.
- **UI_ENTRY_WIDTH**: Width of text entry fields in character units.

#### Data Preview (Text Widget)

```ini
UI_TEXT_SELECT_BG="steel blue"
```

- **UI_TEXT_SELECT_BG**: Background color of selected text in the data preview area. The preview uses **UI_FOREGROUND** for text; its background is derived from the main UI background.

### Example Themes

#### Professional Dark Theme (default-like)
```ini
UI_BACKGROUND="#181818"
UI_FOREGROUND="#CCCCCC"
UI_BUTTON_BG="#1F1F1F"
UI_BUTTON_FG="lime green"
UI_BUTTON_FG_CANCEL="red2"
UI_BUTTON_FG_ACCENT2="yellow"
UI_PADDING=8
UI_BUTTON_WIDTH=12
```

#### Classic Light Theme
```ini
UI_BACKGROUND="white"
UI_FOREGROUND="black"
UI_BUTTON_BG="gray90"
UI_BUTTON_FG="blue"
UI_BUTTON_FG_CANCEL="red"
UI_BUTTON_FG_ACCENT2="dark orange"
UI_PADDING=8
UI_BUTTON_WIDTH=12
```

#### Ocean Theme
```ini
UI_BACKGROUND="#001f3f"
UI_FOREGROUND="#7FDBFF"
UI_BUTTON_BG="#003366"
UI_BUTTON_FG="#39CCCC"
UI_BUTTON_FG_CANCEL="#FF851B"
UI_BUTTON_FG_ACCENT2="#7FDBFF"
UI_PADDING=8
UI_BUTTON_WIDTH=12
```

---

## 3. Plot Style Configuration

These settings control the size, resolution, and visual style of the regression plots (used by both the Tkinter and Streamlit interfaces).

### Figure Dimensions

```ini
PLOT_FIGSIZE_WIDTH=12
PLOT_FIGSIZE_HEIGHT=6
DPI=100
```

- **PLOT_FIGSIZE_WIDTH**: Figure width in inches (for both on-screen display and saved files).
- **PLOT_FIGSIZE_HEIGHT**: Figure height in inches.
- **DPI**: Resolution in dots per inch; higher values give sharper output and larger file sizes.

**Recommendations**:
- **Screen display**: 100 DPI.
- **High-quality prints**: 300 DPI.
- **Publications**: 600 DPI.

### Title Display

```ini
PLOT_SHOW_TITLE=false
```

- **PLOT_SHOW_TITLE**: Whether to display a title above the plot.
  - `true`: Show title (derived from the plot/filename).
  - `false`: No title (cleaner look for slides or publications).

### Fitted Curve Style

```ini
PLOT_LINE_COLOR="black"
PLOT_LINE_WIDTH=1.0
PLOT_LINE_STYLE="-"
```

- **PLOT_LINE_COLOR**: Color of the fitted regression curve.
- **PLOT_LINE_WIDTH**: Line width in points (e.g. 1.0 = thin, 2.0 = bold).
- **PLOT_LINE_STYLE**: Line pattern for the fitted curve.

**Line style options**:
- `"-"`: Solid line (default).
- `"--"`: Dashed line.
- `"-."`: Dash-dot line.
- `":"`: Dotted line.

### Data Points Style

```ini
PLOT_MARKER_FORMAT="o"
PLOT_MARKER_SIZE=5
```

- **PLOT_MARKER_FORMAT**: Marker shape for the measured data points.
- **PLOT_MARKER_SIZE**: Marker size in points.

**Marker format options**: `"o"` (circle, default), `"s"` (square), `"^"` (triangle up), `"d"` (diamond), `"*"` (star).

### Colors for Data Points

```ini
PLOT_ERROR_COLOR="crimson"
PLOT_MARKER_FACE_COLOR="crimson"
PLOT_MARKER_EDGE_COLOR="crimson"
```

- **PLOT_ERROR_COLOR**: Color of the vertical (or horizontal) error bars on data points.
- **PLOT_MARKER_FACE_COLOR**: Fill color of the data point markers.
- **PLOT_MARKER_EDGE_COLOR**: Outline/border color of the markers.

**Common color names**:
- Basic: `"red"`, `"blue"`, `"green"`, `"black"`, `"white"`.
- Extended: `"crimson"`, `"navy"`, `"teal"`, `"gold"`, `"orange"`.
- Scientific: `"darkblue"`, `"darkgreen"`, `"darkred"`.

### Example Plot Styles

#### Publication Style (Black & White)
```ini
PLOT_LINE_COLOR="black"
PLOT_LINE_WIDTH=2.0
PLOT_LINE_STYLE="-"
PLOT_MARKER_FORMAT="o"
PLOT_MARKER_SIZE=6
PLOT_ERROR_COLOR="black"
PLOT_MARKER_FACE_COLOR="white"
PLOT_MARKER_EDGE_COLOR="black"
DPI=300
```

#### Colorful Presentation Style
```ini
PLOT_LINE_COLOR="#2C3E50"
PLOT_LINE_WIDTH=2.5
PLOT_LINE_STYLE="-"
PLOT_MARKER_FORMAT="^"
PLOT_MARKER_SIZE=8
PLOT_ERROR_COLOR="#E74C3C"
PLOT_MARKER_FACE_COLOR="#E74C3C"
PLOT_MARKER_EDGE_COLOR="#C0392B"
DPI=150
```

---

## 4. Font Configuration

Control the font family, size, and style of all text drawn on the plots (title, axis labels, and tick numbers).

### Font Family

```ini
FONT_FAMILY="serif"
```

**Options** (Matplotlib generic families; exact font depends on your system):
- `serif`: Serif fonts (e.g. Times-like); good for formal or printed work.
- `sans-serif`: Sans-serif fonts (e.g. Arial-like); clean and readable on screen.
- `monospace`: Fixed-width fonts (e.g. Courier-like); useful for technical labels.
- `cursive`: Script-like fonts; decorative use.
- `fantasy`: Decorative/artistic fonts.

### Title Font

```ini
FONT_TITLE_SIZE="xx-large"
FONT_TITLE_WEIGHT="semibold"
```

- **FONT_TITLE_SIZE**: Relative size of the plot title. Only used when **PLOT_SHOW_TITLE** is `true`.

**Size options**: `xx-small`, `x-small`, `small`, `medium`, `large`, `x-large`, `xx-large`.

- **FONT_TITLE_WEIGHT**: Font weight (boldness) of the plot title.

**Weight options**: `normal`, `light`, `semibold`, `bold`, `heavy`.

### Axis Labels

```ini
FONT_AXIS_SIZE=30
FONT_AXIS_STYLE="italic"
```

- **FONT_AXIS_SIZE**: Font size in points for the x- and y-axis labels.
- **FONT_AXIS_STYLE**: Font style for axis labels (e.g. variable names are often italic).

**Style options**: `normal`, `italic`, `oblique`.

### Tick Labels

```ini
FONT_TICK_SIZE=16
```

- **FONT_TICK_SIZE**: Font size in points for the numbers on the axis tick marks.

### Example Font Configurations

#### Academic Publication
```ini
FONT_FAMILY="serif"
FONT_TITLE_SIZE="large"
FONT_TITLE_WEIGHT="bold"
FONT_AXIS_SIZE=24
FONT_AXIS_STYLE="italic"
FONT_TICK_SIZE=18
```

#### Modern Presentation
```ini
FONT_FAMILY="sans-serif"
FONT_TITLE_SIZE="x-large"
FONT_TITLE_WEIGHT="semibold"
FONT_AXIS_SIZE=28
FONT_AXIS_STYLE="normal"
FONT_TICK_SIZE=20
```

---

## 5. File Path Configuration

Control the default folders for loading data and saving plots, the naming pattern for saved files, and the image format used when exporting.

```ini
FILE_INPUT_DIR="input"
FILE_OUTPUT_DIR="output"
FILE_FILENAME_TEMPLATE="fit_{}"
FILE_PLOT_FORMAT="png"
```

### Input Directory

```ini
FILE_INPUT_DIR="input"
```

**Options**:
- **Relative path** (from the RegressionLab root): e.g. `"input"`, `"data"`, `"experiments"`.
- **Absolute path**: e.g. `"/home/user/data"` or `"C:\\Users\\Name\\Documents\\Data"`.

### Output Directory

```ini
FILE_OUTPUT_DIR="output"
```

**Options**:
- **Relative path**: e.g. `"output"`, `"results"`, `"plots"` (from the RegressionLab root).
- **Absolute path**: e.g. `"/home/user/results"` or `"C:\\Users\\Name\\Documents\\Results"`.

**Note**: The output directory is created automatically if it does not exist.

### Filename Template

```ini
FILE_FILENAME_TEMPLATE="fit_{}"
```

The `{}` placeholder is replaced with the plot name (e.g. from the loaded file or dialog). The file extension is added automatically based on **FILE_PLOT_FORMAT** (e.g. `.png`).

**Examples**:
```ini
# Default (output: fit_experiment1.png when FILE_PLOT_FORMAT="png")
FILE_FILENAME_TEMPLATE="fit_{}"

# With prefix
FILE_FILENAME_TEMPLATE="regression_{}"
# Result: regression_experiment1.png

# With suffix
FILE_FILENAME_TEMPLATE="{}_result"
# Result: experiment1_result.png
```

### Plot Output Format

```ini
FILE_PLOT_FORMAT="png"
```

**Options**: `png`, `jpg`, `pdf`

- **png**: Default; good balance of quality and file size; supports transparency.
- **jpg**: Smaller files; suitable for sharing or embedding when vector output is not required.
- **pdf**: Vector output for publications and printing; in-app preview may still be raster (e.g. PNG).

---

## 6. Links (Optional)

```ini
DONATIONS_URL="https://www.youtube.com/@whenphysics"
```

- **DONATIONS_URL**: URL displayed as a “Donations” (or similar) link in the desktop app’s **Information** / help dialog, e.g. to support the project. Leave empty to hide the link.

---

## 7. Logging Configuration

Control where and how much RegressionLab logs: level of detail, log file location, and whether messages are also printed to the console.

```ini
LOG_LEVEL=INFO
LOG_FILE=regressionlab.log
LOG_CONSOLE=false
```

### Log Level

```ini
LOG_LEVEL=INFO
```

**Options** (from most to least verbose):
- `DEBUG`: Very detailed messages (function flow, variable values); useful for development and debugging.
- `INFO`: General operational messages (default); good for normal use.
- `WARNING`: Only warnings and more severe; reduces log noise.
- `ERROR`: Only errors and critical issues.
- `CRITICAL`: Only critical failures.

**Recommendation**: Use `INFO` for everyday use; switch to `DEBUG` when troubleshooting.

### Log File

```ini
LOG_FILE=regressionlab.log
```

- Path to the log file (relative to the RegressionLab root or absolute). Logs are appended; the file is created automatically if it does not exist.

**Examples**:
```ini
# Default (in RegressionLab root)
LOG_FILE=regressionlab.log

# In logs subdirectory
LOG_FILE=logs/app.log

# Absolute path
LOG_FILE=/var/log/regressionlab.log
```

### Console Logging

```ini
LOG_CONSOLE=false
```

- `true`: Also print log messages to the console/terminal (useful when running from a terminal).
- `false`: Write only to the log file (default; cleaner when using the GUI).

**Recommendation**: Use `true` when debugging from the command line; use `false` when running the desktop app or for quieter operation.

---

## Applying Configuration Changes

### Tkinter (desktop)

You can change settings in two ways:

- **From the app**: Main menu → **Configure** (or **Configurar**). Adjust values in the dialog and click **Accept**; the app restarts so the new settings take effect.
![Configuration Dialog](../images/en_documentation/tkinter_docs/configuration.png)
- **By editing `.env`**: Edit `.env` with a text editor, save, then restart the application:

```bash
# Restart the application
python src/main_program.py
```

### Streamlit (web)

1. Edit the `.env` file and save.
2. Reload the app in your browser (e.g. Ctrl+R or Cmd+R).

**Note**: For some changes (e.g. paths or logging), you may need to stop and restart the Streamlit server:

```bash
# Stop: Ctrl+C in terminal
# Restart:
streamlit run src/streamlit_app/app.py
```

---

## Common Configuration Scenarios

### Scenario 1: Preparing plots for publication

```ini
# High-resolution black-and-white plots for papers or reports
DPI=600
PLOT_LINE_COLOR="black"
PLOT_LINE_WIDTH=2.0
PLOT_MARKER_FORMAT="o"
PLOT_MARKER_SIZE=6
PLOT_ERROR_COLOR="black"
PLOT_MARKER_FACE_COLOR="white"
PLOT_MARKER_EDGE_COLOR="black"
PLOT_SHOW_TITLE=false
FONT_FAMILY="serif"
FONT_AXIS_SIZE=28
FONT_TICK_SIZE=20
```

### Scenario 2: Quick data exploration

```ini
# Fast rendering and colorful on-screen display
DPI=100
PLOT_LINE_COLOR="blue"
PLOT_LINE_WIDTH=1.5
PLOT_MARKER_FORMAT="o"
PLOT_MARKER_SIZE=5
PLOT_ERROR_COLOR="red"
PLOT_MARKER_FACE_COLOR="red"
PLOT_MARKER_EDGE_COLOR="red"
PLOT_SHOW_TITLE=true
LOG_LEVEL=WARNING
```

### Scenario 3: Debugging issues

```ini
# Detailed logging to trace problems
LOG_LEVEL=DEBUG
LOG_CONSOLE=true
LOG_FILE=debug.log
```

Set **LOG_CONSOLE** to `true` so you can see logs in the terminal.

### Scenario 4: Batch processing

```ini
# Settings suited to processing many files in one run
DPI=150
FILE_OUTPUT_DIR="batch_results"
LOG_LEVEL=WARNING
LOG_CONSOLE=false
```

---

## Troubleshooting configuration

### Changes not applied

**Problem**: You edited `.env` but the app still shows old behavior.

**Solutions**:
1. Confirm the `.env` file was saved (check the timestamp).
2. Fully quit and restart the application (not just refresh the window).
3. Look for syntax errors: missing quotes, stray spaces, or broken lines in `.env`.
4. Ensure `.env` is in the RegressionLab project root (same folder as `src/`, `.env.example`, etc.).

### Invalid color names

**Problem**: The app reports an invalid or unknown color.

**Solutions**:
1. Put color values in double quotes: `"midnight blue"` not `midnight blue`.
2. Use a standard color name (e.g. from [Matplotlib](https://matplotlib.org/stable/gallery/color/named_colors.html)) or a hex code like `"#2C3E50"`.
3. Check spelling; multi-word names must be quoted.

### Font not found

**Problem**: The UI or plot does not show the font you configured.

**Solutions**:
1. Confirm the font is installed on your system (e.g. via Font Book, Windows Fonts).
2. Prefer generic families (`serif`, `sans-serif`, `monospace`); the system will pick a suitable font.
3. Check the exact font name (e.g. “Times New Roman” vs “Times”).

### Path issues

**Problem**: The app cannot find the input or output directory (or files in it).

**Solutions**:
1. On Windows, use forward slashes (`/`) or escaped backslashes (`\\`) in paths.
2. For **FILE_INPUT_DIR**, the folder must exist; for **FILE_OUTPUT_DIR**, it is created if missing.
3. Check read/write permissions for the chosen directories.
4. If relative paths fail, try an absolute path to rule out working-directory issues.

---

## Default configuration

To restore default settings, overwrite `.env` with the example file:

```bash
cp .env.example .env
```

Or delete `.env` and let RegressionLab use built-in defaults.

---

## Next steps

- **Customize your plots**: Experiment with [plot styles](#3-plot-style-configuration) and fonts.
- **Create a theme**: Build a [UI theme](#2-ui-theme-configuration) that fits your workflow.
- **Go further**: See the [Extending RegressionLab](extending.md) guide for advanced customization.

---

*Need more help? Check the [Troubleshooting Guide](troubleshooting.md) or open an issue on GitHub.*
