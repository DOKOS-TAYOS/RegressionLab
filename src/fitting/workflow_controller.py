#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow controller for fitting operations.
Contains coordination functions and workflow patterns for the fitting application.
"""

# Standard library
from tkinter import messagebox
from typing import Any, Callable, Dict, List, Optional, Tuple

# Third-party packages
import pandas as pd

# Local imports
from config import EXIT_SIGNAL
from i18n import t
from loaders.data_loader import (
    get_file_list_by_type,
    get_variable_names,
    load_data_workflow,
)
from loaders.loading_utils import csv_reader, excel_reader, get_file_names
from utils.exceptions import DataLoadError
from utils.logger import get_logger

logger = get_logger(__name__)


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
        file_type: Type of file ('csv', 'xls', 'xlsx')
        
    Returns:
        Loaded data as DataFrame
        
    Raises:
        DataLoadError: If file_type is not supported or loading fails
    """
    logger.info(t('log.reloading_data', path=file_path, type=file_type))
    
    try:
        if file_type == 'csv':
            data = csv_reader(file_path)
        elif file_type in ('xls', 'xlsx'):
            data = excel_reader(file_path)
        else:
            logger.error(t('log.unsupported_file_type', file_type=file_type))
            raise DataLoadError(t('error.unsupported_file_type', file_type=file_type))
        
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
    x_name: str,
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
        x_name: X variable column name
        y_name: Y variable column name
        plot_name: Plot name for window titles and filename
        data_file_path: Path to data file for reloading
        data_file_type: File type ('csv', 'xls', 'xlsx')
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
        fitter_function: Fitting function to call (must accept data, x_name, y_name, plot_name)
        datasets: List of dictionaries, each containing:
                  - 'data': dataset (pandas DataFrame)
                  - 'x_name': X variable column name
                  - 'y_name': Y variable column name
                  - 'plot_name': plot name for display and filename
                  - 'file_path': path to data file for reloading
                  - 'file_type': file type ('csv', 'xls', 'xlsx')
    """
    # Track which datasets should continue in loop mode
    continue_flags = []
    
    # Initial fitting pass for all datasets
    for i, ds in enumerate(datasets):
        fitter_function(ds['data'], ds['x_name'], ds['y_name'], ds['plot_name'])
        # Ask user if they want to continue with this dataset
        should_continue = messagebox.askyesno(
            message=t('workflow.continue_question'),
            title=f"{t('workflow.fitting_title', name=ds['plot_name'])} ({i+1})"
        )
        continue_flags.append(should_continue)
    
    # Loop while at least one dataset is marked to continue
    while any(continue_flags):
        # Reload and refit only datasets marked to continue
        for i, ds in enumerate(datasets):
            if continue_flags[i]:
                # Reload data from file (allows user to modify between iterations)
                ds['data'] = reload_data_by_type(ds['file_path'], ds['file_type'])
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
    plot_name: str = None
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
        plot_name: Plot name for display and filename (optional)
        
    Example:
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
            fit_plot_name = f"{plot_name}_{eq_type}" if plot_name else None
            fitting_function(data, x_name, y_name, fit_plot_name)


# ============================================================================
# DATA LOADING COORDINATION WORKFLOWS
# ============================================================================

def coordinate_data_loading(parent_window, 
                           ask_file_type_func: Callable, 
                           ask_file_name_func: Callable,
                           ask_variables_func: Callable) -> Tuple:
    """
    Coordinate the complete data loading workflow.
    
    This function orchestrates the entire data loading process:
    1. Get available files
    2. Ask user for file type
    3. Ask user for specific file
    4. Load the data
    5. Ask user for variables to use
    
    Args:
        parent_window: Parent Tkinter window
        ask_file_type_func: Function to ask for file type
        ask_file_name_func: Function to ask for file name
        ask_variables_func: Function to ask for variables
        
    Returns:
        Tuple: (data, x_name, y_name, plot_name, file_path, file_type)
            Returns empty tuple if user cancels
    """
    logger.info("Starting data loading workflow")
    empty_result = ('', '', '', '', '', '')
    
    try:
        # Backend: Get available files
        csv, xls, xlsx = get_file_names()
        logger.debug(f"Available files - CSV: {len(csv)}, XLS: {len(xls)}, XLSX: {len(xlsx)}")
    except Exception as e:
        logger.error(f"Failed to get available files: {str(e)}", exc_info=True)
        messagebox.showerror(
            t('error.title'),
            t('error.file_list_error', error=str(e))
        )
        return empty_result
    
    # Frontend: Ask for file type
    file_type = ask_file_type_func(parent_window)
    logger.debug(f"User selected file type: {file_type}")
    
    # Check if user wants to exit
    if file_type == EXIT_SIGNAL or file_type == '':
        logger.info("User cancelled file type selection")
        return empty_result
    
    try:
        # Backend: Get file list for selected type
        file_list = get_file_list_by_type(file_type, csv, xls, xlsx)
        
        # Check if files are available
        if not file_list:
            logger.warning(f"No files available for type: {file_type}")
            messagebox.showwarning(
                t('warning.title'),
                t('warning.no_files_found', file_type=file_type)
            )
            return empty_result
    except Exception as e:
        logger.error(f"Error getting file list: {str(e)}", exc_info=True)
        messagebox.showerror(t('error.title'), t('error.file_list_error', error=str(e)))
        return empty_result
    
    # Frontend: Ask for specific file
    file_name = ask_file_name_func(parent_window, file_list)
    logger.debug(f"User selected file: {file_name}")
    
    # Check if user cancelled
    if not file_name:
        logger.info("User cancelled file selection")
        return empty_result
    
    try:
        # Backend: Load data
        data, file_path = load_data_workflow(file_name, file_type)
        
        # Check if data loaded successfully
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
    
    # Check if user cancelled
    if not x_name or not y_name:
        logger.info("User cancelled variable selection")
        return empty_result
    
    logger.info(f"Data loading workflow completed: {file_name}.{file_type}")
    return data, x_name, y_name, plot_name, file_path, file_type


def coordinate_data_viewing(parent_window,
                            ask_file_type_func: Callable,
                            ask_file_name_func: Callable,
                            show_data_func: Callable) -> None:
    """
    Coordinate the data viewing workflow.
    
    This function orchestrates the process of selecting and displaying
    data from files without performing any fitting operations.
    
    Args:
        parent_window: Parent Tkinter window
        ask_file_type_func: Function to ask for file type
        ask_file_name_func: Function to ask for file name
        show_data_func: Function to display data
    """
    # Get available files
    csv, xls, xlsx = get_file_names()
    
    # Frontend: Ask for file type
    file_type = ask_file_type_func(parent_window)
    
    if file_type != EXIT_SIGNAL and file_type != '':
        # Backend: Get file list for selected type
        file_list = get_file_list_by_type(file_type, csv, xls, xlsx)
        
        # Check if files are available
        if not file_list:
            messagebox.showwarning(
                t('warning.title'),
                t('warning.no_files_found', file_type=file_type)
            )
            return
        
        # Frontend: Ask for specific file
        file_name = ask_file_name_func(parent_window, file_list)
        
        # Check if user cancelled
        if not file_name:
            return
        
        # Backend: Load data
        data, _ = load_data_workflow(file_name, file_type)
        
        # Frontend: Show data
        show_data_func(parent_window, data)


# ============================================================================
# EQUATION SELECTION COORDINATION WORKFLOWS
# ============================================================================

def coordinate_equation_selection(
    parent_window,
    ask_equation_type_func: Callable,
    ask_num_parameters_func: Callable,
    ask_parameter_names_func: Callable,
    ask_custom_formula_func: Callable,
    get_fitting_function_func: Callable
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
    # Ask user for equation type
    selected = ask_equation_type_func(parent_window)
    
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
        fitter_function = get_fitting_function_func(selected)
        return selected, fitter_function
    
    # User wants to exit
    return EXIT_SIGNAL, None


def coordinate_custom_equation(
    parent_window,
    ask_num_parameters_func: Callable,
    ask_parameter_names_func: Callable,
    ask_custom_formula_func: Callable
) -> Tuple[str, Optional[Callable]]:
    """
    Coordinate the custom equation creation workflow.
    
    Handles the process of creating a user-defined custom fitting equation
    by collecting parameter information and the formula. Returns only the
    backend fitting function (without visualization), maintaining separation
    of concerns.
    
    Args:
        parent_window: Parent Tkinter window
        ask_num_parameters_func: Function to ask for number of parameters
        ask_parameter_names_func: Function to ask for parameter names
        ask_custom_formula_func: Function to ask for custom formula
        
    Returns:
        Tuple of ('custom: <formula>', backend_fit_function) or (EXIT_SIGNAL, None) if cancelled
    """
    from fitting.custom_function_evaluator import CustomFunctionEvaluator
    
    # Frontend: Get number of parameters
    num_param = ask_num_parameters_func(parent_window)
    
    # Frontend: Get parameter names
    parameter_names = ask_parameter_names_func(parent_window, num_param)
    
    # Check if user wants to exit (check both translated and internal values)
    exit_option = t('dialog.exit_option')
    if (
        EXIT_SIGNAL in parameter_names
        or 'salir' in parameter_names
        or exit_option in parameter_names
    ):
        return EXIT_SIGNAL, None
    
    # Frontend: Get formula
    custom_formula = ask_custom_formula_func(parent_window, parameter_names)
    
    # Check if user wants to exit (check both translated and internal values)
    if custom_formula in (EXIT_SIGNAL, 'salir', 's', exit_option):
        return EXIT_SIGNAL, None
    
    # Backend: Create custom evaluator
    evaluator = CustomFunctionEvaluator(custom_formula, parameter_names)
    
    # Return backend function (fit only, no visualization)
    # The evaluator.fit method returns (text, y_fitted, equation)
    equation_id = f"custom: {custom_formula[:30]}..."
    return equation_id, evaluator.fit
