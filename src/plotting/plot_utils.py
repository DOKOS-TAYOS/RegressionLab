import matplotlib.pyplot as plt
from config import PLOT_CONFIG, FONT_CONFIG, setup_fonts, get_output_path
from utils.logger import get_logger

logger = get_logger(__name__)

def create_plot(x: list[float], y: list[float], ux: list[float], uy: list[float], 
                y_fitted: list[float], fit_name: str, x_name: str, y_name: str, 
                plot_config: dict | None = None, font_config: dict | None = None) -> str:
    """
    Create and save a plot with experimental data and fitted curve.
    
    Args:
        x: Independent variable data (array-like)
        y: Dependent variable data (array-like)
        ux: Uncertainties in x (array-like)
        uy: Uncertainties in y (array-like)
        y_fitted: Fitted y values (array-like)
        fit_name: Name of the fit for plot title
        x_name: Label for x-axis
        y_name: Label for y-axis
        plot_config: Optional plot configuration dict (defaults to PLOT_CONFIG)
        font_config: Optional font configuration dict (defaults to FONT_CONFIG)
    
    Returns:
        Path to the saved plot file
        
    Raises:
        Exception: If plot creation or saving fails
    """
    logger.info(f"Creating plot: {fit_name}")
    logger.debug(f"Data points: {len(x)}, x_label: {x_name}, y_label: {y_name}")
    
    try:
        # Use default configurations if not provided
        if plot_config is None:
            plot_config = PLOT_CONFIG
        if font_config is None:
            font_config = FONT_CONFIG
        
        # Setup fonts
        fontt, fonta = setup_fonts()
        logger.debug("Fonts configured")
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=plot_config['figsize'])
        logger.debug(f"Figure created with size: {plot_config['figsize']}")
        
        # Plot fitted line first (so it appears behind data points)
        ax.plot(x, y_fitted, 
                color=plot_config['line_color'], 
                lw=plot_config['line_width'], 
                ls=plot_config['line_style'])
        
        # Plot data points with error bars
        ax.errorbar(x, y, 
                    fmt=plot_config['marker_format'],
                    markersize=plot_config['marker_size'], 
                    yerr=uy, 
                    xerr=ux, 
                    ecolor=plot_config['error_color'], 
                    markerfacecolor=plot_config['marker_face_color'], 
                    markeredgecolor=plot_config['marker_edge_color'])
        logger.debug("Data plotted")
        
        # Set labels with proper fonts
        ax.set_xlabel(x_name, fontproperties=fonta)
        ax.set_ylabel(y_name, fontproperties=fonta)
        
        # Set title if enabled in configuration
        if plot_config.get('show_title', False):
            ax.set_title(fit_name, fontproperties=fontt)
        
        # Set tick label font size for better visibility
        ax.tick_params(axis='both', which='major', labelsize=font_config['tick_size'])
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save plot with screen-appropriate quality
        output_path = get_output_path(fit_name)
        logger.debug(f"Saving plot to: {output_path}")
        plt.savefig(output_path, bbox_inches='tight', dpi=plot_config['dpi'])
        
        # Close figure to free memory
        plt.close(fig)
        
        logger.info(f"Plot saved successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create plot: {str(e)}", exc_info=True)
        # Clean up if figure was created
        try:
            plt.close('all')
        except:
            pass
        raise