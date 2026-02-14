# plotting.plot_utils

Plot generation and styling utilities.

## Overview

The `plot_utils.py` module provides functions to create and save plots with experimental data and fitted curves. It handles:

- **2D fit plots**: Data with error bars and fitted curve (`create_plot`). When `fit_info` is provided, the curve is evaluated on a dense linspace over the full x range for a smooth appearance.
- **Pair plots**: Grid of scatter plots for all pairs of variables (`create_pair_plots`)
- **Residual plots**: Residuals vs point index for multidimensional fits (`create_residual_plot`)
- **3D plots**: Data points and fitted surface for two independent variables (`create_3d_plot`). When `fit_info` is provided, the surface is evaluated on a regular grid of linspace points over the full x_0 and x_1 range for a smooth appearance.

All save functions use shared logic: the output directory is created if needed, and when saving as PDF a PNG preview is automatically generated for GUI use. Styling is driven by `config.PLOT_CONFIG` and `config.FONT_CONFIG` when not overridden.

## Key Functions

### Plot Creation

#### `create_plot(x, y, ux, uy, y_fitted, fit_name, x_name, y_name, plot_config=None, font_config=None, output_path=None, fit_info=None) -> str`

Create and save a plot with experimental data and fitted curve.

**Parameters:**
- `x`: Independent variable data (array-like)
- `y`: Dependent variable data (array-like)
- `ux`: Uncertainties in x (array-like)
- `uy`: Uncertainties in y (array-like)
- `y_fitted`: Fitted y values (array-like)
- `fit_name`: Name of the fit for plot title
- `x_name`: Label for x-axis
- `y_name`: Label for y-axis
- `plot_config`: Optional plot configuration dict (defaults to `PLOT_CONFIG`)
- `font_config`: Optional font configuration dict (defaults to `FONT_CONFIG`)
- `output_path`: Optional full path to save the plot. If None, uses `get_output_path(fit_name)`.
- `fit_info`: Optional dict with `fit_func` and `params` to evaluate the fitted function on a dense linspace (300 points) over the full x range. When provided, yields a smoother curve; if None, plots at the original x points.

**Returns:**
- Path to the saved plot file (as string)

**Raises:**
- `Exception`: If plot creation or saving fails

**Example:**
```python
from plotting.plot_utils import create_plot
import numpy as np
import pandas as pd

# Prepare data
data = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [2.1, 4.2, 6.1, 8.0, 10.1],
    'ux': [0.1] * 5,
    'uy': [0.2] * 5
})

# Fitted values
y_fitted = np.array([2, 4, 6, 8, 10])

# Create plot
plot_path = create_plot(
    x=data['x'],
    y=data['y'],
    ux=data['ux'],
    uy=data['uy'],
    y_fitted=y_fitted,
    fit_name='Linear Fit',
    x_name='Time (s)',
    y_name='Distance (m)'
)

print(f"Plot saved to: {plot_path}")
```

#### `create_pair_plots(data, variable_names, plot_config=None, font_config=None, output_path=None) -> str | Figure`

Create a grid of scatter plots for all pairs of variables (pair plot / scatter matrix). Each cell has a minimum size (1.4 in) so many variables remain readable. The Streamlit and Tkinter UIs limit to 10 variables when there are more, via a multiselect or selection dialog.

**Parameters:**
- `data`: DataFrame or dict-like with numeric columns
- `variable_names`: List of column names to use (must exist and be numeric)
- `plot_config`: Optional; defaults to `PLOT_CONFIG`
- `font_config`: Optional; defaults to `FONT_CONFIG`
- `output_path`: If given, save figure and return path (str). If `None`, return the matplotlib Figure for inline display (e.g. Streamlit)

**Returns:** Path to the saved image (str) if `output_path` was set; otherwise the Figure instance.

---

#### `create_residual_plot(residuals, point_indices, fit_name, plot_config=None, font_config=None, output_path=None) -> str`

Create a residual plot for multidimensional fitting (residuals vs point index).

**Parameters:** `residuals`, `point_indices`, `fit_name`, optional `plot_config`, `font_config`, `output_path` (if `None`, uses `get_output_path(fit_name)`).

**Returns:** Path to the saved plot file (str).

---

#### `create_3d_plot(x, y, z, z_fitted, fit_name, x_name, y_name, z_name, plot_config=None, font_config=None, output_path=None, interactive=False, fit_info=None) -> str | tuple[str, Figure]`

Create a 3D plot with data points and fitted surface mesh for two independent variables.

**Parameters:** `x`, `y`, `z`, `z_fitted`, `fit_name`, `x_name`, `y_name`, `z_name`, optional config and path. If `interactive=True`, returns `(save_path, figure)` for embedding in a window (e.g. rotatable with mouse) instead of saving and closing. `fit_info`: Optional dict with `fit_func` and `params` to evaluate the fitted function on a regular grid (50×50) of linspace points over the full x_0 and x_1 range; when provided, yields a smoother surface.

**Returns:** Path (str) when `interactive=False`; `(save_path, figure)` when `interactive=True`.

**Note:** When `fit_info` is provided, the surface is evaluated on the grid. Otherwise, `scipy.interpolate.griddata` is used when scipy is available; a vectorized nearest-neighbor fallback is used without scipy.

## Plot Components

### Fitted Curve

- **Line**: Smooth curve showing the fitted function. When `fit_info` is provided, the curve is evaluated on 300 linspace points over the full x range; otherwise it is drawn at the original data points.
- **Color**: Configurable via `plot_config['line_color']`
- **Width**: Configurable via `plot_config['line_width']`
- **Style**: Configurable via `plot_config['line_style']`

### Experimental Data

- **Markers**: Data points with error bars
- **Format**: Configurable via `plot_config['marker_format']`
- **Size**: Configurable via `plot_config['marker_size']`
- **Colors**: 
  - Face: `plot_config['marker_face_color']`
  - Edge: `plot_config['marker_edge_color']`
  - Error bars: `plot_config['error_color']`

### Axes and Labels

- **X-axis**: Label from `x_name` parameter
- **Y-axis**: Label from `y_name` parameter
- **Title**: Optional, from `fit_name` if `plot_config['show_title']` is True
- **Grid**: Optional, from `plot_config['show_grid']` (default False)
- **Fonts**: Configured via `font_config`

## Configuration

### Plot Configuration

Plot settings can be customized via `plot_config` dictionary:

```python
plot_config = {
    'figsize': (12, 6),           # Figure size (width, height)
    'dpi': 100,                   # Resolution
    'line_color': 'black',         # Fitted curve color
    'line_width': 2,              # Fitted curve width
    'line_style': '-',            # Line style ('-', '--', ':', etc.)
    'marker_format': 'o',         # Marker style ('o', 's', '^', etc.)
    'marker_size': 8,             # Marker size
    'marker_face_color': 'blue',  # Marker fill color
    'marker_edge_color': 'black', # Marker edge color
    'error_color': 'red',        # Error bar color
    'show_title': False,          # Show plot title
    'show_grid': False            # Show background grid on plot
}
```

### Font Configuration

Font settings can be customized via `font_config` dictionary:

```python
font_config = {
    'tick_size': 12,              # Tick label size
    'label_size': 14,             # Axis label size
    'title_size': 16              # Title size
}
```

### Using Default Configuration

If `plot_config` or `font_config` are `None`, the function uses default values from `config.PLOT_CONFIG` and `config.FONT_CONFIG`:

```python
from plotting.plot_utils import create_plot

# Uses default configuration
plot_path = create_plot(
    x=x_data, y=y_data, ux=ux_data, uy=uy_data,
    y_fitted=y_fitted, fit_name='Fit', x_name='x', y_name='y'
)
```

### Custom Configuration

```python
from plotting.plot_utils import create_plot

# Custom plot configuration
custom_plot_config = {
    'figsize': (10, 8),
    'dpi': 150,
    'line_color': 'red',
    'marker_format': 's',
    'show_title': True
}

custom_font_config = {
    'tick_size': 14,
    'label_size': 16
}

plot_path = create_plot(
    x=x_data, y=y_data, ux=ux_data, uy=uy_data,
    y_fitted=y_fitted, fit_name='Custom Fit',
    x_name='X Variable', y_name='Y Variable',
    plot_config=custom_plot_config,
    font_config=custom_font_config
)
```

## Output Path

### Automatic Path Generation

If `output_path` is `None`, the function automatically generates a path using `config.get_output_path(fit_name)`:

```python
# Automatically saves to: output/fit_name.png
plot_path = create_plot(..., fit_name='my_fit', ...)
```

### Custom Output Path

```python
from pathlib import Path

# Custom output path
custom_path = Path('results') / 'experiment1.png'
plot_path = create_plot(
    ...,
    output_path=str(custom_path)
)
```

## Usage Examples

### Basic Plot

```python
from plotting.plot_utils import create_plot
import numpy as np
import pandas as pd

# Load data
data = pd.read_csv('input/experiment.csv')

# Perform fit (example)
y_fitted = 2 * data['x']  # Simple linear fit

# Create plot
plot_path = create_plot(
    x=data['x'],
    y=data['y'],
    ux=data['ux'],
    uy=data['uy'],
    y_fitted=y_fitted,
    fit_name='Linear Fit',
    x_name='Time (s)',
    y_name='Distance (m)'
)
```

### High-Resolution Plot

```python
from plotting.plot_utils import create_plot

high_res_config = {
    'figsize': (16, 10),
    'dpi': 300,  # High resolution
    'line_width': 3,
    'marker_size': 10
}

plot_path = create_plot(
    x=x_data, y=y_data, ux=ux_data, uy=uy_data,
    y_fitted=y_fitted, fit_name='Publication Quality',
    x_name='X', y_name='Y',
    plot_config=high_res_config
)
```

### Custom Styling

```python
from plotting.plot_utils import create_plot

# Custom colors and styles
custom_config = {
    'line_color': '#2E86AB',      # Blue
    'line_width': 2.5,
    'line_style': '--',           # Dashed line
    'marker_format': 'o',
    'marker_size': 10,
    'marker_face_color': '#A23B72',  # Purple
    'marker_edge_color': 'black',
    'error_color': '#F18F01',     # Orange
    'show_title': True
}

plot_path = create_plot(
    x=x_data, y=y_data, ux=ux_data, uy=uy_data,
    y_fitted=y_fitted, fit_name='Custom Styled Fit',
    x_name='X Variable', y_name='Y Variable',
    plot_config=custom_config
)
```

## Integration with Fitting

The plot utility is typically used after performing a fit:

```python
from fitting.fitting_utils import get_fitting_function
from plotting.plot_utils import create_plot

# Get fitting function
fit_func = get_fitting_function('linear_function')

# Perform fit (returns text, y_fitted, equation, fit_info)
result = fit_func(data, 'x', 'y')
text, y_fitted, equation = result[0], result[1], result[2]
fit_info = result[3] if len(result) >= 4 else None

# Create plot (fit_info enables smooth curve via linspace evaluation)
plot_path = create_plot(
    x=data['x'],
    y=data['y'],
    ux=data['ux'],
    uy=data['uy'],
    y_fitted=y_fitted,
    fit_name='Linear Fit',
    x_name='X', y_name='Y',
    fit_info=fit_info,
)
```

## Error Handling

### Plot Creation Errors

```python
from plotting.plot_utils import create_plot

try:
    plot_path = create_plot(
        x=x_data, y=y_data, ux=ux_data, uy=uy_data,
        y_fitted=y_fitted, fit_name='Fit',
        x_name='X', y_name='Y'
    )
except Exception as e:
    print(f"Failed to create plot: {e}")
    # Cleanup any open figures
    import matplotlib.pyplot as plt
    plt.close('all')
```

## Best Practices

1. **Consistent Styling**: Use the same `plot_config` across multiple plots
   ```python
   # Define once
   PLOT_STYLE = {
       'figsize': (12, 6),
       'dpi': 100,
       # ... other settings
   }
   
   # Reuse
   plot1 = create_plot(..., plot_config=PLOT_STYLE)
   plot2 = create_plot(..., plot_config=PLOT_STYLE)
   ```

2. **Error Bar Handling**: Always provide uncertainty arrays (use zeros if unavailable)
   ```python
   # If uncertainties not available
   ux = [0.0] * len(x)
   uy = [0.0] * len(y)
   ```

3. **Output Directory**: The plotting functions create the output directory automatically when saving; you do not need to create it beforehand.

4. **Resource Cleanup**: Figures are closed automatically after saving. Only call `plt.close('all')` when handling errors (e.g. in an except block) to clean up any open figures.

## Technical Details

### Saving and Output

- **Format**: Save format is determined by the file extension in `output_path` (e.g. PNG, PDF).
- **PDF preview**: When the output path has a `.pdf` extension, a PNG preview file (`*_preview.png`) is automatically written in the same directory for use in GUIs.
- **Directory creation**: The parent directory of the save path is created automatically (`parents=True`, `exist_ok=True`).
- **Shared logic**: All plot-saving functions use an internal helper so that save behavior and preview generation are consistent.

### Matplotlib Integration

- Uses `matplotlib.pyplot` for plotting
- Creates figure with specified size and DPI from `plot_config`
- Saves with `bbox_inches='tight'` and configured DPI
- Automatically closes figures after saving (unless returning the figure for interactive use, e.g. pair plot without path or 3D with `interactive=True`)

### Font Configuration

- Uses `config.setup_fonts()` for font configuration
- Supports custom font properties via `font_config`
- Handles font fallbacks gracefully

### 3D Plots and Optional SciPy

- **With fit_info**: The 3D fitted surface is evaluated on a 50×50 grid of linspace points over the full x_0 and x_1 range, yielding a smooth surface.
- **Without fit_info**: With scipy, 3D fitted surface uses `scipy.interpolate.griddata` (linear interpolation, with nearest-neighbor fill outside the convex hull).
- **Without scipy**: A vectorized nearest-neighbor interpolation over the grid is used so 3D plots still work without scipy.

### Performance

- Single figure creation per call
- Efficient memory usage
- Fast rendering for typical data sizes (< 10,000 points)
- Pair plot and 3D fallback use vectorized operations where applicable

---

*For more information about plotting, see [Usage Guide](../usage.md).*
