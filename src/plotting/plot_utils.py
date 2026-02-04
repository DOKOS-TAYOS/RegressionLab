# Standard library
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# Third-party packages
import matplotlib.pyplot as plt

# Local imports
from config import FONT_CONFIG, PLOT_CONFIG, get_output_path, setup_fonts
from utils.logger import get_logger

logger = get_logger(__name__)


def create_pair_plots(
    data: Any,
    variable_names: List[str],
    plot_config: Optional[Dict[str, Any]] = None,
    font_config: Optional[Dict[str, Any]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Union[str, Any]:
    """
    Create a grid of scatter plots for all pairs of variables (pair plot).

    Args:
        data: DataFrame or dict-like with numeric columns.
        variable_names: List of column names to use (must be numeric).
        plot_config: Optional plot configuration dict. Defaults to PLOT_CONFIG.
        font_config: Optional font configuration dict. Defaults to FONT_CONFIG.
        output_path: If given, save figure to this path and return path (str).
            If None, return the Figure for inline display (e.g. Streamlit).

    Returns:
        If output_path is set: path to the saved image (str).
        Otherwise: matplotlib Figure instance.
    """
    import pandas as pd

    # Restrict to columns that exist and are numeric
    cols = [c for c in variable_names if c in data.columns]
    if hasattr(data, 'select_dtypes'):
        df = data[cols].select_dtypes(include=['number'])
    else:
        df = pd.DataFrame({c: data[c] for c in cols if c in data.columns})
        df = df.select_dtypes(include=['number'])
    names = list(df.columns)
    n = len(names)
    if n == 0:
        logger.warning("No numeric variables for pair plot")
        if output_path:
            return str(output_path)
        fig, _ = plt.subplots(1, 1, figsize=(4, 4))
        return fig
    if plot_config is None:
        plot_config = PLOT_CONFIG
    if font_config is None:
        font_config = FONT_CONFIG

    # Cap figure size so windows/layouts do not grow too large
    max_side = 12.0
    cell_inches = min(2.8, max_side / n)
    figsize = (cell_inches * n, cell_inches * n)

    if n == 1:
        # Single variable: one simple scatter (index vs value)
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        ax.set_facecolor('#f8f9fa')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.scatter(
            range(len(df[names[0]])),
            df[names[0]],
            alpha=0.7,
            s=28,
            c='#1f77b4',
            edgecolors='white',
            linewidths=0.5,
        )
        ax.set_xlabel(names[0], fontsize=10)
        ax.set_ylabel(names[0], fontsize=10)
        ax.tick_params(axis='both', labelsize=9)
        plt.tight_layout()
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, bbox_inches='tight', dpi=plot_config.get('dpi', 150))
            plt.close(fig)
            return str(output_path)
        return fig

    try:
        setup_fonts()
    except Exception:
        pass

    fig, axes = plt.subplots(n, n, figsize=figsize)
    fig.patch.set_facecolor('#fafafa')
    scatter_color = '#1f77b4'
    scatter_edge = 'white'
    for i in range(n):
        for j in range(n):
            ax = axes[i, j] if n > 1 else axes[0, 0]
            ax.set_facecolor('#f8f9fa')
            if i == j:
                ax.text(
                    0.5, 0.5, names[i],
                    ha='center', va='center',
                    fontsize=min(10, max(8, 14 - n)),
                    fontweight='bold',
                    color='#333',
                )
                ax.set_xticks([])
                ax.set_yticks([])
            else:
                xcol, ycol = names[j], names[i]
                ax.scatter(
                    df[xcol],
                    df[ycol],
                    alpha=0.65,
                    s=min(45, max(18, 80 - 8 * n)),
                    c=scatter_color,
                    edgecolors=scatter_edge,
                    linewidths=0.4,
                )
                ax.grid(True, linestyle='--', alpha=0.35)
                ax.set_xlabel(xcol, fontsize=min(9, max(7, 11 - n // 2)))
                ax.set_ylabel(ycol, fontsize=min(9, max(7, 11 - n // 2)))
                ax.tick_params(axis='both', labelsize=8)
            ax.set_aspect('auto')
    plt.tight_layout(pad=1.2, h_pad=1.0, w_pad=1.0)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches='tight', dpi=plot_config.get('dpi', 150))
        plt.close(fig)
        logger.info(f"Pair plot saved to {output_path}")
        return str(output_path)
    return fig


def create_plot(
    x: Sequence[float],
    y: Sequence[float],
    ux: Sequence[float],
    uy: Sequence[float],
    y_fitted: Sequence[float],
    fit_name: str,
    x_name: str,
    y_name: str,
    plot_config: Optional[Dict[str, Any]] = None,
    font_config: Optional[Dict[str, Any]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Create and save a plot with experimental data and fitted curve.

    Args:
        x: Independent variable data (array-like).
        y: Dependent variable data (array-like).
        ux: Uncertainties in x (array-like).
        uy: Uncertainties in y (array-like).
        y_fitted: Fitted y values (array-like).
        fit_name: Name of the fit for plot title.
        x_name: Label for x-axis.
        y_name: Label for y-axis.
        plot_config: Optional plot configuration dict. Defaults to PLOT_CONFIG.
        font_config: Optional font configuration dict. Defaults to FONT_CONFIG.
        output_path: Optional full path to save the plot. If None, uses get_output_path(fit_name).

    Returns:
        Path to the saved plot file (as string).

    Raises:
        OSError: If the plot file cannot be written.
        RuntimeError: If matplotlib fails during plot creation or saving.
    """
    logger.info(f"Creating plot: {fit_name}")
    logger.debug(f"Data points: {len(x)}, x_label: {x_name}, y_label: {y_name}")

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_path = str(output_path)
    else:
        save_path = get_output_path(fit_name)

    try:
        if plot_config is None:
            plot_config = PLOT_CONFIG
        if font_config is None:
            font_config = FONT_CONFIG

        fontt, fonta = setup_fonts()
        logger.debug("Fonts configured")

        fig, ax = plt.subplots(figsize=plot_config['figsize'])
        logger.debug(f"Figure created with size: {plot_config['figsize']}")

        ax.plot(
            x, y_fitted,
            color=plot_config['line_color'],
            lw=plot_config['line_width'],
            ls=plot_config['line_style'],
        )
        ax.errorbar(
            x, y,
            fmt=plot_config['marker_format'],
            markersize=plot_config['marker_size'],
            yerr=uy,
            xerr=ux,
            ecolor=plot_config['error_color'],
            markerfacecolor=plot_config['marker_face_color'],
            markeredgecolor=plot_config['marker_edge_color'],
        )
        logger.debug("Data plotted")

        ax.set_xlabel(x_name, fontproperties=fonta)
        ax.set_ylabel(y_name, fontproperties=fonta)

        if plot_config.get('show_title', False):
            ax.set_title(fit_name, fontproperties=fontt)

        ax.tick_params(axis='both', which='major', labelsize=font_config['tick_size'])
        plt.tight_layout()

        logger.debug(f"Saving plot to: {save_path}")
        plt.savefig(save_path, bbox_inches='tight', dpi=plot_config['dpi'])
        plt.close(fig)

        logger.info(f"Plot saved successfully: {save_path}")
        return save_path

    except Exception as e:
        logger.error(f"Failed to create plot: {str(e)}", exc_info=True)
        try:
            plt.close('all')
        except Exception:
            pass
        raise