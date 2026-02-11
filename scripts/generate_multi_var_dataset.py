#!/usr/bin/env python
"""
Generate a single dataset with many variables (≥10) related by different
equations (linear, quadratic, exponential, ln, inverse, sin, cos, etc.),
suitable for RegressionLab fitting and exploration.
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def generate_multi_var_dataset(
    n_points: int = 80,
    x_range: Tuple[float, float] = (0.5, 10.0),
    noise_scale: float = 0.02,
    add_uncertainties: bool = True,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a dataset with one independent variable and many dependent variables
    linked by equations of the kind supported by RegressionLab.

    Variables and equations (all depend on x except where noted):
      x:   independent (grid)
      A:   linear        A = m*x + n
      B:   quadratic     B = a*x^2 + b*x + c
      C:   exponential   C = a*exp(b*x)
      D:   ln            D = a*ln(x)
      E:   inverse       E = a/x
      F:   sin           F = a*sin(b*x)
      G:   cos           G = a*cos(b*x)
      H:   inverse_sq    H = a/x^2
      I:   fourth power  I = a*x^4
      J:   logistic      J = L/(1+exp(-k*(x-x0)))
      K:   gaussian       K = A*exp(-(x-mu)^2/(2*sigma^2))
      L:   linear in A,B L = alpha*A + beta*B + gamma  (chained)
      M:   sinh          M = a*sinh(b*x)
      N:   cosh          N = a*cosh(b*x)

    Returns:
        DataFrame with columns for each variable and optionally uVar columns.
    """
    rng = np.random.default_rng(seed)
    x = np.linspace(x_range[0], x_range[1], n_points)

    # Ensure x > 0 for ln and inverse
    x_safe = np.maximum(x, 0.1)

    def noise(n: int) -> np.ndarray:
        return rng.normal(0, noise_scale, n)

    # --- Equations (same families as equations.yaml) ---
    # Linear: y = m*x + n
    m, n = 2.0, 1.0
    A = m * x + n + noise(n_points)

    # Quadratic: y = a*x^2 + b*x + c
    a_q, b_q, c_q = 0.3, -1.5, 4.0
    B = a_q * x**2 + b_q * x + c_q + noise(n_points)

    # Exponential: y = a*exp(b*x)
    a_exp, b_exp = 5.0, -0.25
    C = a_exp * np.exp(b_exp * x) + noise(n_points)

    # ln: y = a*ln(x)
    a_ln = 2.5
    D = a_ln * np.log(x_safe) + noise(n_points)

    # Inverse: y = a/x
    a_inv = 20.0
    E = a_inv / x_safe + noise(n_points)

    # sin: y = a*sin(b*x)
    a_sin, b_sin = 3.0, 0.8
    F = a_sin * np.sin(b_sin * x) + noise(n_points)

    # cos: y = a*cos(b*x)
    a_cos, b_cos = 2.0, 0.6
    G = a_cos * np.cos(b_cos * x) + noise(n_points)

    # Inverse square: y = a/x^2
    a_inv2 = 50.0
    H = a_inv2 / (x_safe**2) + noise(n_points)

    # Fourth power: y = a*x^4
    a_fourth = 0.05
    I = a_fourth * (x**4) + noise(n_points)

    # Logistic: y = L/(1+exp(-k*(x-x0)))
    L_log, k_log, x0_log = 1.0, 0.7, 5.0
    J = L_log / (1.0 + np.exp(-k_log * (x - x0_log))) + noise(n_points)

    # Gaussian: y = A*exp(-(x-mu)^2/(2*sigma^2))
    A_g, mu_g, sigma_g = 4.0, 5.0, 2.0
    K = A_g * np.exp(-((x - mu_g) ** 2) / (2.0 * sigma_g**2)) + noise(n_points)

    # Chained: linear combination of A and B
    alpha, beta, gamma = 1.0, 0.2, 0.5
    L = alpha * A + beta * B + gamma + noise(n_points)

    # sinh: y = a*sinh(b*x)
    a_sinh, b_sinh = 1.0, 0.4
    M = a_sinh * np.sinh(b_sinh * x) + noise(n_points)

    # cosh: y = a*cosh(b*x)
    a_cosh, b_cosh = 2.0, 0.3
    N = a_cosh * np.cosh(b_cosh * x) + noise(n_points)

    data: dict[str, np.ndarray] = {
        'x': x,
        'A': A,
        'B': B,
        'C': C,
        'D': D,
        'E': E,
        'F': F,
        'G': G,
        'H': H,
        'I': I,
        'J': J,
        'K': K,
        'L': L,
        'M': M,
        'N': N,
    }

    var_order = ['x', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    if add_uncertainties:
        for key in list(data.keys()):
            u = np.abs(x) * 0.01 + 0.02 if key == 'x' else np.abs(data[key]) * 0.03 + 0.05
            data[f'u{key}'] = np.maximum(u, 1e-6)
        cols = [item for name in var_order for item in (name, f'u{name}')]
    else:
        cols = var_order
    return pd.DataFrame({c: data[c] for c in cols})


def save_dataset(df: pd.DataFrame, filename: str, output_dir: str = 'input') -> Path:
    """Save dataset as CSV (and optionally .xlsx, .txt). Returns path to CSV."""
    project_root = Path(__file__).resolve().parent.parent
    out = project_root / output_dir
    out.mkdir(exist_ok=True)
    csv_path = out / f'{filename}.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Generated: {csv_path} ({len(df)} rows, {len(df.columns)} columns)")
    return csv_path


def main() -> None:
    df = generate_multi_var_dataset(
        n_points=80,
        x_range=(0.5, 10.0),
        noise_scale=0.02,
        add_uncertainties=True,
        seed=42,
    )
    save_dataset(df, 'MultiVar_Equations')
    print("\nVariables: x (independent); A..N (dependent).")
    print("Equations: linear, quadratic, exponential, ln, inverse, sin, cos,")
    print("  inverse_square, fourth_power, logistic, gaussian, linear(A,B), sinh, cosh.")


if __name__ == '__main__':
    main()
