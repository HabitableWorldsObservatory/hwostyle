"""Core style engine for hwostyle.

Manages rcParams, mode switching, and global palette/colormap state.
"""

from contextlib import contextmanager

import matplotlib.pyplot as plt
from cycler import cycler

from .colormaps import Colormaps
from .palettes import Palette, Roles
from .styles import MODE_RC, SAVE_DEFAULTS, SHARED_RC

# Global state
_current_mode = "dark"
_current_family = None
_activated = False
palette = Palette("dark")
cmaps = Colormaps("dark")
roles = Roles("dark")


def use(mode, palette_family=None):
    """Switch the global style mode and optionally the palette family.

    Args:
        mode: One of "dark" (talks), "light" (papers), "paper" (tol-colors),
            or "barbie".
        palette_family: Palette family name. One of "cyberpunk", "spectral",
            "biosignature", "tol" (Tol muted), "tol-light", or "barbie".
            Defaults to "cyberpunk" for dark/light, "tol" for paper, and
            "barbie" for barbie mode.

    Raises:
        ValueError: If mode or palette family is invalid.
    """
    global _current_mode, _current_family, _activated, palette, cmaps, roles

    if mode not in MODE_RC:
        msg = f"Mode must be 'dark', 'light', or 'barbie', got '{mode}'"
        raise ValueError(msg)

    _current_mode = mode
    _current_family = palette_family
    _activated = True
    palette = Palette(mode, family=palette_family)
    cmaps = Colormaps(mode)
    roles = Roles(mode, family=palette_family)

    rc = {**SHARED_RC}
    rc.update(MODE_RC[mode])
    rc["axes.prop_cycle"] = cycler(color=palette.as_list)
    plt.rcParams.update(rc)


@contextmanager
def dark(palette_family=None):
    """Context manager for dark mode. Restores previous mode on exit."""
    prev_mode, prev_family = _current_mode, _current_family
    use("dark", palette_family)
    yield
    use(prev_mode, prev_family)


@contextmanager
def light(palette_family=None):
    """Context manager for light mode. Restores previous mode on exit."""
    prev_mode, prev_family = _current_mode, _current_family
    use("light", palette_family)
    yield
    use(prev_mode, prev_family)


@contextmanager
def barbie():
    """Context manager for barbie mode. Restores previous mode on exit."""
    prev_mode, prev_family = _current_mode, _current_family
    use("barbie")
    yield
    use(prev_mode, prev_family)


@contextmanager
def paper(palette_family=None):
    """Context manager for paper mode (tol-colors). Restores previous mode on exit."""
    prev_mode, prev_family = _current_mode, _current_family
    use("paper", palette_family)
    yield
    use(prev_mode, prev_family)


def current_mode():
    """Return the active style mode, or None if use() has never been called.

    The module initializes palette/cmaps objects in dark mode for attribute
    access, but no mode is considered active until use() runs.
    """
    return _current_mode if _activated else None


def save_defaults(mode=None):
    """Savefig policy for a mode as a plain dict.

    Args:
        mode: Mode name. Defaults to the active mode, or "light" when no
            mode has been activated.

    Returns:
        Dict with keys dpi, facecolor, transparent, bbox_inches. A copy;
        mutating it does not alter the policy.
    """
    m = mode if mode is not None else (current_mode() or "light")
    if m not in SAVE_DEFAULTS:
        msg = f"Unknown mode '{m}'; expected one of {sorted(SAVE_DEFAULTS)}"
        raise ValueError(msg)
    return dict(SAVE_DEFAULTS[m])
