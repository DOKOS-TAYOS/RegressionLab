import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from typing import Callable, List, Tuple, Optional
from numpy.typing import NDArray
from decimal import Decimal

from config import EQUATION_FUNCTION_MAP, EXIT_SIGNAL
from utils.exceptions import FittingError
from utils.validators import validate_fitting_data
from utils.logger import get_logger
from i18n import t

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


def estimate_trigonometric_parameters(x: NDArray, y: NDArray) -> Tuple[float, float]:
    """
    Estimate initial parameters for trigonometric functions (sin/cos).
    
    This function estimates the amplitude (a) and angular frequency (b) 
    for functions of the form: y = a * sin(b*x) or y = a * cos(b*x)
    
    Args:
        x: Independent variable array
        y: Dependent variable array
        
    Returns:
        Tuple of (amplitude, frequency):
            - amplitude: Estimated amplitude parameter (a)
            - frequency: Estimated angular frequency parameter (b)
    """
    # Estimate amplitude as half the range of y values
    y_range = np.max(y) - np.min(y)
    amplitude = y_range / 2.0
    
    # Ensure amplitude is not zero
    if np.abs(amplitude) < 1e-10:
        amplitude = 1.0
    
    # Estimate frequency by finding peaks and calculating average distance
    try:
        # Find peaks in the absolute values to handle both sin and cos
        peaks, _ = find_peaks(np.abs(y - np.mean(y)), distance=max(1, len(x) // 10))
        
        if len(peaks) >= 2:
            # Calculate average distance between peaks
            peak_distances = np.diff(x[peaks])
            avg_peak_distance = np.mean(peak_distances)
            
            # For sin/cos, period = 2 * peak_distance (peak to peak)
            # Angular frequency = 2*pi / period
            estimated_period = 2.0 * avg_peak_distance
            frequency = 2.0 * np.pi / estimated_period
        else:
            # Not enough peaks found, use data range as rough estimate
            x_range = np.max(x) - np.min(x)
            # Assume at least one full period in the data
            estimated_period = x_range
            frequency = 2.0 * np.pi / estimated_period
    except Exception as e:
        logger.warning(t('log.peak_detection_failed', error=str(e)))
        # Fallback: assume one period spans the entire x range
        x_range = np.max(x) - np.min(x)
        if x_range > 0:
            frequency = 2.0 * np.pi / x_range
        else:
            frequency = 1.0
    
    # Ensure frequency is positive and reasonable
    if frequency <= 0 or not np.isfinite(frequency):
        frequency = 1.0
    
    logger.debug(t('log.estimated_trig_parameters', amplitude=f"{amplitude:.3f}", frequency=f"{frequency:.3f}"))
    return amplitude, frequency


def estimate_phase_shift(x: NDArray, y: NDArray, amplitude: float, frequency: float) -> float:
    """
    Estimate initial phase shift for trigonometric functions with phase.
    
    For functions of the form: y = a * sin(b*x + c) or y = a * cos(b*x + c)
    
    Args:
        x: Independent variable array
        y: Dependent variable array
        amplitude: Estimated amplitude parameter
        frequency: Estimated frequency parameter
        
    Returns:
        Estimated phase shift (c)
    """
    try:
        # Find the first maximum or zero crossing
        # For simplicity, estimate where the function should start
        y_normalized = y / (amplitude if amplitude != 0 else 1.0)
        
        # Find first point closest to maximum
        first_max_idx = np.argmax(y_normalized)
        x_at_max = x[first_max_idx]
        
        # For sin: max occurs at b*x + c = pi/2, so c = pi/2 - b*x
        # For cos: max occurs at b*x + c = 0, so c = -b*x
        # Use average as rough estimate
        phase = np.pi / 4.0 - frequency * x_at_max
        
        # Wrap phase to [-pi, pi]
        phase = np.arctan2(np.sin(phase), np.cos(phase))
        
    except Exception as e:
        logger.warning(t('log.phase_estimation_failed', error=str(e)))
        phase = 0.0
    
    logger.debug(t('log.estimated_phase_shift', phase=f"{phase:.3f}"))
    return phase


def generic_fit(
    data: dict,
    x_name: str,
    y_name: str,
    fit_func: Callable,
    param_names: List[str],
    equation_template: str,
    initial_guess: Optional[List[float]] = None
) -> Tuple[str, NDArray, str, float]:
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
    
    Returns:
        Tuple of (text, y_fitted, equation, r_squared):
            - text: Formatted text with parameters and uncertainties
            - y_fitted: Array with fitted y values
            - equation: Formatted equation with parameter values
            - r_squared: Coefficient of determination (R²)
            
    Raises:
        FittingError: If fitting fails or data is invalid
    """
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

    # Perform curve fitting
    try:
        logger.debug(t('log.attempting_curve_fitting'))
        if initial_guess is not None:
            logger.debug(t('log.using_initial_guess', guess=str(initial_guess)))
            final_fit = curve_fit(fit_func, x, y, p0=initial_guess, sigma=uy, absolute_sigma=True)
        else:
            final_fit = curve_fit(fit_func, x, y, sigma=uy, absolute_sigma=True)
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
    
    # Calculate R² (coefficient of determination)
    try:
        # Residual sum of squares
        ss_res = np.sum((y - y_fitted) ** 2)
        # Total sum of squares
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        # R² = 1 - (SS_res / SS_tot)
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        logger.debug(f"R² = {r_squared:.6f}")
    except Exception as e:
        logger.warning(f"Error calculating R²: {str(e)}")
        r_squared = 0.0
    
    # Add R² to the text output
    text_lines.append(f"R\u00B2={r_squared:.6f}")
    text = '\n'.join(text_lines)
    
    # Format equation with parameter values
    equation_str = equation_template.format(**formatted_params)
    logger.info(t('log.fit_completed_successfully', equation=equation_str))

    return text, y_fitted, equation_str, r_squared


def get_fitting_function(equation_name: str) -> Optional[Callable]:
    """
    Get the fitting function corresponding to the equation name.
    
    Returns the base fitting function that only performs calculations
    (without visualization). The function returns (text, y_fitted, equation).
    Uses the EQUATION_FUNCTION_MAP from config to resolve equation names
    to their implementation functions.
    
    Args:
        equation_name: String identifier for the equation type
        
    Returns:
        The corresponding fitting function, or None if not found or error occurs
    """
    logger.debug(t('log.getting_fitting_function', equation=equation_name))
    
    if equation_name == EXIT_SIGNAL:
        logger.debug(t('log.exit_signal_received'))
        return None
    
    # Import and return the appropriate fitting function
    if equation_name in EQUATION_FUNCTION_MAP:
        function_name = EQUATION_FUNCTION_MAP[equation_name]
        logger.debug(t('log.equation_maps_to_function', equation=equation_name, function=function_name))
        
        try:
            from fitting import fitting_functions
            fit_function = getattr(fitting_functions, function_name)
            logger.info(t('log.successfully_loaded_fitting_function', function=function_name))
            return fit_function
        except (ImportError, AttributeError) as e:
            # Handle import errors gracefully
            logger.error(t('log.error_importing_fitting_function', function=function_name, error=str(e)), exc_info=True)
            return None
    else:
        # Unknown equation type
        logger.warning(t('log.unknown_equation_type', equation=equation_name))
        return None
