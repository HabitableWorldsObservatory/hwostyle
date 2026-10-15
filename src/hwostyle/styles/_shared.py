"""Shared defaults applied to all style modes.

Each style file can override any key from SHARED_RC or SHARED_CMAPS.
Missing keys fall back to these defaults.
"""

import tol_colors as tc

SHARED_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica", "Arial"],
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 13,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
    "figure.titlesize": 16,
    "savefig.dpi": 300,
}

# Image roles use Paul Tol maps through ``tol_colors`` (no color data is copied
# here). The same maps serve light, dark and paper; for the sequential ones the
# page decides the orientation, so low values sit at the page end. The
# page-end orientation lives in ``dark.py``.
SHARED_CMAPS = {
    # Sequential map for idealized / pre-readout intensity images, oriented
    # low = dark (a dark hole reads dark) on every page. Detector readouts and
    # processed data products use ``readouts`` (magma) to match the survey
    # visual language; idealized noiseless model images use ``intensity``.
    "intensity": tc.iridescent.reversed(),
    "readouts": "magma",
    # Deprecated: use ``intensity`` or ``readouts``. Kept for one minor release.
    "high_dynamic_range": "inferno",
    "residual": tc.BuRd,
    # Signed wavefront error. A separate semantic key from ``residual``
    # (ratio / residual semantics) and from ``phase`` (the cyclic map, for
    # winding phase): an OPD map is signed and centered on zero, so it wants
    # a light-centered diverging map in every mode.
    "opd": tc.PRGn.reversed(),
    # Signed statistics and SNR maps: a diverging map centered on zero that
    # keeps clear of the ``residual`` and ``opd`` maps, so a statistic is never
    # mistaken for a difference image.
    "statistic": tc.nightfall.reversed(),
    "phase": "twilight",
    # Posterior and scatter density, pale to dark on a light page.
    "probability": tc.YlOrBr,
    # Pupil transmission (0 to 1). Pupil and probability share their colors, so
    # they must never appear in the same figure.
    "pupil": tc.WhOrBr,
    "mask": ["#CCCCCC", "#8C8C8C"],
    "brand_intensity": ["#FFFFFF", "#0097A7", "#000000"],
    "brand_diverging": ["#C2185B", "#FFFFFF", "#0097A7"],
}
