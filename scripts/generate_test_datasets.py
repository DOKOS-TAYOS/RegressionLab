#!/usr/bin/env python
"""
Test dataset generator for RegressionLab.

Creates datasets in multiple formats (Excel .xlsx, CSV, TXT) with simulated
experimental data. Each dataset targets one or more equation types used by the
application (linear, quadratic, logarithmic, trigonometric, hyperbolic, inverse,
exponential, Gaussian, logistic, tangent, square pulse, Hermite polynomials).
Datasets are documented with a short description and, where relevant, the
physical phenomenon they represent (e.g. Ohm's law, Boyle's law, projectile
motion).
"""

# Standard library
from pathlib import Path
from typing import Tuple

# Third-party packages
import numpy as np
import pandas as pd
from scipy.special import eval_hermite


def generate_linear_data(
    n_points: int,
    x_range: Tuple[float, float],
    slope: float,
    intercept: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a linear relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        slope: Slope of the linear relationship
        intercept: Y-intercept
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = slope * x + intercept + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_exponential_data(
    n_points: int,
    x_range: Tuple[float, float],
    amplitude: float,
    decay: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following an exponential relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        amplitude: Amplitude of the exponential
        decay: Decay factor
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = amplitude * np.exp(-decay * x) + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_quadratic_data(
    n_points: int,
    x_range: Tuple[float, float],
    a: float,
    b: float,
    c: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a quadratic relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        a, b, c: Coefficients of the parabola (ax² + bx + c)
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = a * x**2 + b * x + c + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_power_law_data(
    n_points: int,
    x_range: Tuple[float, float],
    coefficient: float,
    exponent: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a power law relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values (must be > 0)
        coefficient: Power law coefficient
        exponent: Exponent
        noise: Relative Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(max(x_range[0], 0.1), x_range[1], n_points)
    y_base = coefficient * np.power(x, exponent)
    y = y_base * (1 + np.random.normal(0, noise, n_points))
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.abs(y) * np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_ln_data(
    n_points: int,
    x_range: Tuple[float, float],
    coefficient: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a logarithmic relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values (must be > 0)
        coefficient: Logarithm coefficient
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(max(x_range[0], 0.1), x_range[1], n_points)
    y = coefficient * np.log(x) + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_sin_data(
    n_points: int,
    x_range: Tuple[float, float],
    amplitude: float,
    frequency: float,
    phase: float = 0.0,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a sine relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        amplitude: Sine amplitude
        frequency: Sine frequency
        phase: Phase shift (default 0)
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = amplitude * np.sin(frequency * x + phase) + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_cos_data(
    n_points: int,
    x_range: Tuple[float, float],
    amplitude: float,
    frequency: float,
    phase: float = 0.0,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a cosine relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        amplitude: Cosine amplitude
        frequency: Cosine frequency
        phase: Phase shift (default 0)
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = amplitude * np.cos(frequency * x + phase) + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_sinh_data(
    n_points: int,
    x_range: Tuple[float, float],
    amplitude: float,
    coefficient: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a hyperbolic sine relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        amplitude: Amplitude coefficient
        coefficient: Coefficient inside sinh
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = amplitude * np.sinh(coefficient * x) + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.abs(y) * np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_cosh_data(
    n_points: int,
    x_range: Tuple[float, float],
    amplitude: float,
    coefficient: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a hyperbolic cosine relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        amplitude: Amplitude coefficient
        coefficient: Coefficient inside cosh
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = amplitude * np.cosh(coefficient * x) + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.abs(y) * np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_fourth_power_data(
    n_points: int,
    x_range: Tuple[float, float],
    coefficient: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a fourth power relationship with noise.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        coefficient: Fourth power coefficient
        noise: Relative Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        
    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y_base = coefficient * np.power(x, 4)
    y = y_base * (1 + np.random.normal(0, noise, n_points))
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.abs(y) * np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_gaussian_data(
    n_points: int,
    x_range: Tuple[float, float],
    A: float,
    mu: float,
    sigma: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a Gaussian (normal) distribution with noise.
    y = A * exp(-(x-mu)^2 / (2*sigma^2)).

    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = A * np.exp(-((x - mu) ** 2) / (2.0 * sigma**2)) + np.random.normal(0, noise, n_points)
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_logistic_data(
    n_points: int,
    x_range: Tuple[float, float],
    a: float,
    b: float,
    c: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a logistic (S-shaped) curve with noise.
    y = a / (1 + exp(-b*(x-c))).

    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = a / (1.0 + np.exp(-b * (x - c))) + np.random.normal(0, noise, n_points)
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_tan_data(
    n_points: int,
    x_range: Tuple[float, float],
    amplitude: float,
    frequency: float,
    phase: float = 0.0,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a tangent relationship with noise.
    y = a*tan(b*x) or y = a*tan(b*x + c). x_range must avoid asymptotes (e.g. ±π/2).

    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = amplitude * np.tan(frequency * x + phase) + np.random.normal(0, noise, n_points)
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_square_pulse_data(
    n_points: int,
    x_range: Tuple[float, float],
    A: float,
    t0: float,
    w: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data following a smooth square pulse (tanh-based).
    Same model as fitting_functions.square_pulse_function: pulse amplitude A,
    center t0, width w.

    Returns:
        DataFrame with columns x, ux, y, uy
    """
    k = 50.0
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = A * 0.5 * (
        np.tanh(k * (x - (t0 - w / 2.0))) - np.tanh(k * (x - (t0 + w / 2.0)))
    ) + np.random.normal(0, noise, n_points)
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def generate_hermite_data(
    n_points: int,
    x_range: Tuple[float, float],
    coeffs: Tuple[float, ...],
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate data as a sum of physicist's Hermite polynomials with noise.
    y = c0*H_0(x) + c1*H_1(x) + ... (length of coeffs defines degree).

    Returns:
        DataFrame with columns x, ux, y, uy
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = np.zeros_like(x)
    for i, c in enumerate(coeffs):
        y = y + c * eval_hermite(i, x)
    y = y + np.random.normal(0, noise, n_points)
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy})


def rename_columns_simple(
    df: pd.DataFrame,
    x_var: str,
    y_var: str,
    x_unit: str,
    y_unit: str
) -> pd.DataFrame:
    """
    Rename columns with simple notation (Ejemplo.xlsx style).
    
    Args:
        df: DataFrame with columns x, ux, y, uy
        x_var: Name of x variable
        y_var: Name of y variable
        x_unit: Unit of x
        y_unit: Unit of y
        
    Returns:
        DataFrame with renamed columns
    """
    df_renamed = df.copy()
    df_renamed.columns = [
        f'{x_var}({x_unit})',
        f'u{x_var}({x_unit})',
        f'{y_var}({y_unit})',
        f'u{y_var}({y_unit})'
    ]
    return df_renamed


def rename_columns_latex(
    df: pd.DataFrame,
    x_var: str,
    y_var: str,
    x_unit: str,
    y_unit: str
) -> pd.DataFrame:
    """
    Rename columns with LaTeX notation (Exper1.xlsx style).
    
    Args:
        df: DataFrame with columns x, ux, y, uy
        x_var: Name of x variable in LaTeX
        y_var: Name of y variable in LaTeX
        x_unit: Unit of x in LaTeX
        y_unit: Unit of y in LaTeX
        
    Returns:
        DataFrame with renamed columns
    """
    df_renamed = df.copy()
    df_renamed.columns = [
        f'${x_var} ({x_unit})$',
        f'u${x_var} ({x_unit})$',
        f'${y_var} ({y_unit})$',
        f'u${y_var} ({y_unit})$'
    ]
    return df_renamed


def rename_columns_simple_3var(
    df: pd.DataFrame,
    x_var: str,
    y_var: str,
    z_var: str,
    x_unit: str,
    y_unit: str,
    z_unit: str
) -> pd.DataFrame:
    """
    Rename columns with simple notation for 3 variables.
    
    Args:
        df: DataFrame with columns x, ux, y, uy, z, uz
        x_var: Name of x variable
        y_var: Name of y variable
        z_var: Name of z variable
        x_unit: Unit of x
        y_unit: Unit of y
        z_unit: Unit of z
        
    Returns:
        DataFrame with renamed columns
    """
    df_renamed = df.copy()
    df_renamed.columns = [
        f'{x_var}({x_unit})',
        f'u{x_var}({x_unit})',
        f'{y_var}({y_unit})',
        f'u{y_var}({y_unit})',
        f'{z_var}({z_unit})',
        f'u{z_var}({z_unit})'
    ]
    return df_renamed


def rename_columns_latex_3var(
    df: pd.DataFrame,
    x_var: str,
    y_var: str,
    z_var: str,
    x_unit: str,
    y_unit: str,
    z_unit: str
) -> pd.DataFrame:
    """
    Rename columns with LaTeX notation for 3 variables.
    
    Args:
        df: DataFrame with columns x, ux, y, uy, z, uz
        x_var: Name of x variable in LaTeX
        y_var: Name of y variable in LaTeX
        z_var: Name of z variable in LaTeX
        x_unit: Unit of x in LaTeX
        y_unit: Unit of y in LaTeX
        z_unit: Unit of z in LaTeX
        
    Returns:
        DataFrame with renamed columns
    """
    df_renamed = df.copy()
    df_renamed.columns = [
        f'${x_var} ({x_unit})$',
        f'u${x_var} ({x_unit})$',
        f'${y_var} ({y_unit})$',
        f'u${y_var} ({y_unit})$',
        f'${z_var} ({z_unit})$',
        f'u${z_var} ({z_unit})$'
    ]
    return df_renamed


def generate_3var_linear_data(
    n_points: int,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    m1: float,
    m2: float,
    intercept: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.1,
    z_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate 3-variable data following z = m1*x + m2*y + intercept.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        y_range: Tuple with (min, max) for y values
        m1: Coefficient for x
        m2: Coefficient for y
        intercept: Intercept value
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        z_uncertainty: Base uncertainty in z
        
    Returns:
        DataFrame with columns x, ux, y, uy, z, uz
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = np.linspace(y_range[0], y_range[1], n_points)
    z = m1 * x + m2 * y + intercept + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    uz = np.random.uniform(z_uncertainty * 0.5, z_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy, 'z': z, 'uz': uz})


def generate_3var_quadratic_data(
    n_points: int,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    a: float,
    b: float,
    c: float,
    noise: float = 0.1,
    x_uncertainty: float = 0.1,
    y_uncertainty: float = 0.1,
    z_uncertainty: float = 0.2
) -> pd.DataFrame:
    """
    Generate 3-variable data following z = a*x^2 + b*y^2 + c.
    
    Args:
        n_points: Number of points to generate
        x_range: Tuple with (min, max) for x values
        y_range: Tuple with (min, max) for y values
        a: Coefficient for x^2
        b: Coefficient for y^2
        c: Constant term
        noise: Gaussian noise factor
        x_uncertainty: Base uncertainty in x
        y_uncertainty: Base uncertainty in y
        z_uncertainty: Base uncertainty in z
        
    Returns:
        DataFrame with columns x, ux, y, uy, z, uz
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    y = np.linspace(y_range[0], y_range[1], n_points)
    z = a * x**2 + b * y**2 + c + np.random.normal(0, noise, n_points)
    
    ux = np.random.uniform(x_uncertainty * 0.5, x_uncertainty * 1.5, n_points)
    uy = np.random.uniform(y_uncertainty * 0.5, y_uncertainty * 1.5, n_points)
    uz = np.random.uniform(z_uncertainty * 0.5, z_uncertainty * 1.5, n_points)
    
    return pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy, 'z': z, 'uz': uz})


def save_dataset(df: pd.DataFrame, filename: str, output_dir: str = 'input') -> None:
    """
    Save dataset in Excel (.xlsx), CSV and TXT formats.

    Args:
        df: DataFrame to save
        filename: File name (without extension)
        output_dir: Output directory (relative to project root)
    """
    # Get project root (parent of scripts/)
    project_root = Path(__file__).parent.parent
    output_path = project_root / output_dir
    output_path.mkdir(exist_ok=True)

    # .xlsx
    xlsx_path = output_path / f'{filename}.xlsx'
    df.to_excel(xlsx_path, index=False)
    print(f'Generated: {xlsx_path}')

    # .csv (comma-separated, UTF-8)
    csv_path = output_path / f'{filename}.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f'Generated: {csv_path}')

    # .txt (tab-separated for compatibility with loading_utils.txt_reader)
    txt_path = output_path / f'{filename}.txt'
    df.to_csv(txt_path, index=False, sep='\t', encoding='utf-8')
    print(f'Generated: {txt_path}')


def main() -> None:
    """
    Generate all test datasets for every equation type supported by RegressionLab.

    Each dataset is documented with: equation type, short description, and
    physical phenomenon when applicable. Output: .xlsx, .csv, .txt per dataset.
    """
    print("=" * 80)
    print("Test Dataset Generator - RegressionLab")
    print("=" * 80)
    print()

    # ========================================================================
    # LINEAR FUNCTIONS
    # ========================================================================
    # Equation: linear_function (y = mx). Proportional relationship.
    # Physical: Force vs acceleration (F = ma), or any y ∝ x.
    # ------------------------------------------------------------------------
    print("Generating Linear1 (linear_function: y = mx, proportional)...")
    df1 = generate_linear_data(
        n_points=15,
        x_range=(1.0, 10.0),
        slope=3.5,
        intercept=0.0,
        noise=0.2,
        x_uncertainty=0.1,
        y_uncertainty=0.3
    )
    df1 = rename_columns_simple(df1, 'F', 'a', 'N', 'm/s^2')
    save_dataset(df1, 'Linear1')

    # Equation: linear_function_with_n (y = mx + n). Linear with intercept.
    # Physical: Uniform rectilinear motion (position = v*t + x0), calibration lines.
    # ------------------------------------------------------------------------
    print("Generating Linear2 (linear_function_with_n: y = mx + n, uniform motion)...")
    df2 = generate_linear_data(
        n_points=20,
        x_range=(0.5, 10.0),
        slope=2.5,
        intercept=1.0,
        noise=0.3,
        x_uncertainty=0.1,
        y_uncertainty=0.2
    )
    df2 = rename_columns_simple(df2, 't', 'v', 's', 'm/s')
    save_dataset(df2, 'Linear2')

    # Equation: linear_function_with_n. Ohm's law: V = R*I + offset.
    # Physical: Voltage vs current in a resistor (Ohm's law).
    # ------------------------------------------------------------------------
    print("Generating Linear3_Ohm (Ohm's law: V = R*I + offset)...")
    df3 = generate_linear_data(
        n_points=15,
        x_range=(0.1, 5.0),
        slope=100.0,
        intercept=0.5,
        noise=2.0,
        x_uncertainty=0.01,
        y_uncertainty=1.0
    )
    df3 = rename_columns_latex(df3, 'I', 'V', 'A', 'V')
    save_dataset(df3, 'Linear3_Ohm')

    # ========================================================================
    # EXPONENTIAL FUNCTION
    # ========================================================================
    # Equation: exponential_function (y = a*exp(b*x)). Here b < 0 (decay).
    # Physical: Radioactive decay, Newton cooling, RC discharge.
    # ------------------------------------------------------------------------
    print("Generating Exponential1 (exponential_function: decay, y = a*exp(b*x), b<0)...")
    df_exp = generate_exponential_data(
        n_points=20,
        x_range=(0.0, 5.0),
        amplitude=100.0,
        decay=0.5,
        noise=2.0,
        x_uncertainty=0.05,
        y_uncertainty=1.0
    )
    df_exp = rename_columns_simple(df_exp, 't', 'N', 's', '')
    save_dataset(df_exp, 'Exponential1')

    # ========================================================================
    # LOGARITHMIC FUNCTIONS
    # ========================================================================
    # Equation: ln_function (y = a*ln(x)).
    # Physical: pH vs concentration (log scale), sound level (dB) vs intensity.
    # ------------------------------------------------------------------------
    print("Generating Logarithmic1 (ln_function: y = a*ln(x), pH/concentration)...")
    df4 = generate_ln_data(
        n_points=20,
        x_range=(0.5, 50.0),
        coefficient=2.5,
        noise=0.1,
        x_uncertainty=0.5,
        y_uncertainty=0.15
    )
    df4 = rename_columns_simple(df4, 'C', 'pH', 'mol/L', '')
    save_dataset(df4, 'Logarithmic1')

    # ln_function. Sound intensity level (dB) vs intensity I.
    # ------------------------------------------------------------------------
    print("Generating Logarithmic2 (ln_function: sound intensity / dB)...")
    df5 = generate_ln_data(
        n_points=15,
        x_range=(1.0, 100.0),
        coefficient=10.0,
        noise=0.5,
        x_uncertainty=1.0,
        y_uncertainty=0.3
    )
    df5 = rename_columns_latex(df5, 'I', 'L', 'W/m^2', 'dB')
    save_dataset(df5, 'Logarithmic2')

    # ========================================================================
    # QUADRATIC FUNCTIONS
    # ========================================================================
    # Equation: quadratic_function (y = ax^2). Parabola through origin.
    # Physical: Kinetic energy E = (1/2)mv^2, power in resistor P = I^2*R.
    # ------------------------------------------------------------------------
    print("Generating Quadratic1 (quadratic_function: y = ax^2, kinetic energy)...")
    df6 = generate_quadratic_data(
        n_points=18,
        x_range=(0, 10.0),
        a=0.5,
        b=0.0,
        c=0.0,
        noise=0.5,
        x_uncertainty=0.2,
        y_uncertainty=0.3
    )
    df6 = rename_columns_simple(df6, 'v', 'E', 'm/s', 'J')
    save_dataset(df6, 'Quadratic1')

    # Equation: quadratic_function_complete (y = ax^2 + bx + c).
    # Physical: Projectile height h(t) = h0 + v0*t - (g/2)*t^2.
    # ------------------------------------------------------------------------
    print("Generating Quadratic2_Complete (quadratic_function_complete: projectile motion)...")
    df7 = generate_quadratic_data(
        n_points=25,
        x_range=(0, 5.0),
        a=-4.9,
        b=20.0,
        c=1.5,
        noise=0.3,
        x_uncertainty=0.1,
        y_uncertainty=0.2
    )
    df7 = rename_columns_latex(df7, 't', 'h', 's', 'm')
    save_dataset(df7, 'Quadratic2_Complete')

    # quadratic_function_complete. Bernoulli-type pressure vs velocity (quadratic in v).
    # ------------------------------------------------------------------------
    print("Generating Quadratic3_Fluid (quadratic_function_complete: Bernoulli)...")
    df8 = generate_quadratic_data(
        n_points=20,
        x_range=(0.5, 5.0),
        a=-2.0,
        b=15.0,
        c=10.0,
        noise=1.0,
        x_uncertainty=0.1,
        y_uncertainty=0.5
    )
    df8 = rename_columns_latex(df8, 'v', 'P', '\\frac{m}{s}', 'kPa')
    save_dataset(df8, 'Quadratic3_Fluid')

    # ========================================================================
    # FOURTH POWER FUNCTION
    # ========================================================================
    # Equation: fourth_power (y = ax^4).
    # Physical: Stefan–Boltzmann law: radiant power P ∝ T^4.
    # ------------------------------------------------------------------------
    print("Generating FourthPower1 (fourth_power: Stefan-Boltzmann, P ~ T^4)...")
    df9 = generate_fourth_power_data(
        n_points=12,
        x_range=(1.0, 5.0),
        coefficient=5.67e-8,
        noise=0.05,
        x_uncertainty=0.1,
        y_uncertainty=0.1
    )
    df9 = rename_columns_latex(df9, 'T', 'P', 'K', 'W/m^2')
    save_dataset(df9, 'FourthPower1')

    # ========================================================================
    # SINE FUNCTIONS
    # ========================================================================
    # Equation: sin_function (y = a*sin(b*x)).
    # Physical: Simple harmonic motion (position vs time), AC signal without phase.
    # ------------------------------------------------------------------------
    print("Generating Sine1 (sin_function: y = a*sin(bx), harmonic motion)...")
    df10 = generate_sin_data(
        n_points=30,
        x_range=(0, 4*np.pi),
        amplitude=5.0,
        frequency=1.0,
        phase=0.0,
        noise=0.2,
        x_uncertainty=0.1,
        y_uncertainty=0.15
    )
    df10 = rename_columns_simple(df10, 't', 'x', 's', 'm')
    save_dataset(df10, 'Sine1')

    # Equation: sin_function_with_c (y = a*sin(b*x + c)).
    # Physical: AC voltage/current with phase shift, waves.
    # ------------------------------------------------------------------------
    print("Generating Sine2_Phase (sin_function_with_c: AC voltage with phase)...")
    df11 = generate_sin_data(
        n_points=25,
        x_range=(0, 2*np.pi),
        amplitude=220.0,
        frequency=2.0,
        phase=np.pi/4,
        noise=5.0,
        x_uncertainty=0.05,
        y_uncertainty=3.0
    )
    df11 = rename_columns_latex(df11, 't', 'V', 's', 'V')
    save_dataset(df11, 'Sine2_Phase')

    # ========================================================================
    # COSINE FUNCTIONS
    # ========================================================================
    # Equation: cos_function (y = a*cos(b*x)).
    # Physical: Oscillation starting at maximum (e.g. spring at t=0).
    # ------------------------------------------------------------------------
    print("Generating Cosine1 (cos_function: y = a*cos(bx), oscillation)...")
    df12 = generate_cos_data(
        n_points=30,
        x_range=(0, 4*np.pi),
        amplitude=3.0,
        frequency=0.5,
        phase=0.0,
        noise=0.15,
        x_uncertainty=0.1,
        y_uncertainty=0.1
    )
    df12 = rename_columns_simple(df12, 't', 'y', 's', 'cm')
    save_dataset(df12, 'Cosine1')

    # Equation: cos_function_with_c (y = a*cos(b*x + c)).
    # Physical: Wave displacement vs position with phase.
    # ------------------------------------------------------------------------
    print("Generating Cosine2_Phase (cos_function_with_c: wave motion)...")
    df13 = generate_cos_data(
        n_points=40,
        x_range=(0, 3*np.pi),
        amplitude=2.5,
        frequency=1.5,
        phase=np.pi/3,
        noise=0.1,
        x_uncertainty=0.05,
        y_uncertainty=0.08
    )
    df13 = rename_columns_latex(df13, 'x', 'A', 'm', 'mm')
    save_dataset(df13, 'Cosine2_Phase')

    # ========================================================================
    # TANGENT FUNCTIONS
    # ========================================================================
    # Equation: tan_function (y = a*tan(b*x)). Domain chosen to avoid asymptotes.
    # Physical: Refraction angle vs incidence (within a branch), some optical relations.
    # ------------------------------------------------------------------------
    print("Generating Tan1 (tan_function: y = a*tan(bx))...")
    df_tan1 = generate_tan_data(
        n_points=25,
        x_range=(-0.8, 0.8),
        amplitude=2.0,
        frequency=1.0,
        phase=0.0,
        noise=0.1,
        x_uncertainty=0.02,
        y_uncertainty=0.15
    )
    df_tan1 = rename_columns_simple(df_tan1, 'x', 'y', 'rad', '')
    save_dataset(df_tan1, 'Tan1')

    # Equation: tan_function_with_c (y = a*tan(b*x + c)).
    # ------------------------------------------------------------------------
    print("Generating Tan2_Phase (tan_function_with_c: y = a*tan(bx+c))...")
    df_tan2 = generate_tan_data(
        n_points=25,
        x_range=(-0.6, 0.6),
        amplitude=1.5,
        frequency=1.2,
        phase=0.3,
        noise=0.08,
        x_uncertainty=0.02,
        y_uncertainty=0.1
    )
    df_tan2 = rename_columns_simple(df_tan2, 'x', 'y', 'rad', '')
    save_dataset(df_tan2, 'Tan2_Phase')

    # ========================================================================
    # HYPERBOLIC FUNCTIONS
    # ========================================================================
    # Equation: sinh_function (y = a*sinh(b*x)).
    # Physical: Catenary (ideal hanging chain), some growth models.
    # ------------------------------------------------------------------------
    print("Generating HyperbolicSine1 (sinh_function: catenary)...")
    df14 = generate_sinh_data(
        n_points=20,
        x_range=(-2.0, 2.0),
        amplitude=2.0,
        coefficient=1.0,
        noise=0.1,
        x_uncertainty=0.05,
        y_uncertainty=0.1
    )
    df14 = rename_columns_simple(df14, 'x', 'y', 'm', 'm')
    save_dataset(df14, 'HyperbolicSine1')

    # Equation: cosh_function (y = a*cosh(b*x)).
    # Physical: Catenary (hanging cable), arch shape.
    # ------------------------------------------------------------------------
    print("Generating HyperbolicCosine1 (cosh_function: hanging cable)...")
    df15 = generate_cosh_data(
        n_points=25,
        x_range=(-3.0, 3.0),
        amplitude=10.0,
        coefficient=0.5,
        noise=0.2,
        x_uncertainty=0.1,
        y_uncertainty=0.15
    )
    df15 = rename_columns_latex(df15, 'x', 'h', 'm', 'm')
    save_dataset(df15, 'HyperbolicCosine1')

    # ========================================================================
    # INVERSE FUNCTIONS
    # ========================================================================
    # Equation: inverse_function (y = a/x).
    # Physical: Boyle's law (ideal gas): P*V = constant → P = k/V.
    # ------------------------------------------------------------------------
    print("Generating Inverse1_Boyle (inverse_function: Boyle's law P ~ 1/V)...")
    df16 = generate_power_law_data(
        n_points=15,
        x_range=(1.0, 10.0),
        coefficient=100.0,
        exponent=-1.0,
        noise=0.03,
        x_uncertainty=0.1,
        y_uncertainty=0.05
    )
    df16 = rename_columns_latex(df16, 'V', 'P', 'L', 'kPa')
    save_dataset(df16, 'Inverse1_Boyle')

    # Equation: inverse_square_function (y = a/x^2).
    # Physical: Intensity of radiation vs distance (inverse square law).
    # ------------------------------------------------------------------------
    print("Generating Inverse2_Radiation (inverse_square_function: intensity vs distance)...")
    df17 = generate_power_law_data(
        n_points=12,
        x_range=(1.0, 5.0),
        coefficient=100.0,
        exponent=-2.0,
        noise=0.05,
        x_uncertainty=0.05,
        y_uncertainty=0.1
    )
    df17 = rename_columns_simple(df17, 'd', 'I', 'm', 'W/m^2')
    save_dataset(df17, 'Inverse2_Radiation')

    # inverse_square_function. Gravitational force F ∝ 1/r^2.
    # ------------------------------------------------------------------------
    print("Generating Inverse3_Gravity (inverse_square_function: gravity F ~ 1/r^2)...")
    df18 = generate_power_law_data(
        n_points=10,
        x_range=(1.0, 10.0),
        coefficient=6.67e-11,
        exponent=-2.0,
        noise=0.05,
        x_uncertainty=0.1,
        y_uncertainty=0.1
    )
    df18 = rename_columns_latex(df18, 'r', 'F', 'm', 'N')
    save_dataset(df18, 'Inverse3_Gravity')

    # ========================================================================
    # GAUSSIAN FUNCTION
    # ========================================================================
    # Equation: gaussian_function (y = A*exp(-(x-mu)^2/(2*sigma^2))).
    # Physical: Normal distribution, spectral lines, beam intensity profile.
    # ------------------------------------------------------------------------
    print("Generating Gaussian1 (gaussian_function: bell curve / spectral line)...")
    df_gauss = generate_gaussian_data(
        n_points=40,
        x_range=(0.0, 10.0),
        A=5.0,
        mu=5.0,
        sigma=1.2,
        noise=0.1,
        x_uncertainty=0.1,
        y_uncertainty=0.12
    )
    df_gauss = rename_columns_simple(df_gauss, 'x', 'I', 'mm', 'a.u.')
    save_dataset(df_gauss, 'Gaussian1')

    # ========================================================================
    # LOGISTIC (BINOMIAL) FUNCTION
    # ========================================================================
    # Equation: binomial_function (y = a/(1+exp(-b*(x-c)))). S-shaped curve.
    # Physical: Population growth with saturation, dose-response, activation curves.
    # ------------------------------------------------------------------------
    print("Generating Logistic1 (binomial_function: logistic / dose-response)...")
    df_log = generate_logistic_data(
        n_points=30,
        x_range=(-2.0, 8.0),
        a=1.0,
        b=0.8,
        c=3.0,
        noise=0.03,
        x_uncertainty=0.1,
        y_uncertainty=0.02
    )
    df_log = rename_columns_simple(df_log, 'dose', 'response', 'mg', '')
    save_dataset(df_log, 'Logistic1')

    # ========================================================================
    # SQUARE PULSE FUNCTION
    # ========================================================================
    # Equation: square_pulse_function (smooth pulse: A, center t0, width w).
    # Physical: Gate signal, rectangular pulse approximation, detector response.
    # ------------------------------------------------------------------------
    print("Generating SquarePulse1 (square_pulse_function: smooth rectangular pulse)...")
    df_pulse = generate_square_pulse_data(
        n_points=50,
        x_range=(0.0, 10.0),
        A=2.0,
        t0=5.0,
        w=2.0,
        noise=0.05,
        x_uncertainty=0.05,
        y_uncertainty=0.06
    )
    df_pulse = rename_columns_simple(df_pulse, 't', 'V', 's', 'V')
    save_dataset(df_pulse, 'SquarePulse1')

    # ========================================================================
    # HERMITE POLYNOMIALS
    # ========================================================================
    # Equation: hermite_polynomial_3 (y = c0*H_0(x) + ... + c3*H_3(x)).
    # Physical: Quantum oscillator wavefunctions, orthogonal basis fits.
    # ------------------------------------------------------------------------
    print("Generating Hermite3_1 (hermite_polynomial_3: sum of H_0..H_3)...")
    df_h3 = generate_hermite_data(
        n_points=35,
        x_range=(-2.0, 2.0),
        coeffs=(1.0, 0.5, -0.3, 0.2),
        noise=0.08,
        x_uncertainty=0.05,
        y_uncertainty=0.06
    )
    df_h3 = rename_columns_simple(df_h3, 'x', 'y', '', '')
    save_dataset(df_h3, 'Hermite3_1')

    # Equation: hermite_polynomial_4 (y = c0*H_0(x) + ... + c4*H_4(x)).
    # ------------------------------------------------------------------------
    print("Generating Hermite4_1 (hermite_polynomial_4: sum of H_0..H_4)...")
    df_h4 = generate_hermite_data(
        n_points=40,
        x_range=(-2.0, 2.0),
        coeffs=(1.0, 0.4, -0.2, 0.1, 0.05),
        noise=0.06,
        x_uncertainty=0.05,
        y_uncertainty=0.05
    )
    df_h4 = rename_columns_simple(df_h4, 'x', 'y', '', '')
    save_dataset(df_h4, 'Hermite4_1')

    # ========================================================================
    # 3-VARIABLE DATASETS (More than 2 magnitudes)
    # ========================================================================
    # Multi-magnitude datasets (x, y, z). For workflows that support 3 variables.
    # ------------------------------------------------------------------------
    print("Generating 3Var_Linear1 (3 magnitudes, linear z = m1*x + m2*y + n)...")
    df19 = generate_3var_linear_data(
        n_points=20,
        x_range=(0, 10.0),
        y_range=(0, 5.0),
        m1=2.0,
        m2=3.0,
        intercept=1.0,
        noise=0.5,
        x_uncertainty=0.2,
        y_uncertainty=0.15,
        z_uncertainty=0.3
    )
    df19 = rename_columns_simple_3var(df19, 'x', 'y', 'z', 'm', 'm', 'm')
    save_dataset(df19, '3Var_Linear1')

    # 3-variable quadratic: z = a*x^2 + b*y^2 + c (e.g. energy surface).
    # ------------------------------------------------------------------------
    print("Generating 3Var_Quadratic1 (3 magnitudes, quadratic z = a*x^2 + b*y^2 + c)...")
    df20 = generate_3var_quadratic_data(
        n_points=25,
        x_range=(0, 5.0),
        y_range=(0, 3.0),
        a=1.5,
        b=2.0,
        c=0.5,
        noise=0.3,
        x_uncertainty=0.1,
        y_uncertainty=0.08,
        z_uncertainty=0.2
    )
    df20 = rename_columns_latex_3var(df20, 'x', 'y', 'E', 'm', 'm', 'J')
    save_dataset(df20, '3Var_Quadratic1')

    # 3-variable mixed: z = a/x + b*y (combined inverse and linear).
    # ------------------------------------------------------------------------
    print("Generating 3Var_Mixed1 (3 magnitudes, mixed z = a/x + b*y)...")
    rng_mixed = np.random.default_rng(42)
    n = 20
    x = np.linspace(1.0, 10.0, n)
    y = np.linspace(0.5, 5.0, n)
    z = 50.0 / x + 2.0 * y + rng_mixed.normal(0, 0.5, n)
    ux = rng_mixed.uniform(0.1, 0.3, n)
    uy = rng_mixed.uniform(0.05, 0.15, n)
    uz = rng_mixed.uniform(0.2, 0.4, n)
    df21 = pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy, 'z': z, 'uz': uz})
    df21 = rename_columns_simple_3var(df21, 'P', 'T', 'V', 'kPa', 'K', 'L')
    save_dataset(df21, '3Var_Mixed1')
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print()
    print("=" * 80)
    print("Generated 30 test datasets in 'input' (xlsx, csv, txt each)")
    print("=" * 80)
    print()
    print("Datasets by equation type (description / physical phenomenon):")
    print()
    print("LINEAR:")
    print("  - Linear1: linear_function (y = mx) - Force vs acceleration, proportionality")
    print("  - Linear2: linear_function_with_n (y = mx + n) - Uniform motion, calibration")
    print("  - Linear3_Ohm: linear_function_with_n - Ohm's law (V vs I)")
    print()
    print("EXPONENTIAL:")
    print("  - Exponential1: exponential_function (y = a*exp(b*x), b<0) - Decay, cooling, RC")
    print()
    print("LOGARITHMIC:")
    print("  - Logarithmic1: ln_function (y = a*ln(x)) - pH vs concentration")
    print("  - Logarithmic2: ln_function - Sound level (dB) vs intensity")
    print()
    print("QUADRATIC:")
    print("  - Quadratic1: quadratic_function (y = ax^2) - Kinetic energy E ~ v^2")
    print("  - Quadratic2_Complete: quadratic_function_complete - Projectile height h(t)")
    print("  - Quadratic3_Fluid: quadratic_function_complete - Bernoulli (P vs v)")
    print()
    print("FOURTH POWER:")
    print("  - FourthPower1: fourth_power (y = ax^4) - Stefan-Boltzmann P ~ T^4")
    print()
    print("SINE / COSINE:")
    print("  - Sine1: sin_function - Harmonic motion, AC without phase")
    print("  - Sine2_Phase: sin_function_with_c - AC voltage with phase")
    print("  - Cosine1: cos_function - Oscillation from maximum")
    print("  - Cosine2_Phase: cos_function_with_c - Wave with phase")
    print()
    print("TANGENT:")
    print("  - Tan1: tan_function (y = a*tan(bx))")
    print("  - Tan2_Phase: tan_function_with_c (y = a*tan(bx+c))")
    print()
    print("HYPERBOLIC:")
    print("  - HyperbolicSine1: sinh_function - Catenary")
    print("  - HyperbolicCosine1: cosh_function - Hanging cable / arch")
    print()
    print("INVERSE:")
    print("  - Inverse1_Boyle: inverse_function (y = a/x) - Boyle's law P*V = const")
    print("  - Inverse2_Radiation: inverse_square_function - Intensity vs distance")
    print("  - Inverse3_Gravity: inverse_square_function - Gravitational force F ~ 1/r^2")
    print()
    print("GAUSSIAN / LOGISTIC / PULSE / HERMITE:")
    print("  - Gaussian1: gaussian_function - Bell curve, spectral line")
    print("  - Logistic1: binomial_function - Logistic / dose-response S-curve")
    print("  - SquarePulse1: square_pulse_function - Smooth rectangular pulse")
    print("  - Hermite3_1: hermite_polynomial_3 - Sum H_0...H_3")
    print("  - Hermite4_1: hermite_polynomial_4 - Sum H_0...H_4")
    print()
    print("3-VARIABLE (multi-magnitude):")
    print("  - 3Var_Linear1: z = m1*x + m2*y + n")
    print("  - 3Var_Quadratic1: z = a*x^2 + b*y^2 + c")
    print("  - 3Var_Mixed1: z = a/x + b*y")
    print()


if __name__ == '__main__':
    main()
