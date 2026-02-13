"""Pure hex color manipulation utilities (no config/env dependencies)."""

from typing import Tuple


def parse_hex_to_rgb(hex_color: str) -> Tuple[int, int, int] | None:
    """
    Parse a hex color string to RGB tuple (0-255 range).

    Args:
        hex_color: Hex string (e.g., '#rrggbb' or '#rgb').

    Returns:
        Tuple of (r, g, b) in 0-255 range, or None if invalid.
    """
    if not hex_color or not isinstance(hex_color, str):
        return None
    raw = hex_color.strip().lstrip("#")
    if len(raw) == 6 and all(c in "0123456789abcdefABCDEF" for c in raw):
        try:
            return (
                int(raw[0:2], 16),
                int(raw[2:4], 16),
                int(raw[4:6], 16),
            )
        except ValueError:
            return None
    if len(raw) == 3 and all(c in "0123456789abcdefABCDEF" for c in raw):
        try:
            return (
                int(raw[0] * 2, 16),
                int(raw[1] * 2, 16),
                int(raw[2] * 2, 16),
            )
        except ValueError:
            return None
    return None


def lighten_hex(hex_color: str, factor: float = 0.08, default: str = "#222222") -> str:
    """
    Return a slightly lighter shade of hex color.

    Args:
        hex_color: Input hex color (e.g., '#181818').
        factor: Amount to lighten (0-1, default 0.08).
        default: Fallback when input is invalid.

    Returns:
        Lighter hex color as #rrggbb.
    """
    rgb = parse_hex_to_rgb(hex_color)
    if rgb is None:
        return default
    r, g, b = rgb
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def muted_from_hex(hex_color: str, default: str = "#666666") -> str:
    """
    Approximate muted (grayish) color from a hex color.

    Args:
        hex_color: Input hex color.
        default: Fallback when input is invalid.

    Returns:
        Muted gray hex color as #rrggbb.
    """
    rgb = parse_hex_to_rgb(hex_color)
    if rgb is None:
        return default
    r, g, b = rgb
    mid = int(0.5 * (r + g + b) + 0.5 * 0x66)
    m = min(255, max(0, mid))
    return f"#{m:02x}{m:02x}{m:02x}"
