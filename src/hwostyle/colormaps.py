"""Data-driven colormap registry for HWO figures.

Colormap preferences are defined in the styles package. Each style file
specifies overrides on top of the shared defaults. This class simply
looks up the resolved value for the current mode.
"""

from matplotlib.colors import LinearSegmentedColormap

from .styles import MODE_CMAPS


def _resolve(value, name):
    """Turn a string, color-list, or Colormap into a usable matplotlib colormap."""
    if isinstance(value, str):
        return value
    if isinstance(value, LinearSegmentedColormap):
        return value
    return LinearSegmentedColormap.from_list(
        f"hwo_{name}", value, N=256 if len(value) > 2 else 2
    )


class Colormaps:
    """Mode-aware colormap registry with semantic names.

    Access colormaps by their intended use rather than by implementation name.
    The returned colormap depends on the current mode.

    Categories:
        intensity (idealized / noiseless model images, low = dark),
        readouts (detector readouts + processed data products; magma),
        high_dynamic_range, residual, statistic (signed statistics and
        SNR maps; PuOr), phase, probability, mask,
        brand_intensity, brand_diverging.
    """

    def __init__(self, mode="dark"):
        """Initialize colormaps for the given mode."""
        self._mode = mode
        self._cmaps = MODE_CMAPS[mode]

    def __getattr__(self, name):
        """Look up a colormap by semantic name."""
        if name.startswith("_"):
            raise AttributeError(name)
        cmaps = object.__getattribute__(self, "_cmaps")
        if name in cmaps:
            return _resolve(cmaps[name], name)
        msg = f"No colormap '{name}'. Available: {list(cmaps.keys())}"
        raise AttributeError(msg)

    def __repr__(self):
        """String representation."""
        return f"Colormaps(mode='{self._mode}')"
