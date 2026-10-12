"""Shared defaults applied to all style modes.

Each style file can override any key from SHARED_RC or SHARED_CMAPS.
Missing keys fall back to these defaults.
"""

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

SHARED_CMAPS = {
    # Sequential map for idealized / pre-readout intensity images, oriented
    # low = dark (a dark hole reads dark). Detector readouts and processed
    # data products use ``readouts`` (magma) to match the survey visual
    # language; idealized noiseless model images use ``intensity``.
    "intensity": "viridis",
    "readouts": "magma",
    "high_dynamic_range": "inferno",
    "residual": "RdBu_r",
    # Signed wavefront error. A separate semantic key from ``residual``
    # (ratio / residual semantics) and from ``phase`` (the cyclic map, for
    # winding phase): an OPD map is signed and centered on zero, so it wants
    # a white-centered diverging map in every mode. Same underlying map as
    # ``residual`` today; the split is what lets either be retuned alone.
    "opd": "RdBu_r",
    # Signed statistics and SNR maps: a diverging map centered on zero that
    # keeps clear of the red-blue ``residual`` map, so a statistic is never
    # mistaken for a difference image.
    "statistic": "PuOr",
    "phase": "twilight",
    "probability": "YlOrRd_r",
    "mask": ["#FFFFFF", "#0097A7"],
    "brand_intensity": ["#FFFFFF", "#0097A7", "#000000"],
    "brand_diverging": ["#C2185B", "#FFFFFF", "#0097A7"],
}
