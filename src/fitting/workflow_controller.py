"""
Workflow controller for fitting operations.
Contains coordination functions and workflow patterns for the fitting application.
"""

# Standard library
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Third-party packages
import pandas as pd

# Local imports
from config import EXIT_SIGNAL
from i18n import t
from loaders import (
    FILE_TYPE_READERS,
    get_variable_names,
    load_data,
)

from utils import DataLoadError, get_logger

logger = get_logger(__name__)


# ============================================================================
# LAZY TKINTER IMPORT (for desktop GUI only, not available in headless environments)
# ============================================================================

def _get_messagebox() -> Any:
    """
    Lazy import of tkinter.messagebox.
    
    This function is only called from functions that require GUI dialogs
    (which are not used in Streamlit). Importing here avoids import errors
    when the module is loaded in headless environments.
    
    Returns:
        tkinter.messagebox module
        
    Raises:
        ImportError: If tkinter is not available
    """
    from tkinter import messagebox  # type: ignore[import-untyped]
    return messagebox


# ============================================================================
# DATA RELOADING UTILITIES
# ============================================================================

def reload_data_by_type(file_path: str, file_type: str) -> pd.DataFrame:
    """
    Reload data from a file based on its type.
    
    This function is used in loop mode to reload updated data from
    the same file. Useful when the user is modifying data in real-time
    and wants to see the updated fit after each modification.
    
    Args:
        file_path: Path to the data file
        file_type: Type of file ('csv', 'xlsx', 'txt')
        
    Returns:
        Loaded data as DataFrame
        
    Raises:
        DataLoadError: If file_type is not supported or loading fails
    """
    logger.info(t('log.reloading_data', path=file_path, type=file_type))

    try:
        reader = FILE_TYPE_READERS.get(file_type)
        if reader is None:
            logger.error(t('log.unsupported_file_type', file_type=file_type))
            raise DataLoadError(t('error.unsupported_file_type', file_type=file_type))
        data = reader(file_path)
        
        logger.info(t('log.data_reloaded', rows=len(data)))
        return data
        
    except Exception as e:
        logger.error(t('log.reload_failed', path=file_path, error=str(e)), exc_info=True)
        raise


# ============================================================================
# FITTING LOOP WORKFLOWS
# ============================================================================

def single_fit_with_loop(
    fitter_function: Callable,
    data: pd.DataFrame,
    x_name: Union[str, List[str]],
    y_name: str,
    plot_name: str,
    data_file_path: str,
    data_file_type: str
) -> None:
    """
    Execute a single fitting operation with optional loop mode.
    
    This function performs an initial fit and then optionally loops,
    reloading data and refitting each iteration. This is useful for
    iterative data analysis where the user modifies the data file
    between fits to explore different scenarios.
    
    Workflow:
    1. Perform initial fit with current data
    2. Show results and ask if user wants to continue
    3. If yes: reload data from file and repeat
    4. If no: exit
    
    Args:
        fitter_function: Fitting function to call (must accept data, x_name, y_name, plot_name)
        data: Initial dataset (pandas DataFrame)
        x_name: X variable column name(s) - string for single variable, list for multiple
        y_name: Y variable column name
        plot_name: Plot name for window titles and filename
        data_file_path: Path to data file for reloading
        data_file_type: File type ('csv', 'xlsx', 'txt')
    """
    logger.info(f"Starting single fit with loop: {plot_name}")
    
    # Perform first fit with initial data
    try:
        fitter_function(data, x_name, y_name, plot_name)
        logger.debug(t('log.initial_fit_completed'))
    except Exception as e:
        logger.error(t('log.initial_fit_failed', error=str(e)), exc_info=True)
        # Error is already shown by the fitter_function wrapper
        return
    
    # Ask if user wants to continue with loop mode
    messagebox = _get_messagebox()
    continue_fitting = messagebox.askyesno(
        message=t('workflow.continue_question'), 
        title=t('workflow.fitting_title', name=plot_name)
    )
    
    iteration = 1
    # Loop mode: reload data and refit until user exits
    while continue_fitting:
        logger.info(t('log.loop_iteration', iteration=iteration, name=plot_name))
        
        try:
            # Reload data from file (allows user to modify file between iterations)
            data = reload_data_by_type(data_file_path, data_file_type)
            # Perform fit with reloaded data
            fitter_function(data, x_name, y_name, plot_name)
            logger.debug(f"Loop iteration {iteration} completed successfully")
        except Exception as e:
            logger.error(
                t('log.error_in_iteration', iteration=iteration, error=str(e)),
                exc_info=True
            )
            # Error is handled by fitter_function wrapper or messagebox
        
        # Ask if user wants another iteration
        continue_fitting = messagebox.askyesno(
            message=t('workflow.continue_question'), 
            title=t('workflow.fitting_title', name=plot_name)
        )
        iteration += 1
    
    logger.info(t('log.loop_completed', name=plot_name, iterations=iteration-1))


def multiple_fit_with_loop(
    fitter_function: Callable,
    datasets: List[Dict[str, Any]]
) -> None:
    """
    Execute multiple fitting operations with optional loop mode.
    
    Performs fitting on multiple datasets sequentially, with the option
    to reload and refit each dataset in a loop. Each dataset can be
    independently continued or stopped.
    
    Workflow:
    1. Fit all datasets once
    2. Ask user for each dataset if they want to continue
    3. For datasets marked to continue: reload and refit
    4. Repeat until no datasets are marked to continue
    
    Args:
        fitter_function: Fitting function to call (must accept data, x_name, y_name, plot_name).
        datasets: List of dictionaries, each containing:
                  - 'data': dataset (pandas DataFrame)
                  - 'x_name': X variable column name
                  - 'y_name': Y variable column name
                  - 'plot_name': plot name for display and filename
                  - 'data_file_path': path to data file for reloading
                  - 'data_file_type': file type ('csv', 'xlsx', 'txt')
    """
    messagebox = _get_messagebox()
    continue_flags: List[bool] = []

    for i, ds in enumerate(datasets):
        fitter_function(ds['data'], ds['x_name'], ds['y_name'], ds['plot_name'])
        should_continue = messagebox.askyesno(
            message=t('workflow.continue_question'),
            title=f"{t('workflow.fitting_title', name=ds['plot_name'])} ({i+1})"
        )
        continue_flags.append(should_continue)

    while any(continue_flags):
        for i, ds in enumerate(datasets):
            if continue_flags[i]:
                ds['data'] = reload_data_by_type(
                    ds['data_file_path'], ds['data_file_type']
                )
                # Perform fit with reloaded data
                fitter_function(ds['data'], ds['x_name'], ds['y_name'], ds['plot_name'])
        
        # Ask again for each dataset that's still continuing
        for i, ds in enumerate(datasets):
            if continue_flags[i]:
                continue_flags[i] = messagebox.askyesno(
                    message=t('workflow.continue_question'),
                    title=f"{t('workflow.fitting_title', name=ds['plot_name'])} ({i+1})"
                )


def apply_all_equations(
    equation_setter: Callable[[str], None],
    get_fitter: Callable[[], Optional[Callable]],
    equation_types: List[str],
    data: pd.DataFrame,
    x_name: str,
    y_name: str,
    plot_name: Optional[str] = None,
) -> None:
    """
    Apply all available equation types to a dataset.
    
    This function automatically tests all predefined equation types on
    a single dataset, displaying results for each. Useful for exploratory
    data analysis to determine which mathematical model best fits the data.
    
    The function iterates through all equations and displays the fit results
    one by one, allowing the user to compare goodness of fit visually.
    
    Args:
        equation_setter: Function to set the current equation type (e.g., 'linear_function')
        get_fitter: Function to retrieve the fitter for the currently set equation type
        equation_types: List of equation type identifiers to test
            (e.g., from config.AVAILABLE_EQUATION_TYPES)
        data: Dataset to fit (pandas DataFrame)
        x_name: Independent variable column name
        y_name: Dependent variable column name
        plot_name: Plot name for display and filename (optional).

    Examples:
        >>> from config import AVAILABLE_EQUATION_TYPES
        >>> apply_all_equations(
        ...     equation_setter=my_setter,
        ...     get_fitter=my_getter,
        ...     equation_types=AVAILABLE_EQUATION_TYPES,
        ...     data=df,
        ...     x_name='x',
        ...     y_name='y',
        ...     plot_name='my_plot'
        ... )
    """
    # Iterate through all equation types
    for eq_type in equation_types:
        # Set the current equation type
        equation_setter(eq_type)
        # Get the fitter function for this equation
        fitting_function = get_fitter()
        
        # Perform fit if fitter was successfully retrieved
        if fitting_function is not None:
            # Create a plot name with the equation type for differentiation
            fit_plot_name = f"{plot_name}_{eq_type}" if plot_name is not None else None
            fitting_function(data, x_name, y_name, fit_plot_name)


# ============================================================================
# DATA LOADING COORDINATION WORKFLOWS
# ============================================================================

def coordinate_data_loading(
    parent_window: Any,
    open_load_func: Callable,
    ask_variables_func: Callable,
) -> Tuple[Union[pd.DataFrame, str], str, str, str, str, str]:
    """
    Coordinate the complete data loading workflow.

    This function orchestrates the entire data loading process:
    1. Open native file dialog to select a data file
    2. Load the data
    3. Ask user for variables to use

    Args:
        parent_window: Parent Tkinter window.
        open_load_func: Function that opens native file dialog, returns (path, file_type)
            or (None, None) on cancel. E.g. open_load_dialog from frontend.ui_dialogs.
        ask_variables_func: Function to ask for variables.

    Returns:
        Tuple (data, x_name, y_name, plot_name, file_path, file_type).
        On user cancel, data is empty string and other fields are empty strings.
    """
    logger.info("Starting data loading workflow")
    empty_result = ('', '', '', '', '', '')
    messagebox = _get_messagebox()

    # Frontend: Open native file dialog
    file_path, file_type = open_load_func(parent_window)
    logger.debug(f"User selected file: {file_path} (type: {file_type})")

    if not file_path or not file_type:
        logger.info("User cancelled file selection")
        return empty_result

    try:
        # Backend: Load data from selected path
        data = load_data(file_path, file_type)

        if data is None or data.empty:
            logger.error("Loaded data is None or empty")
            messagebox.showerror(
                t('error.title'),
                t('error.data_load_error', error='Data is empty')
            )
            return empty_result
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}", exc_info=True)
        messagebox.showerror(
            t('error.title'),
            t('error.data_load_error', error=str(e))
        )
        return empty_result

    # Backend: Get variable names
    variables_name = get_variable_names(data)
    logger.debug(f"Available variables: {variables_name}")

    # Frontend: Ask for variables
    x_name, y_name, plot_name = ask_variables_func(parent_window, variables_name)
    logger.debug(f"User selected variables: x={x_name}, y={y_name}, plot={plot_name}")

    if not x_name or not y_name:
        logger.info("User cancelled variable selection")
        return empty_result

    logger.info(f"Data loading workflow completed: {file_path}")
    return data, x_name, y_name, plot_name, file_path, file_type


def coordinate_data_viewing(
    parent_window: Any,
    open_load_func: Callable,
    show_data_func: Callable,
) -> None:
    """
    Coordinate the data viewing workflow.

    This function orchestrates the process of selecting and displaying
    data from files without performing any fitting operations.

    Args:
        parent_window: Parent Tkinter window.
        open_load_func: Function that opens native file dialog, returns (path, file_type)
            or (None, None) on cancel.
        show_data_func: Function to display data.
    """
    messagebox = _get_messagebox()

    # Frontend: Open native file dialog
    file_path, file_type = open_load_func(parent_window)

    if not file_path or not file_type:
        return

    try:
        data = load_data(file_path, file_type)
        show_data_func(parent_window, data)
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}", exc_info=True)
        messagebox.showerror(
            t('error.title'),
            t('error.data_load_error', error=str(e))
        )


# ============================================================================
# EQUATION SELECTION COORDINATION WORKFLOWS
# ============================================================================

def coordinate_equation_selection(
    parent_window: Any,
    ask_equation_type_func: Callable,
    ask_num_parameters_func: Callable,
    ask_parameter_names_func: Callable,
    ask_custom_formula_func: Callable,
    get_fitting_function_func: Callable,
) -> Tuple[str, Optional[Callable]]:
    """
    Coordinate the equation selection workflow.
    
    Handles the complete process of equation selection, including both
    predefined equations and custom user-defined equations.
    
    Args:
        parent_window: Parent Tkinter window
        ask_equation_type_func: Function to ask for equation type
        ask_num_parameters_func: Function to ask for number of parameters
        ask_parameter_names_func: Function to ask for parameter names
        ask_custom_formula_func: Function to ask for custom formula
        get_fitting_function_func: Function to retrieve fitting function by name
        
    Returns:
        Tuple of (equation_name, fitter_function)
    """
    # Ask user for equation type (may return tuple with optional initial/bounds overrides)
    result = ask_equation_type_func(parent_window)
    if isinstance(result, tuple) and len(result) == 3:
        selected, user_initial_guess, user_bounds = result
    else:
        selected = result if isinstance(result, str) else EXIT_SIGNAL
        user_initial_guess = None
        user_bounds = None

    # Handle custom equation
    if selected == 'custom':
        return coordinate_custom_equation(
            parent_window,
            ask_num_parameters_func,
            ask_parameter_names_func,
            ask_custom_formula_func
        )

    # Handle predefined equations
    if selected != EXIT_SIGNAL and selected != '':
        fitter_function = get_fitting_function_func(
            selected, user_initial_guess, user_bounds
        )
        return selected, fitter_function

    # User wants to exit
    return EXIT_SIGNAL, None


def coordinate_custom_equation(
    parent_window: Any,
    ask_num_parameters_func: Callable,
    ask_parameter_names_func: Callable,
    ask_custom_formula_func: Callable,
) -> Tuple[str, Optional[Callable]]:
    """
    Coordinate the custom equation creation workflow.
    
    Handles the process of creating a user-defined custom fitting equation
    by collecting parameter information and the formula. Returns only the
    backend fitting function (without visualization), maintaining separation
    of concerns.
    
    Args:
        parent_window: Parent Tkinter window
        ask_num_parameters_func: Function to ask for number of parameters and independent variables
        ask_parameter_names_func: Function to ask for parameter names
        ask_custom_formula_func: Function to ask for custom formula
        
    Returns:
        Tuple of ('custom: <formula>', backend_fit_function) or (EXIT_SIGNAL, None) if cancelled
    """
    from fitting.custom_function_evaluator import CustomFunctionEvaluator
    
    # Frontend: Get number of parameters and independent variables
    result = ask_num_parameters_func(parent_window)
    if result is None:
        return EXIT_SIGNAL, None
    
    num_param, num_independent_vars = result

    # Frontend: Get parameter names
    parameter_names = ask_parameter_names_func(parent_window, num_param)
    
    # Check if user wants to exit (check both translated and internal values)
    exit_option = t('dialog.exit_option')
    if (
        EXIT_SIGNAL in parameter_names
        or 'exit' in parameter_names
        or exit_option in parameter_names
    ):
        return EXIT_SIGNAL, None
    
    # Frontend: Get formula (pass num_independent_vars for appropriate hints)
    custom_formula = ask_custom_formula_func(parent_window, parameter_names, num_independent_vars)
    
    # Check if user wants to exit (check both translated and internal values)
    if custom_formula in (EXIT_SIGNAL, 'exit', 'e', exit_option):
        return EXIT_SIGNAL, None
    
    # Backend: Create custom evaluator
    evaluator = CustomFunctionEvaluator(custom_formula, parameter_names, num_independent_vars)
    
    # Create a wrapper function that stores num_independent_vars as an attribute
    # This allows us to access it later for determining plot type
    def fit_wrapper(data: Any, x_name: Union[str, List[str]], y_name: str) -> Tuple[str, Any, str]:
        """Wrapper for evaluator.fit that stores num_independent_vars."""
        return evaluator.fit(data, x_name, y_name)
    
    # Store num_independent_vars as attribute on wrapper function
    fit_wrapper.num_independent_vars = num_independent_vars  # type: ignore
    
    # Return backend function (fit only, no visualization)
    # The wrapper returns (text, y_fitted, equation)
    equation_id = f"custom: {custom_formula[:30]}..."
    return equation_id, fit_wrapper
