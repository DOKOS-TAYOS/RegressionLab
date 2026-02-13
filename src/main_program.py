#!/usr/bin/env python
"""
Main Program - Data Fitting Application
Entry point for the curve fitting application with GUI interface.
"""

# Standard library
import sys
from pathlib import Path
from tkinter import messagebox
from typing import Any, Callable, List, Optional, Union

# Add src directory to Python path for proper imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Local imports (kept lightweight at startup; heavy modules are loaded lazily)
from config import AVAILABLE_EQUATION_TYPES, EXIT_SIGNAL, __version__, initialize_and_validate_config  # noqa: E402
from i18n import t, initialize_i18n  # noqa: E402
from frontend import start_main_menu  # noqa: E402
from fitting import get_fitting_function  # noqa: E402
from utils import FittingError, setup_logging, get_logger  # noqa: E402

# Initialize configuration validation, i18n and logging at module level
initialize_and_validate_config()
initialize_i18n()
setup_logging()
logger = get_logger(__name__)


# ============================================================================
# APPLICATION STATE
# ============================================================================

class _ApplicationState:
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
_app_state = _ApplicationState()


# ============================================================================
# WORKFLOW FUNCTIONS - Main Menu Callbacks
# ============================================================================

def _get_menu_window() -> Optional[Any]:
    """Get the menu window from __main__ module."""
    import __main__
    return getattr(__main__, 'menu', None)


def _equation_display_name(equation_name: str) -> str:
    """Convert internal equation name to display form (e.g. 'linear_function' -> 'Linear Function')."""
    return equation_name.replace('_', ' ').title()


def _resolve_multiple_x_variables(
    menu: Any,
    data: Any,
    x_name: str,
    num_independent_vars: int,
    filter_uncertainty: bool = False,
) -> Optional[Union[str, List[str]]]:
    """
    Ask for multiple x variables when equation has more than one independent variable.

    Args:
        menu: Parent window for dialogs.
        data: Dataset (DataFrame or dict).
        x_name: First x variable already selected.
        num_independent_vars: Number of independent variables required.
        filter_uncertainty: If True, exclude uncertainty columns from variable list.

    Returns:
        List of x variable names, or None if user cancels. For single-variable fits,
        returns x_name unchanged.
    """
    if num_independent_vars <= 1:
        return x_name
    from frontend import ask_multiple_x_variables
    from loaders import get_variable_names

    variable_names = get_variable_names(data, filter_uncertainty=filter_uncertainty)
    x_names = ask_multiple_x_variables(
        parent_window=menu,
        variable_names=variable_names,
        num_vars=num_independent_vars,
        first_x_name=x_name,
    )
    return x_names if x_names else None


def _set_equation_helper(equation_name: str) -> None:
    """
    Set the current equation and create a fitter with visualization.
    
    This helper retrieves the backend fitting function for the given equation,
    wraps it with frontend visualization, and stores both in the application state.
    
    Args:
        equation_name: Internal name of the equation (e.g., 'linear_function')
    """
    base_fit = get_fitting_function(equation_name)
    if base_fit:
        fitter_with_ui = _wrap_with_visualization(base_fit, _equation_display_name(equation_name))
        _app_state.set_equation(equation_name, fitter_with_ui)

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
    from plotting import create_plot
    from frontend import create_result_window
    
    def wrapped_function(
        data: Any,
        x_name: Union[str, List[str]],
        y_name: str,
        plot_name: Optional[str] = None,
    ) -> None:
        """Execute fitting and display results."""
        try:
            # Backend: Perform the fitting calculation
            # Returns: parameter text, fitted y values, formatted equation, fit_info (for prediction)
            result = base_fit_function(data, x_name, y_name)
            if len(result) == 4:
                text, y_fitted, equation, fit_info = result
            else:
                text, y_fitted, equation = result
                fit_info = None

            num_indep = getattr(base_fit_function, 'num_independent_vars', 1)
            if isinstance(x_name, list):
                num_indep = len(x_name)

            x_key: str = x_name if isinstance(x_name, str) else x_name[0]
            y = data[y_name]
            uy = data.get('u%s' % y_name, [0.0] * len(y))
            filename_base = plot_name if plot_name else fit_name
            figure_3d = None

            if num_indep == 1:
                x = data[x_key]
                ux = data.get('u%s' % x_key, [0.0] * len(x))
                output_path = create_plot(
                    x, y, ux, uy, y_fitted, filename_base, x_key, y_name,
                    fit_info=fit_info,
                )
            elif num_indep == 2:
                # Two variables: 3D plot (interactive, rotatable with mouse)
                from plotting import create_3d_plot
                x1 = data[x_name[0]]
                x2 = data[x_name[1]]
                output_path, figure_3d = create_3d_plot(
                    x1, x2, y, y_fitted, filename_base,
                    x_name[0], x_name[1], y_name,
                    interactive=True,
                    fit_info=fit_info,
                )
            else:
                # Multiple variables (>2): residual plot
                from plotting import create_residual_plot
                import numpy as np
                residuals = np.array(y) - np.array(y_fitted)
                point_indices = list(range(len(y)))
                output_path = create_residual_plot(
                    residuals, point_indices, filename_base
                )
            
            # Display the results in a Tkinter window
            window_title = plot_name if plot_name else fit_name
            create_result_window(
                window_title, text, equation, output_path,
                figure_3d=figure_3d,
                fit_info=fit_info,
            )
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
    from fitting import (
        single_fit_with_loop,
        coordinate_data_loading,
        coordinate_equation_selection,
    )
    from frontend import (
        open_load_dialog,
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
    
    num_independent_vars = getattr(base_fit_function, 'num_independent_vars', 1)
    fitter_with_ui = _wrap_with_visualization(base_fit_function, _equation_display_name(equation_name))
    
    # Store current equation in app state
    _app_state.set_equation(equation_name, fitter_with_ui)
    
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
        open_load_func=open_load_dialog,
        ask_variables_func=ask_variables
    )
    
    # Check if data was loaded successfully (empty string indicates cancellation)
    if isinstance(data, str):  # Empty result
        logger.info(t('log.user_cancelled_data'))
        return
    
    # Phase 3.5: If multidimensional, ask for additional x variables
    x_name = _resolve_multiple_x_variables(menu, data, x_name, num_independent_vars)
    if x_name is None:
        logger.info("User cancelled multiple x variables selection")
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
    from fitting import (
        multiple_fit_with_loop,
        coordinate_data_loading,
        coordinate_equation_selection,
    )
    from frontend import (
        open_load_dialog,
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

    num_independent_vars = getattr(base_fit_function, 'num_independent_vars', 1)
    fitter_with_ui = _wrap_with_visualization(base_fit_function, _equation_display_name(equation_name))
    _app_state.set_equation(equation_name, fitter_with_ui)
    
    # Ask for number of datasets
    num_datasets = ask_num_fits(menu)
    if num_datasets is None:
        return

    # Ask if user wants loop mode
    loop_mode = messagebox.askyesno(
        message=t('workflow.loop_question'), 
        title=t('workflow.multiple_fitting_title')
    )
    
    datasets: List[dict] = []
    for _ in range(num_datasets):
        if any(ds.get('data_file_type') == EXIT_SIGNAL for ds in datasets):
            break
        (
            data, x_name, y_name, plot_name, data_file_path, data_file_type
        ) = coordinate_data_loading(
            parent_window=menu,
            open_load_func=open_load_dialog,
            ask_variables_func=ask_variables
        )
        if isinstance(data, str):
            datasets.append({'data_file_type': EXIT_SIGNAL})
            break
        x_name = _resolve_multiple_x_variables(
            menu, data, x_name, num_independent_vars, filter_uncertainty=True
        )
        if x_name is None:
            datasets.append({'data_file_type': EXIT_SIGNAL})
            break
        datasets.append({
            'data': data,
            'x_name': x_name,
            'y_name': y_name,
            'plot_name': plot_name,
            'data_file_path': data_file_path,
            'data_file_type': data_file_type
        })
    
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
    from fitting import coordinate_data_loading, coordinate_equation_selection
    from frontend import (
        open_load_dialog,
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
        open_load_func=open_load_dialog,
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
        
        if equation_name != EXIT_SIGNAL and base_fit_function is not None:
            fitter_with_ui = _wrap_with_visualization(base_fit_function, _equation_display_name(equation_name))
            _app_state.set_equation(equation_name, fitter_with_ui)

            # If custom multidimensional, ask for independent variables before fitting
            num_independent_vars = getattr(base_fit_function, 'num_independent_vars', 1)
            fit_x_name = _resolve_multiple_x_variables(menu, data, x_name, num_independent_vars)
            if fit_x_name is None:
                logger.info("User cancelled multiple x variables selection")
                continue
            fitter_with_ui(data, fit_x_name, y_name, plot_name)
        
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
    from fitting import apply_all_equations, coordinate_data_loading
    from frontend import (
        open_load_dialog,
        ask_variables,
    )

    menu = _get_menu_window()
    
    # Load data
    (
        data, x_name, y_name, plot_name, data_file_path, data_file_type
    ) = coordinate_data_loading(
        parent_window=menu,
        open_load_func=open_load_dialog,
        ask_variables_func=ask_variables
    )
    
    if isinstance(data, str):  # Empty result
        return
    
    # Apply all equation types
    apply_all_equations(
        equation_setter=_set_equation_helper,
        get_fitter=lambda: _app_state.current_fitter,
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
    from fitting import coordinate_data_viewing
    from frontend import (
        open_load_dialog,
        show_data_dialog,
    )

    menu = _get_menu_window()
    
    coordinate_data_viewing(
        parent_window=menu,
        open_load_func=open_load_dialog,
        show_data_func=show_data_dialog
    )


def show_help() -> None:
    """
    Display help and information about the application.
    
    Shows information about fitting modes, navigation, data locations, and output locations.
    """
    # Lazy import to avoid loading help dialog module at startup
    from frontend import show_help_dialog

    menu = _get_menu_window()
    show_help_dialog(parent_window=menu)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def _check_for_updates() -> None:
    """
    Check for updates once a week. If a newer version is available and
    CHECK_UPDATES is enabled, show a dialog asking if the user wants to update.
    If yes, perform git pull (preserves input/, output/, .env).
    """
    from utils.update_checker import (
        is_update_available,
        perform_git_pull,
        record_check_done,
        should_run_check,
    )

    if not should_run_check():
        logger.debug("Update check skipped (CHECK_UPDATES disabled or checked recently)")
        return

    latest = is_update_available(__version__)
    record_check_done()

    if latest:
        logger.info("Update available: %s (current: %s)", latest, __version__)
    else:
        logger.debug("Update check done: no newer version (current: %s)", __version__)

    if not latest:
        return

    wants_update = messagebox.askyesno(
        t('update.title'),
        t('update.message', latest=latest, current=__version__),
        default=messagebox.YES,
    )
    if not wants_update:
        return

    success, msg = perform_git_pull()
    if success:
        # msg may be git output or i18n key
        display_msg = t(msg) if msg.startswith('update.') else msg
        messagebox.showinfo(t('update.title'), display_msg)
    else:
        display_msg = t(msg) if msg.startswith('update.') else msg
        messagebox.showerror(t('update.title'), display_msg)


def main() -> None:
    """Main entry point for the application."""
    logger.info("="*60)
    logger.info(t('log.application_starting'))
    logger.info(t('log.version', version=__version__))
    logger.info("="*60)

    try:
        _check_for_updates()
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
