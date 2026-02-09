# Configuration Guide

RegressionLab is highly customizable through the `.env` configuration file. This guide explains all available configuration options and how to modify them.

## Getting Started with Configuration

### Configuring from Tkinter (Desktop App)

If you use the **Tkinter desktop application**, you can change settings without editing files manually: from the main menu, click **Configure** (or **Configurar** in Spanish). A configuration dialog opens with **collapsible sections** for:

- **Language**: Application language (es, en, de).
- **UI**: Background/foreground colors, button colors (normal, cancel, accent), padding, button width, font family/size, spinbox/entry widths, data-preview selection color.
- **Plot**: Figure size, DPI, title on/off, line/marker style and colors.
- **Font**: Plot font family, title/axis/tick size and style.
- **Paths**: Input/output directories, filename template, plot format (PNG, JPG, PDF).
- **Links**: Donations URL (optional).
- **Logging**: Log level, log file path, console output on/off.

Each option shows a short description. When you click **Accept**, the values are written to `.env` and the application restarts so the new settings take effect. **Cancel** discards changes. This is the easiest way to customize RegressionLab when using the desktop version.

### Locating the Configuration File

The configuration file is located in the root directory of RegressionLab:
```
RegressionLab/
  .env               ← Your configuration file
  .env.example       ← Template with all options (desktop)
  .env_mobile.example ← Optional template for mobile (e.g. Pydroid 3); copy to .env if needed
```

### First-Time Setup

If `.env` doesn't exist:

```bash
# Copy the example file
cp .env.example .env

# Or on Windows
copy .env.example .env
```

Then edit `.env` with your preferred text editor:
- **Visual Studio Code**: `code .env`.
- **Nano** (Linux/macOS): `nano .env`.
- **Notepad** (Windows): `notepad .env`.
- **Vim**: `vim .env`.

## Configuration Sections

The `.env` file is organized into logical sections (same groups as in the Tkinter **Configure** dialog):

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
- Changes all UI text, dialogs, and messages.
- Affects both Tkinter and Streamlit interfaces.
- Does not affect data or plot labels.

**Note**: Language changes require restarting the application.

---

## 2. UI Theme Configuration

These settings control the appearance of the Tkinter desktop application. They do not affect the Streamlit web version. Active (hover/click) colors are derived automatically from these values.

### Color Settings

#### Background and Foreground

```ini
UI_BACKGROUND="#181818"
UI_FOREGROUND="#CCCCCC"
```

- **UI_BACKGROUND**: Main window background color
- **UI_FOREGROUND**: Text color

**Color Options**:
- **Named colors**: `"white"`, `"black"`, `"navy"`, `"crimson"`, etc.
- **Hex codes**: `"#2C3E50"`, `"#FF5733"`, etc.

#### Button Colors

```ini
UI_BUTTON_BG="#1F1F1F"
UI_BUTTON_FG="lime green"
UI_BUTTON_FG_CANCEL="red2"
UI_BUTTON_FG_ACCENT2="yellow"
```

- **UI_BUTTON_BG**: Background color for buttons
- **UI_BUTTON_FG**: Text color for normal buttons
- **UI_BUTTON_FG_CANCEL**: Text color for cancel/exit buttons
- **UI_BUTTON_FG_ACCENT2**: Text color for secondary accent buttons (e.g. “Accept” in dialogs)

### Layout and Widget Sizes

#### Padding and Button Width

```ini
UI_PADDING=8
UI_BUTTON_WIDTH=12
```

- **UI_PADDING**: Spacing between widgets (pixels), used for both horizontal and vertical padding
- **UI_BUTTON_WIDTH**: Width for buttons (in characters). Wide buttons use 2.5× this value internally

#### Font Settings

```ini
UI_FONT_FAMILY="Bahnschrift"
UI_FONT_SIZE=18
```

- **UI_FONT_FAMILY**: Font family for UI text
- **UI_FONT_SIZE**: UI font size (points)

**Common Font Families**:
- **Monospace**: `"Courier"`, `"Courier New"`, `"Menlo"`, `"Monaco"`.
- **Sans-serif**: `"Arial"`, `"Helvetica"`, `"Verdana"`, `"Tahoma"`.
- **Serif**: `"Times New Roman"`, `"Georgia"`, `"Palatino"`.

#### Input Widget Sizes

```ini
UI_SPINBOX_WIDTH=10
UI_ENTRY_WIDTH=25
```

- **UI_SPINBOX_WIDTH**: Width of spinbox widgets (characters)
- **UI_ENTRY_WIDTH**: Width of text entry fields (characters)

#### Data Preview (Text Widget)

```ini
UI_TEXT_SELECT_BG="steel blue"
```

- **UI_TEXT_SELECT_BG**: Background color for selected text in the data preview. Text and selection foreground use **UI_FOREGROUND**; the preview background is derived from the main UI background.

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

These settings control the appearance of generated plots (both Tkinter and Streamlit).

### Figure Dimensions

```ini
PLOT_FIGSIZE_WIDTH=12
PLOT_FIGSIZE_HEIGHT=6
DPI=100
```

- **PLOT_FIGSIZE_WIDTH**: Width in inches
- **PLOT_FIGSIZE_HEIGHT**: Height in inches
- **DPI**: Resolution (dots per inch)

**Recommendations**:
- **Screen display**: 100 DPI.
- **High-quality prints**: 300 DPI.
- **Publications**: 600 DPI.

### Title Display

```ini
PLOT_SHOW_TITLE=false
```

- **PLOT_SHOW_TITLE**: Whether to show the plot title
  - `true`: Show title (uses the plot filename)
  - `false`: Hide title (cleaner appearance)

### Fitted Curve Style

```ini
PLOT_LINE_COLOR="black"
PLOT_LINE_WIDTH=1.0
PLOT_LINE_STYLE="-."
```

- **PLOT_LINE_COLOR**: Color of the fitted curve line
- **PLOT_LINE_WIDTH**: Width of the fitted curve line (points)
- **PLOT_LINE_STYLE**: Line style

**Line Style Options**:
- `"-"`: Solid line.
- `"--"`: Dashed line.
- `"-."`: Dash-dot line (default).
- `":"`: Dotted line.

### Data Points Style

```ini
PLOT_MARKER_FORMAT="o"
PLOT_MARKER_SIZE=5
```

- **PLOT_MARKER_FORMAT**: Shape of data point markers
- **PLOT_MARKER_SIZE**: Size of markers (points)

**Marker Format Options** (allowed values): `"o"` (circle, default), `"s"` (square), `"^"` (triangle up), `"d"` (diamond), `"*"` (star).

### Colors for Data Points

```ini
PLOT_ERROR_COLOR="crimson"
PLOT_MARKER_FACE_COLOR="crimson"
PLOT_MARKER_EDGE_COLOR="crimson"
```

- **PLOT_ERROR_COLOR**: Color of error bars
- **PLOT_MARKER_FACE_COLOR**: Fill color of markers
- **PLOT_MARKER_EDGE_COLOR**: Edge color of markers

**Common Color Names**:
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

Control text appearance in plots.

### Font Family

```ini
FONT_FAMILY="serif"
```

**Options**:
- `serif`: Times-like fonts (professional, traditional).
- `sans-serif`: Arial-like fonts (modern, clean).
- `monospace`: Courier-like fonts (technical).
- `cursive`: Script-like fonts (decorative).
- `fantasy`: Decorative fonts (artistic).

### Title Font

```ini
FONT_TITLE_SIZE="xx-large"
FONT_TITLE_WEIGHT="semibold"
```

- **FONT_TITLE_SIZE**: Size of plot title

**Size Options**: 
`xx-small`, `x-small`, `small`, `medium`, `large`, `x-large`, `xx-large`

- **FONT_TITLE_WEIGHT**: Boldness of plot title

**Weight Options**:
`normal`, `light`, `semibold`, `bold`, `heavy`

### Axis Labels

```ini
FONT_AXIS_SIZE=30
FONT_AXIS_STYLE="italic"
```

- **FONT_AXIS_SIZE**: Font size for axis labels (points)
- **FONT_AXIS_STYLE**: Font style for axis labels

**Style Options**:
- `normal`: Regular text.
- `italic`: Slanted text (traditional for variables).
- `oblique`: Slanted text (similar to italic).

### Tick Labels

```ini
FONT_TICK_SIZE=16
```

- **FONT_TICK_SIZE**: Font size for axis tick numbers (points)

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

Control where RegressionLab looks for input data and saves output plots.

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
- Relative path (relative to RegressionLab root): `"input"`, `"data"`, `"experiments"`.
- Absolute path: `"/home/user/data"`, `"C:\\Users\\Name\\Documents\\Data"`.

### Output Directory

```ini
FILE_OUTPUT_DIR="output"
```

**Options**:
- Relative path: `"output"`, `"results"`, `"plots"`.
- Absolute path: `"/home/user/results"`, `"C:\\Users\\Name\\Documents\\Results"`.

**Note**: The directory will be created automatically if it doesn't exist.

### Filename Template

```ini
FILE_FILENAME_TEMPLATE="fit_{}"
```

The `{}` placeholder is replaced with the plot name. The file extension is added automatically from **FILE_PLOT_FORMAT** (e.g. `.png`).

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

- **png**: Default; good balance of quality and size.
- **jpg**: Smaller files; use when PDF is not needed.
- **pdf**: Vector-style output for publications; in-app preview may still use PNG.

---

## 6. Links (Optional)

```ini
DONATIONS_URL="https://www.youtube.com/@whenphysics"
```

- **DONATIONS_URL**: URL shown in the desktop app’s **Information** (help) dialog as a “Donations” button. Leave empty or set to your own link. Only affects the Tkinter interface.

---

## 7. Logging Configuration

Control how RegressionLab logs information, warnings, and errors.

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
- `DEBUG`: Detailed diagnostic information (for development).
- `INFO`: General informational messages (default).
- `WARNING`: Warning messages only.
- `ERROR`: Error messages only.
- `CRITICAL`: Critical errors only.

**Recommendation**: Use `INFO` for normal operation, `DEBUG` for troubleshooting.

### Log File

```ini
LOG_FILE=regressionlab.log
```

- Relative or absolute path to log file
- Logs are appended to this file
- File is created automatically if it doesn't exist

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

- `true`: Print log messages to console/terminal
- `false`: Only write to log file (default)

**Recommendation**: Use `true` for development, `false` for production or when running from the GUI.

---

## Applying Configuration Changes

### For Tkinter (Desktop Version)

You can change configuration in either of these ways:

- **From the configuration menu**: Main menu → **Configure** (Configurar). Edit the values in the dialog and save; the application will restart automatically.
- **By editing `.env`**: Edit the `.env` file, save it, then restart the application:

```bash
# Restart the application
python src/main_program.py
```

### For Streamlit (Web Version)

1. Edit `.env` file
2. Save the changes
3. Reload the Streamlit app in your browser (usually Ctrl+R or Cmd+R)

**Note**: Some changes may require stopping and restarting the Streamlit server:

```bash
# Stop: Ctrl+C in terminal
# Restart:
streamlit run src/streamlit_app/app.py
```

---

## Common Configuration Scenarios

### Scenario 1: Preparing Plots for Publication

```ini
# High-resolution black and white plots
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

### Scenario 2: Quick Data Exploration

```ini
# Fast rendering, colorful display
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

### Scenario 3: Debugging Issues

```ini
# Detailed logging for troubleshooting
LOG_LEVEL=DEBUG
LOG_CONSOLE=true
LOG_FILE=debug.log
```

(Set **LOG_CONSOLE** to `true` to see logs in the terminal.)

### Scenario 4: Batch Processing

```ini
# Optimized for processing many files
DPI=150
FILE_OUTPUT_DIR="batch_results"
LOG_LEVEL=WARNING
LOG_CONSOLE=false
```

---

## Troubleshooting Configuration

### Changes Not Applied

**Problem**: Modified `.env` but see no changes

**Solutions**:
1. Ensure you saved the `.env` file.
2. Restart the application completely.
3. Check for syntax errors in `.env`.
4. Verify `.env` is in the correct location (RegressionLab root).

### Invalid Color Names

**Problem**: Error about invalid color

**Solutions**:
1. Use quotes around color names: `"midnight blue"` not `midnight blue`.
2. Use valid color names or hex codes.
3. Check spelling of color names.

### Font Not Found

**Problem**: Specified font doesn't appear

**Solutions**:
1. Verify the font is installed on your system.
2. Use a generic font family (`serif`, `sans-serif`, `monospace`).
3. Check font name spelling.

### Path Issues

**Problem**: Can't find input/output directories

**Solutions**:
1. Use forward slashes (`/`) even on Windows, or escape backslashes (`\\`).
2. Ensure directories exist or will be created.
3. Check file permissions.
4. Use absolute paths if relative paths don't work.

---

## Default Configuration

If you want to reset to default settings, simply copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Or delete `.env` and let RegressionLab use built-in defaults.

---

## Next Steps

- **Customize your plots**: Try different [plot styles](#3-plot-style-configuration)
- **Create a theme**: Design a [UI theme](#2-ui-theme-configuration) that matches your preferences
- **Learn advanced usage**: Read the [Extending RegressionLab](extending.md) guide

---

*Need more help? Check the [Troubleshooting Guide](troubleshooting.md) or open an issue on GitHub.*
