# Configuration Guide

RegressionLab is highly customizable through the `.env` configuration file. This guide explains all available configuration options and how to modify them.

## Getting Started with Configuration

### Locating the Configuration File

The configuration file is located in the root directory of RegressionLab:
```
RegressionLab/
  .env          ← Your configuration file
  .env.example  ← Template with all options
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
- **Visual Studio Code**: `code .env`
- **Nano** (Linux/macOS): `nano .env`
- **Notepad** (Windows): `notepad .env`
- **Vim**: `vim .env`

## Configuration Sections

The `.env` file is organized into logical sections:

1. [Language Configuration](#1-language-configuration)
2. [UI Theme Configuration](#2-ui-theme-configuration)
3. [Plot Style Configuration](#3-plot-style-configuration)
4. [Font Configuration](#4-font-configuration)
5. [File Path Configuration](#5-file-path-configuration)
6. [Logging Configuration](#6-logging-configuration)

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
- Changes all UI text, dialogs, and messages
- Affects both Tkinter and Streamlit interfaces
- Does not affect data or plot labels

**Note**: Language changes require restarting the application.

---

## 2. UI Theme Configuration

These settings control the appearance of the Tkinter desktop application. They do not affect the Streamlit web version.

### Color Settings

#### Background and Foreground

```ini
UI_BACKGROUND="midnight blue"
UI_FOREGROUND="snow"
```

- **UI_BACKGROUND**: Main window background color
- **UI_FOREGROUND**: Text color

**Color Options**:
- **Named colors**: `"white"`, `"black"`, `"navy"`, `"crimson"`, etc.
- **Hex codes**: `"#2C3E50"`, `"#FF5733"`, etc.
- **RGB tuples**: Not supported in .env file

#### Button Colors

```ini
UI_BUTTON_FG="lime green"
UI_BUTTON_FG_CANCEL="red2"
```

- **UI_BUTTON_FG**: Color for normal button text
- **UI_BUTTON_FG_CANCEL**: Color for cancel/exit button text

#### Active Colors (Hover/Click)

```ini
UI_ACTIVE_BG="navy"
UI_ACTIVE_FG="snow"
```

- **UI_ACTIVE_BG**: Background when button is hovered/clicked
- **UI_ACTIVE_FG**: Text color when button is hovered/clicked

### Layout Settings

#### Border and Relief

```ini
UI_BORDER_WIDTH=8
UI_RELIEF="ridge"
```

- **UI_BORDER_WIDTH**: Width of borders around widgets (pixels)
- **UI_RELIEF**: 3D effect style

**Relief Options**:
- `flat`: No 3D effect
- `raised`: Appears raised above surface
- `sunken`: Appears pressed into surface
- `groove`: Appears to have a groove around it
- `ridge`: Appears to have a ridge around it (default)

#### Padding

```ini
UI_PADDING_X=8
UI_PADDING_Y=8
```

- **UI_PADDING_X**: Horizontal spacing between widgets (pixels)
- **UI_PADDING_Y**: Vertical spacing between widgets (pixels)

### Widget Sizes

#### Button Dimensions

```ini
UI_BUTTON_WIDTH=12
UI_BUTTON_WIDTH_WIDE=28
```

- **UI_BUTTON_WIDTH**: Width for normal buttons (in characters)
- **UI_BUTTON_WIDTH_WIDE**: Width for wide buttons (in characters)

#### Font Settings

```ini
UI_FONT_SIZE=16
UI_FONT_SIZE_LARGE=20
UI_FONT_FAMILY="Menlo"
```

- **UI_FONT_SIZE**: Standard UI font size (points)
- **UI_FONT_SIZE_LARGE**: Large UI font size (points)
- **UI_FONT_FAMILY**: Font family for UI text

**Common Font Families**:
- **Monospace**: `"Courier"`, `"Courier New"`, `"Menlo"`, `"Monaco"`
- **Sans-serif**: `"Arial"`, `"Helvetica"`, `"Verdana"`, `"Tahoma"`
- **Serif**: `"Times New Roman"`, `"Georgia"`, `"Palatino"`

#### Input Widget Sizes

```ini
UI_SPINBOX_WIDTH=10
UI_ENTRY_WIDTH=25
```

- **UI_SPINBOX_WIDTH**: Width of spinbox widgets (characters)
- **UI_ENTRY_WIDTH**: Width of text entry fields (characters)

#### Data Preview (Text Widget)

The data preview window uses a separate style so you can keep a terminal-like or readable font/size:

```ini
UI_TEXT_BG="gray15"
UI_TEXT_FG="light cyan"
UI_TEXT_FONT_FAMILY="Consolas"
UI_TEXT_FONT_SIZE=11
UI_TEXT_INSERT_BG="spring green"
UI_TEXT_SELECT_BG="steel blue"
UI_TEXT_SELECT_FG="white"
```

- **UI_TEXT_BG** / **UI_TEXT_FG**: Background and text color for the data preview
- **UI_TEXT_FONT_FAMILY** / **UI_TEXT_FONT_SIZE**: Font for the preview (e.g. monospace, smaller size)
- **UI_TEXT_INSERT_BG**: Cursor color
- **UI_TEXT_SELECT_BG** / **UI_TEXT_SELECT_FG**: Selection highlight colors

### Example Themes

#### Professional Dark Theme
```ini
UI_BACKGROUND="#1e1e1e"
UI_FOREGROUND="#d4d4d4"
UI_BUTTON_FG="#00ff00"
UI_BUTTON_FG_CANCEL="#ff4444"
UI_ACTIVE_BG="#2d2d30"
UI_ACTIVE_FG="#ffffff"
UI_BORDER_WIDTH=6
UI_RELIEF="flat"
```

#### Classic Light Theme
```ini
UI_BACKGROUND="white"
UI_FOREGROUND="black"
UI_BUTTON_FG="blue"
UI_BUTTON_FG_CANCEL="red"
UI_ACTIVE_BG="lightgray"
UI_ACTIVE_FG="black"
UI_BORDER_WIDTH=4
UI_RELIEF="raised"
```

#### Ocean Theme
```ini
UI_BACKGROUND="#001f3f"
UI_FOREGROUND="#7FDBFF"
UI_BUTTON_FG="#39CCCC"
UI_BUTTON_FG_CANCEL="#FF851B"
UI_ACTIVE_BG="#0074D9"
UI_ACTIVE_FG="white"
UI_BORDER_WIDTH=8
UI_RELIEF="groove"
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
- **Screen display**: 100 DPI
- **High-quality prints**: 300 DPI
- **Publications**: 600 DPI

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
PLOT_LINE_WIDTH=1.00
PLOT_LINE_STYLE="-"
```

- **PLOT_LINE_COLOR**: Color of the fitted curve line
- **PLOT_LINE_WIDTH**: Width of the fitted curve line (points)
- **PLOT_LINE_STYLE**: Line style

**Line Style Options**:
- `"-"`: Solid line (default)
- `"--"`: Dashed line
- `"-."`: Dash-dot line
- `":"`: Dotted line

### Data Points Style

```ini
PLOT_MARKER_FORMAT="o"
PLOT_MARKER_SIZE=5
```

- **PLOT_MARKER_FORMAT**: Shape of data point markers
- **PLOT_MARKER_SIZE**: Size of markers (points)

**Marker Format Options**:
- `"o"`: Circle (default)
- `"s"`: Square
- `"^"`: Triangle (up)
- `"v"`: Triangle (down)
- `"d"`: Diamond
- `"*"`: Star
- `"+"`: Plus
- `"x"`: X mark

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
- Basic: `"red"`, `"blue"`, `"green"`, `"black"`, `"white"`
- Extended: `"crimson"`, `"navy"`, `"teal"`, `"gold"`, `"orange"`
- Scientific: `"darkblue"`, `"darkgreen"`, `"darkred"`

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
- `serif`: Times-like fonts (professional, traditional)
- `sans-serif`: Arial-like fonts (modern, clean)
- `monospace`: Courier-like fonts (technical)
- `cursive`: Script-like fonts (decorative)
- `fantasy`: Decorative fonts (artistic)

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
- `normal`: Regular text
- `italic`: Slanted text (traditional for variables)
- `oblique`: Slanted text (similar to italic)

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
FILE_FILENAME_TEMPLATE="fit_{}.png"
```

### Input Directory

```ini
FILE_INPUT_DIR="input"
```

**Options**:
- Relative path (relative to RegressionLab root): `"input"`, `"data"`, `"experiments"`
- Absolute path: `"/home/user/data"`, `"C:\\Users\\Name\\Documents\\Data"`

### Output Directory

```ini
FILE_OUTPUT_DIR="output"
```

**Options**:
- Relative path: `"output"`, `"results"`, `"plots"`
- Absolute path: `"/home/user/results"`, `"C:\\Users\\Name\\Documents\\Results"`

**Note**: The directory will be created automatically if it doesn't exist.

### Filename Template

```ini
FILE_FILENAME_TEMPLATE="fit_{}.png"
```

The `{}` placeholder will be replaced with the plot name.

**Examples**:
```ini
# Default
FILE_FILENAME_TEMPLATE="fit_{}.png"
# Result: fit_experiment1.png

# With prefix and date
FILE_FILENAME_TEMPLATE="regression_{}_2026.png"
# Result: regression_experiment1_2026.png

# Different extension (not recommended)
FILE_FILENAME_TEMPLATE="{}_result.jpg"
# Result: experiment1_result.jpg
```

---

## 6. Logging Configuration

Control how RegressionLab logs information, warnings, and errors.

```ini
LOG_LEVEL=INFO
LOG_FILE=regressionlab.log
LOG_CONSOLE=true
```

### Log Level

```ini
LOG_LEVEL=INFO
```

**Options** (from most to least verbose):
- `DEBUG`: Detailed diagnostic information (for development)
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only
- `CRITICAL`: Critical errors only

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
LOG_CONSOLE=true
```

- `true`: Print log messages to console/terminal
- `false`: Only write to log file

**Recommendation**: Keep `true` for development, use `false` for production deployments.

---

## Applying Configuration Changes

### For Tkinter (Desktop Version)

1. Edit `.env` file
2. Save the changes
3. Restart the application

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
1. Ensure you saved the `.env` file
2. Restart the application completely
3. Check for syntax errors in `.env`
4. Verify `.env` is in the correct location (RegressionLab root)

### Invalid Color Names

**Problem**: Error about invalid color

**Solutions**:
1. Use quotes around color names: `"midnight blue"` not `midnight blue`
2. Use valid color names or hex codes
3. Check spelling of color names

### Font Not Found

**Problem**: Specified font doesn't appear

**Solutions**:
1. Verify the font is installed on your system
2. Use a generic font family (`serif`, `sans-serif`, `monospace`)
3. Check font name spelling

### Path Issues

**Problem**: Can't find input/output directories

**Solutions**:
1. Use forward slashes (`/`) even on Windows, or escape backslashes (`\\`)
2. Ensure directories exist or will be created
3. Check file permissions
4. Use absolute paths if relative paths don't work

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
