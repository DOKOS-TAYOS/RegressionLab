#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test dataset generator for RegressionLab.
Creates Excel files with simulated experimental data following the structure
of Ejemplo.xlsx and Exper1.xlsx.
"""

# Standard library
from pathlib import Path
from typing import Tuple

# Third-party packages
import numpy as np
import pandas as pd


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
    Save dataset in Excel format.
    
    Args:
        df: DataFrame to save
        filename: File name (without extension)
        output_dir: Output directory (relative to project root)
    """
    # Get project root (parent of scripts/)
    project_root = Path(__file__).parent.parent
    output_path = project_root / output_dir
    output_path.mkdir(exist_ok=True)
    
    filepath = output_path / f'{filename}.xlsx'
    df.to_excel(filepath, index=False)
    print(f'Generated: {filepath}')


def main() -> None:
    """
    Generate all test datasets.
    
    Creates comprehensive test datasets with different mathematical relationships
    to test ALL fitting capabilities of the RegressionLab application.
    Each dataset simulates realistic experimental data with:
    - Realistic noise levels
    - Measurement uncertainties
    - Various units and variable names
    - Both simple and LaTeX notation
    - Some datasets with 3 magnitudes (x, y, z)
    
    Function types covered:
    - Linear: linear_function, linear_function_with_n
    - Logarithmic: ln_function
    - Polynomial: quadratic_function, quadratic_function_complete, fourth_power
    - Trigonometric: sin_function, sin_function_with_c, cos_function, cos_function_with_c
    - Hyperbolic: sinh_function, cosh_function
    - Inverse: inverse_function, inverse_square_function
    """
    
    print("=" * 80)
    print("Test Dataset Generator - RegressionLab")
    print("=" * 80)
    print()
    
    # ========================================================================
    # LINEAR FUNCTIONS
    # ========================================================================
    
    # Dataset 1: Linear through origin - y = mx
    print("Generating Linear1.xlsx (proportional relationship)...")
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
    
    # Dataset 2: Linear with intercept - y = mx + n
    print("Generating Linear2.xlsx (uniform motion)...")
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
    
    # Dataset 3: Linear with LaTeX notation - Ohm's Law
    print("Generating Linear3_Ohm.xlsx (Ohm's law)...")
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
    # LOGARITHMIC FUNCTIONS
    # ========================================================================
    
    # Dataset 4: Logarithmic - y = a*ln(x)
    print("Generating Logarithmic1.xlsx (pH scale)...")
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
    
    # Dataset 5: Logarithmic with LaTeX
    print("Generating Logarithmic2.xlsx (sound intensity)...")
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
    
    # Dataset 6: Quadratic through origin - y = ax^2
    print("Generating Quadratic1.xlsx (kinetic energy)...")
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
    
    # Dataset 7: Quadratic complete - y = ax^2 + bx + c
    print("Generating Quadratic2_Complete.xlsx (projectile motion)...")
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
    
    # Dataset 8: Quadratic - Fluid flow
    print("Generating Quadratic3_Fluid.xlsx (Bernoulli)...")
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
    
    # Dataset 9: Fourth power - y = ax^4 (Stefan-Boltzmann law)
    print("Generating FourthPower1.xlsx (Stefan-Boltzmann)...")
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
    
    # Dataset 10: Sine - y = a*sin(bx)
    print("Generating Sine1.xlsx (simple harmonic motion)...")
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
    
    # Dataset 11: Sine with phase - y = a*sin(bx + c)
    print("Generating Sine2_Phase.xlsx (AC voltage)...")
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
    
    # Dataset 12: Cosine - y = a*cos(bx)
    print("Generating Cosine1.xlsx (oscillation)...")
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
    
    # Dataset 13: Cosine with phase - y = a*cos(bx + c)
    print("Generating Cosine2_Phase.xlsx (wave motion)...")
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
    # HYPERBOLIC FUNCTIONS
    # ========================================================================
    
    # Dataset 14: Hyperbolic sine - y = a*sinh(bx)
    print("Generating HyperbolicSine1.xlsx (catenary)...")
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
    
    # Dataset 15: Hyperbolic cosine - y = a*cosh(bx)
    print("Generating HyperbolicCosine1.xlsx (hanging cable)...")
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
    
    # Dataset 16: Inverse - y = a/x (Boyle's law)
    print("Generating Inverse1_Boyle.xlsx (Boyle's law)...")
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
    
    # Dataset 17: Inverse square - y = a/x^2 (Radiation intensity)
    print("Generating Inverse2_Radiation.xlsx (inverse square law)...")
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
    
    # Dataset 18: Inverse square (Gravitational force)
    print("Generating Inverse3_Gravity.xlsx (gravitational force)...")
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
    # 3-VARIABLE DATASETS (More than 2 magnitudes)
    # ========================================================================
    
    # Dataset 19: 3-variable linear - z = m1*x + m2*y + n
    print("Generating 3Var_Linear1.xlsx (3 magnitudes - linear)...")
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
    
    # Dataset 20: 3-variable quadratic - z = a*x^2 + b*y^2 + c
    print("Generating 3Var_Quadratic1.xlsx (3 magnitudes - quadratic)...")
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
    
    # Dataset 21: 3-variable mixed (using existing generation)
    print("Generating 3Var_Mixed1.xlsx (3 magnitudes - combined)...")
    n = 20
    x = np.linspace(1.0, 10.0, n)
    y = np.linspace(0.5, 5.0, n)
    z = 50.0 / x + 2.0 * y + np.random.normal(0, 0.5, n)
    ux = np.random.uniform(0.1, 0.3, n)
    uy = np.random.uniform(0.05, 0.15, n)
    uz = np.random.uniform(0.2, 0.4, n)
    df21 = pd.DataFrame({'x': x, 'ux': ux, 'y': y, 'uy': uy, 'z': z, 'uz': uz})
    df21 = rename_columns_simple_3var(df21, 'P', 'T', 'V', 'kPa', 'K', 'L')
    save_dataset(df21, '3Var_Mixed1')
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print()
    print("=" * 80)
    print(f"Generated 21 test datasets in 'input' directory")
    print("=" * 80)
    print()
    print("Generated datasets by function type:")
    print()
    print("LINEAR FUNCTIONS (3 datasets):")
    print("  - Linear1.xlsx: Proportional (y = mx)")
    print("  - Linear2.xlsx: With intercept (y = mx + n)")
    print("  - Linear3_Ohm.xlsx: Ohm's law (LaTeX)")
    print()
    print("LOGARITHMIC FUNCTIONS (2 datasets):")
    print("  - Logarithmic1.xlsx: pH scale")
    print("  - Logarithmic2.xlsx: Sound intensity (LaTeX)")
    print()
    print("QUADRATIC FUNCTIONS (3 datasets):")
    print("  - Quadratic1.xlsx: Through origin (y = ax^2)")
    print("  - Quadratic2_Complete.xlsx: Complete (y = ax^2 + bx + c)")
    print("  - Quadratic3_Fluid.xlsx: Bernoulli equation")
    print()
    print("FOURTH POWER FUNCTION (1 dataset):")
    print("  - FourthPower1.xlsx: Stefan-Boltzmann law")
    print()
    print("SINE FUNCTIONS (2 datasets):")
    print("  - Sine1.xlsx: Simple harmonic (y = a*sin(bx))")
    print("  - Sine2_Phase.xlsx: With phase (y = a*sin(bx + c))")
    print()
    print("COSINE FUNCTIONS (2 datasets):")
    print("  - Cosine1.xlsx: Simple (y = a*cos(bx))")
    print("  - Cosine2_Phase.xlsx: With phase (y = a*cos(bx + c))")
    print()
    print("HYPERBOLIC FUNCTIONS (2 datasets):")
    print("  - HyperbolicSine1.xlsx: Catenary (y = a*sinh(bx))")
    print("  - HyperbolicCosine1.xlsx: Hanging cable (y = a*cosh(bx))")
    print()
    print("INVERSE FUNCTIONS (3 datasets):")
    print("  - Inverse1_Boyle.xlsx: Boyle's law (y = a/x)")
    print("  - Inverse2_Radiation.xlsx: Inverse square (y = a/x^2)")
    print("  - Inverse3_Gravity.xlsx: Gravitational force (y = a/x^2)")
    print()
    print("3-VARIABLE DATASETS (3 datasets with more than 2 magnitudes):")
    print("  - 3Var_Linear1.xlsx: Linear (z = m1*x + m2*y + n)")
    print("  - 3Var_Quadratic1.xlsx: Quadratic (z = a*x^2 + b*y^2 + c)")
    print("  - 3Var_Mixed1.xlsx: Mixed (z = a/x + b*y)")
    print()


if __name__ == '__main__':
    main()
