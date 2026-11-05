"""
Shared Test Context & Utility Functions for Vyasa Mahabharata E2E Tests.
Contains database helpers, WCAG contrast calculations, damped wave physics models,
typography checks, and file system paths.
"""

import math
import os
import re
import sqlite3
import tempfile
from typing import Dict, List, Optional, Tuple, Any


def get_project_root() -> str:
    """Returns absolute path to the project root directory."""
    # From tests/e2e/test_context.py -> up 2 levels
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(cur_dir, "..", ".."))


def get_db_path() -> str:
    """Returns absolute path to the pre-packaged SQLite database asset."""
    return os.path.join(get_project_root(), "app", "src", "main", "assets", "mahabharata.db")


def get_gradle_properties_path() -> str:
    """Returns absolute path to gradle.properties."""
    return os.path.join(get_project_root(), "gradle.properties")


def get_ci_workflow_path() -> str:
    """Returns absolute path to the GitHub Actions build workflow."""
    return os.path.join(get_project_root(), ".github", "workflows", "build-apk.yml")


def connect_db(read_only: bool = True) -> sqlite3.Connection:
    """
    Connects to the assets database.
    If read_only is True, opens with URI read-only flag.
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database asset not found at {db_path}")
        
    if read_only:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
    else:
        conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_in_memory_db_copy() -> sqlite3.Connection:
    """
    Creates an in-memory clone of the assets database for isolated write tests.
    Leaves the main asset untouched.
    """
    src_conn = connect_db(read_only=True)
    mem_conn = sqlite3.connect(":memory:")
    src_conn.backup(mem_conn)
    src_conn.close()
    mem_conn.row_factory = sqlite3.Row
    return mem_conn


# =====================================================================
# WCAG 2.1 Color & Contrast Utilities
# =====================================================================

def parse_hex_color(hex_str: str) -> Tuple[int, int, int]:
    """Parses #RRGGBB hex string into (R, G, B) tuple in 0..255."""
    clean_hex = hex_str.strip().lstrip("#")
    if len(clean_hex) == 8:
        # ARGB or RGBA - take RGB
        clean_hex = clean_hex[2:] if clean_hex.startswith("FF") else clean_hex[:6]
    if len(clean_hex) != 6:
        raise ValueError(f"Invalid hex color code: {hex_str}")
    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)
    return r, g, b


def srgb_channel_to_linear(val_255: int) -> float:
    """Converts 0..255 sRGB color channel to linear relative value."""
    s = val_255 / 255.0
    if s <= 0.04045:
        return s / 12.92
    return math.pow((s + 0.055) / 1.055, 2.4)


def calculate_relative_luminance(hex_str: str) -> float:
    """Calculates WCAG 2.1 relative luminance for a given hex color."""
    r, g, b = parse_hex_color(hex_str)
    r_lin = srgb_channel_to_linear(r)
    g_lin = srgb_channel_to_linear(g)
    b_lin = srgb_channel_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """
    Calculates the WCAG 2.1 contrast ratio between two colors:
    (L1 + 0.05) / (L2 + 0.05) where L1 is the lighter color.
    """
    l1 = calculate_relative_luminance(hex1)
    l2 = calculate_relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# =====================================================================
# Physics: Damped Harmonic Oscillator Wave Simulation
# =====================================================================

def damped_wave_amplitude(
    t: float,
    amplitude: float = 1.0,
    damping_ratio: float = 0.15,
    natural_frequency: float = 10.0,
    distance_r: float = 0.0,
    wave_speed: float = 1.0
) -> float:
    """
    Simulates concentric circular ripple wave:
    y(r, t) = A_0 * e^(-zeta * omega * (t - r/v)) * cos(omega_d * (t - r/v))
    Returns wave height at distance r and time t.
    """
    if damping_ratio >= 1.0:
        raise ValueError("System must be underdamped (zeta < 1.0) for oscillatory ripples")
        
    delayed_t = t - (distance_r / wave_speed if wave_speed > 0 else 0)
    if delayed_t < 0:
        return 0.0  # Wavefront has not reached this point yet
        
    omega_d = natural_frequency * math.sqrt(1.0 - damping_ratio ** 2)
    envelope = amplitude * math.exp(-damping_ratio * natural_frequency * delayed_t)
    return envelope * math.cos(omega_d * delayed_t)


# =====================================================================
# Typography & Measure Utilities
# =====================================================================

def verify_line_height_ratio(font_size_sp: float, line_height_sp: float, target_ratio: float = 1.8) -> bool:
    """Verifies that line_height_sp / font_size_sp matches the target ratio within float tolerance."""
    if font_size_sp <= 0:
        return False
    actual_ratio = line_height_sp / font_size_sp
    return abs(actual_ratio - target_ratio) < 0.01


def calculate_cpl(container_width_dp: float, font_size_sp: float, avg_char_width_em: float = 0.6) -> float:
    """
    Calculates expected Characters Per Line (CPL) given container width and font size.
    In typography, 1 em = font_size_sp.
    """
    char_width_dp = font_size_sp * avg_char_width_em
    if char_width_dp <= 0:
        return 0.0
    return container_width_dp / char_width_dp


# =====================================================================
# Quote Card Exporter Geometry Specifications
# =====================================================================

QUOTE_CARD_WIDTH = 1080
QUOTE_CARD_HEIGHT = 1350
QUOTE_CARD_ASPECT_RATIO = QUOTE_CARD_WIDTH / QUOTE_CARD_HEIGHT  # 0.8 (4:5 portrait)
