"""Application constants, equation mappings, and version."""

EQUATION_FUNCTION_MAP = {
    'linear_function_with_n': 'fit_linear_function_with_n',
    'linear_function': 'fit_linear_function',
    'quadratic_function_complete': 'fit_quadratic_function_complete',
    'quadratic_function': 'fit_quadratic_function',
    'fourth_power': 'fit_fourth_power',
    'ln_function': 'fit_ln_function',
    'inverse_function': 'fit_inverse_function',
    'inverse_square_function': 'fit_inverse_square_function',
    'sin_function': 'fit_sin_function',
    'sin_function_with_c': 'fit_sin_function_with_c',
    'cos_function': 'fit_cos_function',
    'cos_function_with_c': 'fit_cos_function_with_c',
    'tan_function': 'fit_tan_function',
    'tan_function_with_c': 'fit_tan_function_with_c',
    'sinh_function': 'fit_sinh_function',
    'cosh_function': 'fit_cosh_function',
    'exponential_function': 'fit_exponential_function',
    'binomial_function': 'fit_binomial_function',
    'gaussian_function': 'fit_gaussian_function',
    'square_pulse_function': 'fit_square_pulse_function',
    'hermite_polynomial_3': 'fit_hermite_polynomial_3',
    'hermite_polynomial_4': 'fit_hermite_polynomial_4',
}

AVAILABLE_EQUATION_TYPES = list(EQUATION_FUNCTION_MAP.keys())

EQUATION_FORMULAS: dict[str, str] = {
    'linear_function_with_n': 'y = mx + n',
    'linear_function': 'y = mx',
    'quadratic_function_complete': 'y = ax² + bx + c',
    'quadratic_function': 'y = ax²',
    'fourth_power': 'y = ax⁴',
    'sin_function': 'y = a·sin(bx)',
    'sin_function_with_c': 'y = a·sin(bx + c)',
    'cos_function': 'y = a·cos(bx)',
    'cos_function_with_c': 'y = a·cos(bx + c)',
    'sinh_function': 'y = a·sinh(bx)',
    'cosh_function': 'y = a·cosh(bx)',
    'ln_function': 'y = a·ln(x)',
    'inverse_function': 'y = a/x',
    'inverse_square_function': 'y = a/x²',
    'gaussian_function': 'y = a·exp(-(x-μ)²/(2σ²))',
    'exponential_function': 'y = a·exp(bx)',
    'binomial_function': 'y = L/(1 + exp(-k(x-x₀)))',
    'tan_function': 'y = a·tan(bx)',
    'tan_function_with_c': 'y = a·tan(bx + c)',
    'square_pulse_function': 'y = a si |x-x₀| ≤ w/2, else 0',
    'hermite_polynomial_3': 'y = Σ cᵢ·Hᵢ(x) (grado 0-3)',
    'hermite_polynomial_4': 'y = Σ cᵢ·Hᵢ(x) (grado 0-4)',
}

EQUATION_PARAM_NAMES: dict[str, list[str]] = {
    'linear_function_with_n': ['n', 'm'],
    'linear_function': ['m'],
    'quadratic_function_complete': ['a', 'b', 'c'],
    'quadratic_function': ['a'],
    'fourth_power': ['a'],
    'sin_function': ['a', 'b'],
    'sin_function_with_c': ['a', 'b', 'c'],
    'cos_function': ['a', 'b'],
    'cos_function_with_c': ['a', 'b', 'c'],
    'sinh_function': ['a', 'b'],
    'cosh_function': ['a', 'b'],
    'ln_function': ['a'],
    'inverse_function': ['a'],
    'inverse_square_function': ['a'],
    'gaussian_function': ['A', 'mu', 'sigma'],
    'exponential_function': ['a', 'b'],
    'binomial_function': ['a', 'b', 'c'],
    'tan_function': ['a', 'b'],
    'tan_function_with_c': ['a', 'b', 'c'],
    'square_pulse_function': ['A', 't0', 'w'],
    'hermite_polynomial_3': ['c0', 'c1', 'c2', 'c3'],
    'hermite_polynomial_4': ['c0', 'c1', 'c2', 'c3', 'c4'],
}

MATH_FUNCTION_REPLACEMENTS = {
    r'\bln\b': 'np.log',
    r'\bsin\b': 'np.sin',
    r'\bcos\b': 'np.cos',
    r'\btan\b': 'np.tan',
    r'\bsinh\b': 'np.sinh',
    r'\bcosh\b': 'np.cosh',
    r'\btanh\b': 'np.tanh',
    r'\bexp\b': 'np.exp',
    r'\bsqrt\b': 'np.sqrt',
    r'\babs\b': 'np.abs',
    r'\bpi\b': 'np.pi',
    r'\be\b': 'np.e',
}

__version__ = "0.8.2"

EXIT_SIGNAL = 'Salir'
