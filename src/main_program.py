#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main Program - Data Fitting Application
Entry point for the curve fitting application with GUI interface.
"""
__author__ = "Alejandro Mata Ali"
__copyright__ = "Public content for science use"
__credits__ = ["Alejandro Mata Ali"]
__maintainer__ = "Alejandro Mata Ali"
__email__ = "alejandro.mata.ali@gmail.com"
__status__ = "Beta"

# Standard library
import sys
from pathlib import Path
from tkinter import messagebox
from typing import Any, Callable, Optional

# Add src directory to Python path for proper imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Local imports (kept lightweight at startup; heavy modules are loaded lazily)
from config import AVAILABLE_EQUATION_TYPES, EXIT_SIGNAL, __version__
from i18n import t, initialize_i18n
from frontend.ui_main_menu import start_main_menu
from fitting.fitting_utils import get_fitting_function
from utils.exceptions import FittingError
from utils.logger import setup_logging, get_logger

# Initialize i18n and logging at module level
initialize_i18n()
setup_logging()
logger = get_logger(__name__)


# ============================================================================
# APPLICATION STATE
# ============================================================================

class ApplicationState:
    """
    Encapsulates application state instead of using global variables.
    
    This class manages the current state of the application, particularly
    tracking which equation type is currently selected and ready for use.
    
    Using a class for state management (instead of module-level globals)
    provides better:

        - Testability: Easy to create fresh state for tests
        - Encapsulation: State changes go through methods
        - Clarity: All state in one place
    
    Attributes:
        menu_window: Reference to the main Tkinter menu window
        current_equation: Name of the currently selected equation (e.g., 'linear_function')
        current_fitter: The fitting function wrapped with visualization
    """
    
    def __init__(self):
        """Initialize application state with default values."""
        self.menu_window = None
        self.current_equation: str = ''
        self.current_fitter: Optional[Callable] = None
    
    def set_equation(self, equation_name: str, fitter_function: Optional[Callable]) -> None:
        """
        Set the current equation and its fitter function.
        
        This is called after the user selects an equation type,
        storing it so it can be reused for multiple datasets.
        
        Args:
            equation_name: Internal name of the equation
            fitter_function: Function to perform fitting (with visualization)
        """
        self.current_equation = equation_name
        self.current_fitter = fitter_function
    
    def reset_equation(self) -> None:
        """
        Reset equation state to initial values.
        
        Called when starting a new fitting operation or
        when the user cancels equation selection.
        """
        self.current_equation = ''
        self.current_fitter = None


# Global application state instance
# This is the single source of truth for application state
app_state = ApplicationState()


# ============================================================================
# WORKFLOW FUNCTIONS - Main Menu Callbacks
# ============================================================================

def _get_menu_window() -> Optional[Any]:
    """Get the menu window from __main__ module."""
    import __main__
    return getattr(__main__, 'menu', None)


# Helper function to set equation and get fitter with visualization
def _set_equation_helper(equation_name: str) -> None:
    # Get backend fitting function
    base_fit = get_fitting_function(equation_name)
    if base_fit:
        # Wrap with frontend visualization
        display_name = equation_name.replace('_', ' ').title()
        fitter_with_ui = _wrap_with_visualization(base_fit, display_name)
        app_state.set_equation(equation_name, fitter_with_ui)

def _wrap_with_visualization(base_fit_function: Callable, fit_name: str) -> Callable:
    """
    Wrap a backend fitting function with frontend visualization.
    
    This decorator pattern keeps the separation between backend (calculations)
    and frontend (UI), allowing backend functions to be tested independently
    and reused in different contexts (GUI, CLI, web, etc.).
    
    The wrapper:
    1. Calls the backend function to get fit results
    2. Extracts data and uncertainties from the dataset
    3. Creates a plot with matplotlib
    4. Displays results in a Tkinter window
    
    Args:
        base_fit_function: Backend function that returns (text, y_fitted, equation)
        fit_name: Name of the fit for display in window title and plot
        
    Returns:
        Wrapped function that performs fitting and shows results
    """
    # Lazy import heavy modules only when visualization is actually needed
    from plotting.plot_utils import create_plot
    from frontend.ui_dialogs import create_result_window
    
    def wrapped_function(
        data: Any,
        x_name: str,
        y_name: str,
        plot_name: Optional[str] = None,
    ) -> None:
        """Execute fitting and display results."""
        try:
            # Backend: Perform the fitting calculation
            # Returns: parameter text, fitted y values, formatted equation
            text, y_fitted, equation = base_fit_function(data, x_name, y_name)
            
            # Extract data arrays for plotting
            # The application expects uncertainty columns to be named 'u<varname>'
            x = data[x_name]
            y = data[y_name]
            ux = data['u%s' % x_name]  # x uncertainty
            uy = data['u%s' % y_name]  # y uncertainty
            
            # Use plot_name for filename, fit_name for window title
            filename_base = plot_name if plot_name else fit_name
            
            # Frontend: Create visualization
            # 1. Create and save the plot as an image file
            output_path = create_plot(x, y, ux, uy, y_fitted, filename_base, x_name, y_name)
            # 2. Display the results in a Tkinter window
            window_title = plot_name if plot_name else fit_name
            create_result_window(window_title, text, equation, output_path)
        except FittingError as e:
            # Show error message when fitting fails due to scipy convergence issues
            messagebox.showerror(
                t('error.fitting_error'),
                t('error.fitting_failed_details', error=str(e))
            )
        except Exception as e:
            # Catch any other unexpected errors during fitting or visualization
            messagebox.showerror(
                t('error.fitting_error'),
                t('error.fitting_failed_generic', error_type=type(e).__name__, error=str(e))
            )
    
    return wrapped_function


def normal_fitting() -> None:
    """
    Perform a normal fitting operation with optional loop mode.
    
    This is the main fitting workflow that most users will use.
    It fits a single equation type to a single dataset.
    
    Workflow:
    1. User selects equation type (predefined or custom)
    2. User decides whether to enable loop mode
    3. User selects data file and variables
    4. Fit is performed and results displayed
    5. If loop mode: user can modify data and refit without restarting
    
    Loop mode is useful for:

        - Exploring different data subsets
        - Iteratively cleaning outliers
        - Testing sensitivity to data modifications
    """
    # Lazy imports to avoid loading heavy dependencies at application startup
    from fitting.workflow_controller import (
        single_fit_with_loop,
        coordinate_data_loading,
        coordinate_equation_selection,
    )
    from frontend.ui_dialogs import (
        ask_file_type,
        ask_file_name,
        ask_variables,
        ask_equation_type,
        ask_num_parameters,
        ask_parameter_names,
        ask_custom_formula,
    )

    logger.info(t('log.normal_fitting_workflow'))
    menu = _get_menu_window()
    
    # Phase 1: Equation Selection
    # Get the backend fitting function (returns calculation results only)
    equation_name, base_fit_function = coordinate_equation_selection(
        parent_window=menu,
        ask_equation_type_func=ask_equation_type,
        ask_num_parameters_func=ask_num_parameters,
        ask_parameter_names_func=ask_parameter_names,
        ask_custom_formula_func=ask_custom_formula,
        get_fitting_function_func=get_fitting_function
    )
    
    # User cancelled equation selection
    if equation_name == EXIT_SIGNAL or base_fit_function is None:
        logger.info(t('log.user_cancelled_equation'))
        return
    
    # Wrap backend function with frontend visualization layer
    display_name = equation_name.replace('_', ' ').title()
    fitter_with_ui = _wrap_with_visualization(base_fit_function, display_name)
    
    # Store current equation in app state
    app_state.set_equation(equation_name, fitter_with_ui)
    
    # Phase 2: Loop Mode Selection
    # Ask if user wants to enable loop mode (allows reloading and refitting)
    loop_mode = messagebox.askyesno(
        message=t('workflow.loop_question'), 
        title=t('workflow.normal_fitting_title')
    )
    
    # Phase 3: Data Loading
    # Load the dataset and get variable selections
    (
        data, x_name, y_name, plot_name, data_file_path, data_file_type
    ) = coordinate_data_loading(
        parent_window=menu,
        ask_file_type_func=ask_file_type,
        ask_file_name_func=ask_file_name,
        ask_variables_func=ask_variables
    )
    
    # Check if data was loaded successfully (empty string indicates cancellation)
    if isinstance(data, str):  # Empty result
        logger.info(t('log.user_cancelled_data'))
        return
    
    # Phase 4: Fitting Execution
    if loop_mode:
        # Loop mode: fit, show results, ask to continue, reload data, repeat
        single_fit_with_loop(
            fitter_function=fitter_with_ui,
            data=data,
            x_name=x_name,
            y_name=y_name,
            plot_name=plot_name,
            data_file_path=data_file_path,
            data_file_type=data_file_type
        )
    else:
        # Single mode: fit once and done
        fitter_with_ui(data, x_name, y_name, plot_name)

def single_fit_multiple_datasets() -> None:
    """
    Perform multiple fitting operations with the same equation on different datasets.
    
    Workflow:
    1. Select equation type
    2. Specify how many datasets to fit
    3. Load each dataset
    4. Perform fits on all datasets
    5. Optionally reload and refit in loop
    """
    # Lazy imports to avoid loading heavy dependencies at application startup
    from fitting.workflow_controller import (
        multiple_fit_with_loop,
        coordinate_data_loading,
        coordinate_equation_selection,
    )
    from frontend.ui_dialogs import (
        ask_file_type,
        ask_file_name,
        ask_variables,
        ask_equation_type,
        ask_num_parameters,
        ask_parameter_names,
        ask_custom_formula,
        ask_num_fits,
    )

    menu = _get_menu_window()
    
    # Select equation (backend function)
    equation_name, base_fit_function = coordinate_equation_selection(
        parent_window=menu,
        ask_equation_type_func=ask_equation_type,
        ask_num_parameters_func=ask_num_parameters,
        ask_parameter_names_func=ask_parameter_names,
        ask_custom_formula_func=ask_custom_formula,
        get_fitting_function_func=get_fitting_function
    )
    
    if equation_name == EXIT_SIGNAL or base_fit_function is None:
        return
    
    # Wrap backend function with frontend visualization
    display_name = equation_name.replace('_', ' ').title()
    fitter_with_ui = _wrap_with_visualization(base_fit_function, display_name)
    
    app_state.set_equation(equation_name, fitter_with_ui)
    
    # Ask for number of datasets
    num_datasets = ask_num_fits(menu)
    if num_datasets is None:
        return

    # Ask if user wants loop mode
    loop_mode = messagebox.askyesno(
        message=t('workflow.loop_question'), 
        title=t('workflow.multiple_fitting_title')
    )
    
    # Load all datasets
    datasets = []
    for i in range(num_datasets):
        # Check if user hasn't cancelled any previous load
        if not any(ds.get('file_type') == EXIT_SIGNAL for ds in datasets):
            (
                data, x_name, y_name, plot_name, data_file_path, data_file_type
            ) = coordinate_data_loading(
                parent_window=menu,
                ask_file_type_func=ask_file_type,
                ask_file_name_func=ask_file_name,
                ask_variables_func=ask_variables
            )
            
            if not isinstance(data, str):  # Data loaded successfully
                datasets.append({
                    'data': data,
                    'x_name': x_name,
                    'y_name': y_name,
                    'plot_name': plot_name,
                    'data_file_path': data_file_path,
                    'data_file_type': data_file_type
                })
            else:
                datasets.append({'data_file_type': EXIT_SIGNAL})
    
    # Only proceed if all datasets were loaded successfully
    if not any(ds.get('data_file_type') == EXIT_SIGNAL for ds in datasets):
        if loop_mode:
            # Execute multiple fittings with loop
            multiple_fit_with_loop(fitter_function=fitter_with_ui, datasets=datasets)
        else:
            # Execute single fit for each dataset
            for ds in datasets:
                fitter_with_ui(ds['data'], ds['x_name'], ds['y_name'], ds['plot_name'])


def multiple_fits_single_dataset() -> None:
    """
    Test different equation types on the same dataset.
    
    Workflow:
    1. Load a dataset once
    2. Try different equation types on it
    3. Compare results without reloading the data
    """
    # Lazy imports to avoid loading heavy dependencies at application startup
    from fitting.workflow_controller import coordinate_data_loading, coordinate_equation_selection
    from frontend.ui_dialogs import (
        ask_file_type,
        ask_file_name,
        ask_variables,
        ask_equation_type,
        ask_num_parameters,
        ask_parameter_names,
        ask_custom_formula,
    )

    menu = _get_menu_window()
    
    # Load data once
    (
        data, x_name, y_name, plot_name, data_file_path, data_file_type
    ) = coordinate_data_loading(
        parent_window=menu,
        ask_file_type_func=ask_file_type,
        ask_file_name_func=ask_file_name,
        ask_variables_func=ask_variables
    )
    
    if isinstance(data, str):  # Empty result
        return
    
    continue_testing = True
    
    while continue_testing:
        # Select equation type (backend function)
        equation_name, base_fit_function = coordinate_equation_selection(
            parent_window=menu,
            ask_equation_type_func=ask_equation_type,
            ask_num_parameters_func=ask_num_parameters,
            ask_parameter_names_func=ask_parameter_names,
            ask_custom_formula_func=ask_custom_formula,
            get_fitting_function_func=get_fitting_function
        )
        
        # Perform fit if equation was selected
        if equation_name != EXIT_SIGNAL and base_fit_function is not None:
            # Wrap backend function with frontend visualization
            display_name = equation_name.replace('_', ' ').title()
            fitter_with_ui = _wrap_with_visualization(base_fit_function, display_name)
            
            app_state.set_equation(equation_name, fitter_with_ui)
            fitter_with_ui(data, x_name, y_name, plot_name)
        
        # Ask if user wants to try another equation
        continue_testing = messagebox.askyesno(
            message=t('workflow.continue_question'), 
            title=t('workflow.fitting_title', name=plot_name)
        )


def all_fits_single_dataset() -> None:
    """
    Perform all available fitting types on the selected dataset.
    
    This function loads data and sequentially applies all predefined equation types
    to fit the data, generating results for each fitting method.
    """
    # Lazy imports to avoid loading heavy dependencies at application startup
    from fitting.workflow_controller import apply_all_equations, coordinate_data_loading
    from frontend.ui_dialogs import (
        ask_file_type,
        ask_file_name,
        ask_variables,
    )

    menu = _get_menu_window()
    
    # Load data
    (
        data, x_name, y_name, plot_name, data_file_path, data_file_type
    ) = coordinate_data_loading(
        parent_window=menu,
        ask_file_type_func=ask_file_type,
        ask_file_name_func=ask_file_name,
        ask_variables_func=ask_variables
    )
    
    if isinstance(data, str):  # Empty result
        return
    
    # Apply all equation types
    apply_all_equations(
        equation_setter=_set_equation_helper,
        get_fitter=lambda: app_state.current_fitter,
        equation_types=AVAILABLE_EQUATION_TYPES,
        data=data,
        x_name=x_name,
        y_name=y_name,
        plot_name=plot_name
    )


def watch_data() -> None:
    """
    View data from a file without performing any fitting.
    
    This function allows users to inspect loaded data.
    """
    # Lazy imports to avoid loading heavy dependencies at application startup
    from fitting.workflow_controller import coordinate_data_viewing
    from frontend.ui_dialogs import (
        ask_file_type,
        ask_file_name,
        show_data_dialog,
    )

    menu = _get_menu_window()
    
    coordinate_data_viewing(
        parent_window=menu,
        ask_file_type_func=ask_file_type,
        ask_file_name_func=ask_file_name,
        show_data_func=show_data_dialog
    )


def show_help() -> None:
    """
    Display help and information about the application.
    
    Shows information about fitting modes, navigation, data locations, and output locations.
    """
    # Lazy import to avoid loading help dialog module at startup
    from frontend.ui_dialogs import show_help_dialog

    menu = _get_menu_window()
    show_help_dialog(parent_window=menu)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main() -> None:
    """Main entry point for the application."""
    logger.info("="*60)
    logger.info(t('log.application_starting'))
    logger.info(t('log.version', version=__version__))
    logger.info("="*60)
    
    try:
        # Start the main menu
        # The start_main_menu function stores the menu in __main__.menu
        # Callbacks access it via _get_menu_window()
        start_main_menu(
            normal_fitting_callback=normal_fitting,
            single_fit_multiple_datasets_callback=single_fit_multiple_datasets,
            multiple_fits_single_dataset_callback=multiple_fits_single_dataset,
            all_fits_single_dataset_callback=all_fits_single_dataset,
            watch_data_callback=watch_data,
            help_callback=show_help
        )
        logger.info(t('log.application_closed'))
    except Exception as e:
        logger.critical(t('log.unexpected_error', error=str(e)), exc_info=True)
        messagebox.showerror(
            t('error.critical_error'),
            t('error.unexpected_error', error=str(e))
        )
        raise


if __name__ == "__main__":
    main()
