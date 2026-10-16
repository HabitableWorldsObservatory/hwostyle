"""hwostyle: Matplotlib styles, palettes, and colormaps for HWO.

Usage::

    import hwostyle

    hwostyle.use("light")
    hwostyle.use("dark", palette_family="biosignature")

    hwostyle.palette.o2
    hwostyle.cmaps.intensity
    hwostyle.roles.planet

    # Color utilities
    from hwostyle.colors import wavelength_to_rgb, contrast_ratio
"""

from . import colors, core, motifs
from .core import barbie, current_mode, dark, light, paper, save_defaults, use

try:
    from ._version import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0.dev"


def __getattr__(name):
    """Forward ``palette``, ``cmaps``, and ``roles`` to the live core state."""
    if name in ("palette", "cmaps", "roles"):
        return getattr(core, name)
    raise AttributeError(f"module 'hwostyle' has no attribute {name!r}")


__all__ = [
    "barbie",
    "cmaps",
    "colors",
    "current_mode",
    "dark",
    "light",
    "motifs",
    "palette",
    "paper",
    "roles",
    "save_defaults",
    "use",
]
