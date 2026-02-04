# Standard library
from decimal import Decimal
from typing import Any, Callable, List, Optional, Sequence, Tuple

# Numerical library
import numpy as np

# Local imports (heavy numerical libraries are imported lazily inside functions)
from config import (
    EQUATION_FORMULAS,
    EQUATION_FUNCTION_MAP,
    EQUATION_PARAM_NAMES,
    EXIT_SIGNAL,
)
from i18n import t
from utils.exceptions import FittingError
from utils.logger import get_logger

logger = get_logger(__name__)

def format_parameter(value: float, sigma: float) -> Tuple[float, str]:
    """
    Format a parameter and its uncertainty using scientific notation.
    
    Args:
        value: Parameter value
        sigma: Uncertainty in the parameter
        
    Returns:
        Tuple of (rounded_value, formatted_sigma_string)
    """
    # Check if sigma is infinite or NaN
    if not np.isfinite(sigma):
        if np.isinf(sigma):
            # Use infinity symbol instead of INF
            return round(value, 6), '∞'
        else:  # NaN
            return round(value, 6), 'NaN'
    
    try:
        sigma_str = '%.1E' % Decimal(sigma)
        # Try to extract exponent part (format: X.XE+YY or X.XE-YY)
        if 'E' in sigma_str or 'e' in sigma_str:
            exp_part = sigma_str.split('E')[-1] if 'E' in sigma_str else sigma_str.split('e')[-1]
            if exp_part:  # Check if exp_part is not empty
                exp_value = int(exp_part)
                rounded_value = round(value, 1 - exp_value)
            else:
                # Fallback if no exponent found
                logger.debug(t('log.no_exponent_found', sigma_str=sigma_str))
                rounded_value = round(value, 6)  # Default to 6 decimal places
        else:
            # No exponential notation, use default rounding
            logger.debug(t('log.no_exponential_notation', sigma_str=sigma_str))
            rounded_value = round(value, 6)
        return rounded_value, sigma_str
    except (ValueError, IndexError, OverflowError) as e:
        # If anything goes wrong, return value with default formatting
        logger.warning(t('log.error_formatting_parameter', error=str(e)))
        return round(value, 6), f"{sigma:.1E}"


def generic_fit(
    data: Any,
    x_name: str,
    y_name: str,
    fit_func: Callable[..., Any],
    param_names: List[str],
    equation_template: str,
    initial_guess: Optional[List[float]] = None,
    bounds: Optional[Tuple[Sequence[float], Sequence[float]]] = None
) -> Tuple[str, Any, str]:
    """
    Generic fitting function that performs curve fitting with any function.
    
    This function handles the complete fitting workflow including parameter
    extraction, uncertainty calculation, and result formatting.
    
    Args:
        data: Data dictionary containing x, y and their uncertainties
        x_name: Name of the x variable
        y_name: Name of the y variable
        fit_func: Function to fit (e.g., linear_function_with_n, sin_function, etc.)
        param_names: List of parameter names (e.g., ['m', 'n'] or ['a', 'b', 'c'])
        equation_template: Template for equation display (e.g., "y={m}x+{n}")
        initial_guess: Optional initial parameter values for fitting (improves convergence)
        bounds: Optional (lower_bounds, upper_bounds) for parameters;
            avoids overflow in exponentials
    
    Returns:
        Tuple of (text, y_fitted, equation):
            - text: Formatted text with parameters, uncertainties, R² and statistics
            - y_fitted: Array with fitted y values
            - equation: Formatted equation with parameter values
            
    Raises:
        FittingError: If fitting fails or data is invalid
    """
    # Lazy imports to avoid loading heavy numerical stack when importing this module
    from scipy import stats as scipy_stats
    from scipy.optimize import curve_fit
    from utils.validators import validate_fitting_data

    logger.info(t('log.starting_generic_fit', x=x_name, y=y_name, params=str(param_names)))

    # Validate fitting data
    try:
        validate_fitting_data(data, x_name, y_name)
    except Exception as e:
        logger.error(t('log.data_validation_failed', error=str(e)))
        raise FittingError(t('error.data_validation_failed', error=str(e)))
    
    # Extract data
    x = data[x_name]
    ux = data['u%s' % x_name]
    y = data[y_name]
    uy = data['u%s' % y_name]
    
    logger.debug(t('log.data_points_info', 
                   points=len(x), 
                   x_min=f"{x.min():.3f}", 
                   x_max=f"{x.max():.3f}",
                   y_min=f"{y.min():.3f}", 
                   y_max=f"{y.max():.3f}"))

    # curve_fit needs p0 when the function uses *args (e.g. custom functions) so it can
    # determine the number of parameters; otherwise it raises "Unable to determine
    # number of fit parameters"
    if initial_guess is None:
        initial_guess = [1.0] * len(param_names)
        logger.debug(t('log.using_initial_guess', guess=str(initial_guess)))

    # Perform curve fitting
    try:
        logger.debug(t('log.attempting_curve_fitting'))
        fit_kwargs: dict = dict(
            f=fit_func, xdata=x, ydata=y, p0=initial_guess,
            sigma=uy, absolute_sigma=True
        )
        if bounds is not None:
            fit_kwargs['bounds'] = bounds
        final_fit = curve_fit(**fit_kwargs)
        logger.debug(t('log.curve_fitting_successful'))
    except RuntimeError as e:
        # scipy.optimize.curve_fit raises RuntimeError when it can't converge
        logger.error(t('log.curve_fitting_convergence_failed', error=str(e)))
        raise FittingError(t('error.fitting_convergence_failed', error=str(e)))
    except ValueError as e:
        # ValueError when data is invalid
        logger.error(t('log.invalid_data_for_fitting', error=str(e)))
        raise FittingError(t('error.invalid_data_for_fitting', error=str(e)))
    except TypeError as e:
        # TypeError for function signature issues
        logger.error(t('log.function_signature_error', error=str(e)))
        raise FittingError(t('error.fitting_function_error', error=str(e)))
    except Exception as e:
        logger.error(t('log.unexpected_fitting_error', error=str(e)), exc_info=True)
        raise FittingError(t('error.unexpected_fitting_error', error=str(e)))
    
    # Extract parameters and uncertainties
    try:
        if len(param_names) == 1:
            params = [final_fit[0][0]]
            uncertainties = [np.sqrt(np.diag(final_fit[1]))[0]]
        else:
            params = list(final_fit[0])
            uncertainties = list(np.sqrt(np.diag(final_fit[1])))
        
        logger.debug(t('log.extracted_parameters', params=str(dict(zip(param_names, params)))))
        
        # Log if any uncertainties are infinite (informational, not an error)
        if any(np.isinf(u) for u in uncertainties):
            logger.info(t('log.infinite_uncertainties'))
        
    except Exception as e:
        logger.error(t('log.error_extracting_parameters', error=str(e)), exc_info=True)
        raise FittingError(t('error.extracting_parameters', error=str(e)))
    
    # Format parameters
    formatted_params = {}
    formatted_uncertainties = {}
    text_lines = []
    
    for name, param, uncertainty in zip(param_names, params, uncertainties):
        formatted_param, formatted_uncertainty = format_parameter(param, uncertainty)
        formatted_params[name] = formatted_param
        formatted_uncertainties[name] = formatted_uncertainty
        text_lines.append(
            '{0}={{{0}}} ,\u03C3({0})={{{0}_u}}'.format(name).format(
                **{name: formatted_param, f'{name}_u': formatted_uncertainty}
            )
        )
    
    # Calculate fitted curve
    try:
        y_fitted = fit_func(x, *params)
        logger.debug(t('log.fitted_curve_calculated', points=len(y_fitted)))
    except Exception as e:
        logger.error(t('log.error_calculating_fitted_curve', error=str(e)), exc_info=True)
        raise FittingError(t('error.calculating_fitted_curve', error=str(e)))
    
    # Calculate fit statistics
    n_points = len(y)
    n_params = len(params)
    dof = n_points - n_params
    
    # Initialize statistics dictionary
    fit_stats = {}
    
    # Calculate R² (coefficient of determination)
    try:
        ss_res = np.sum((y - y_fitted) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        fit_stats['r_squared'] = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        logger.debug(f"R² = {fit_stats['r_squared']:.6f}")
    except Exception as e:
        logger.warning("Error calculating R²: %s", str(e))
        fit_stats['r_squared'] = 0.0
    
    # Calculate chi-squared statistics
    uy_safe = np.where(np.greater(uy, 1e-15), uy, 1e-15)
    fit_stats['chi_squared'] = float(np.sum(((y - y_fitted) / uy_safe) ** 2))
    fit_stats['reduced_chi_squared'] = fit_stats['chi_squared'] / dof if dof > 0 else float('nan')
    fit_stats['dof'] = dof
    
    # Calculate 95% confidence intervals for parameters (t-distribution)
    t_crit = scipy_stats.t.ppf(0.975, dof) if dof > 0 else float('nan')
    fit_stats['confidence_intervals'] = {}
    
    for name, param, uncertainty in zip(param_names, params, uncertainties):
        if dof > 0 and np.isfinite(uncertainty) and np.isfinite(t_crit):
            ci_low = param - t_crit * uncertainty
            ci_high = param + t_crit * uncertainty
            fit_stats['confidence_intervals'][name] = {
                'low': ci_low,
                'high': ci_high,
                'available': True
            }
        else:
            fit_stats['confidence_intervals'][name] = {
                'low': None,
                'high': None,
                'available': False
            }
    
    # Generate text output using the fit_stats dictionary
    text_lines.append(f"R\u00B2={fit_stats['r_squared']:.6f}")
    text_lines.append(t('stats.chi_squared', value=f"{fit_stats['chi_squared']:.4g}"))
    text_lines.append(
        t('stats.reduced_chi_squared', value=f"{fit_stats['reduced_chi_squared']:.4g}")
    )
    text_lines.append(t('stats.dof', value=fit_stats['dof']))
    
    # Add confidence intervals
    for name in param_names:
        ci = fit_stats['confidence_intervals'][name]
        if ci['available']:
            text_lines.append(
                t(
                    'stats.param_ci_95',
                    param=name,
                    low=f"{ci['low']:.4g}",
                    high=f"{ci['high']:.4g}"
                )
            )
        else:
            text_lines.append(t('stats.param_ci_95_na', param=name))
    
    text = '\n'.join(text_lines)
    
    # Format equation with parameter values
    equation_str = equation_template.format(**formatted_params)
    logger.info(t('log.fit_completed_successfully', equation=equation_str))

    return text, y_fitted, equation_str


def get_equation_param_info(
    equation_name: str,
) -> Optional[Tuple[List[str], str]]:
    """
    Return parameter names and display formula for an equation type.

    Args:
        equation_name: String identifier for the equation type.

    Returns:
        (param_names, formula_str) or None if equation is unknown.
    """
    if equation_name not in EQUATION_PARAM_NAMES or equation_name not in EQUATION_FORMULAS:
        return None
    return (
        list(EQUATION_PARAM_NAMES[equation_name]),
        EQUATION_FORMULAS[equation_name],
    )


def merge_initial_guess(
    computed: List[float],
    override: Optional[List[Optional[float]]],
) -> List[float]:
    """Use override values where not None; otherwise keep computed."""
    if override is None or len(override) != len(computed):
        return list(computed)
    return [
        float(override[i]) if override[i] is not None else computed[i]
        for i in range(len(computed))
    ]


def merge_bounds(
    computed_bounds: Optional[Tuple[Sequence[float], Sequence[float]]],
    override_lower: Optional[List[Optional[float]]],
    override_upper: Optional[List[Optional[float]]],
    n_params: int,
) -> Optional[Tuple[Tuple[float, ...], Tuple[float, ...]]]:
    """Build (lower, upper) using overrides where not None; else computed or ±inf."""
    if override_lower is None and override_upper is None:
        return computed_bounds
    inf = float('-inf')
    pos_inf = float('inf')
    if computed_bounds is not None:
        base_lower = list(computed_bounds[0])
        base_upper = list(computed_bounds[1])
    else:
        base_lower = [inf] * n_params
        base_upper = [pos_inf] * n_params
    if override_lower is not None:
        for i, v in enumerate(override_lower):
            if i < n_params and v is not None:
                base_lower[i] = float(v)
    if override_upper is not None:
        for i, v in enumerate(override_upper):
            if i < n_params and v is not None:
                base_upper[i] = float(v)
    return (tuple(base_lower), tuple(base_upper))


def get_fitting_function(
    equation_name: str,
    initial_guess_override: Optional[List[Optional[float]]] = None,
    bounds_override: Optional[Tuple[List[Optional[float]], List[Optional[float]]]] = None,
) -> Optional[Callable]:
    """
    Get the fitting function corresponding to the equation name.

    Returns a function (data, x_name, y_name, plot_name) that performs the fit.
    If initial_guess_override or bounds_override are provided, they are passed
    to the underlying fit (None in a slot means use estimator value).

    Args:
        equation_name: String identifier for the equation type.
        initial_guess_override: Optional list of initial values (None = use estimator).
        bounds_override: Optional (lower_list, upper_list) (None in slot = use estimator).

    Returns:
        The corresponding fitting function, or None if not found or error occurs.
    """
    logger.debug(t('log.getting_fitting_function', equation=equation_name))

    if equation_name == EXIT_SIGNAL:
        logger.debug(t('log.exit_signal_received'))
        return None

    if equation_name not in EQUATION_FUNCTION_MAP:
        logger.warning(t('log.unknown_equation_type', equation=equation_name))
        return None

    function_name = EQUATION_FUNCTION_MAP[equation_name]
    logger.debug(
        t('log.equation_maps_to_function', equation=equation_name, function=function_name)
    )

    try:
        from fitting import fitting_functions
        base_fit = getattr(fitting_functions, function_name)
    except (ImportError, AttributeError) as e:
        logger.error(
            t('log.error_importing_fitting_function', function=function_name, error=str(e)),
            exc_info=True,
        )
        return None

    logger.info(t('log.successfully_loaded_fitting_function', function=function_name))

    def fit_with_overrides(
        data: Any, x_name: str, y_name: str
    ) -> Tuple[str, Any, str]:
        return base_fit(
            data,
            x_name,
            y_name,
            initial_guess_override=initial_guess_override,
            bounds_override=bounds_override,
        )

    return fit_with_overrides
