"""Paper mode: publication-ready style using tol-colors for accessibility.

Uses the tol-colors 'light' qualitative colorset for line/scatter plots
and the 'iridescent' sequential colormap for continuous data. These are
designed for print-safe, colorblind-friendly scientific figures.
"""

import tol_colors as tc

# Pull the tol 'light' qualitative colors as a list
_tol_light = tc.light
TOL_LIGHT_COLORS = list(_tol_light)

# Iridescent colormap from tol-colors
TOL_IRIDESCENT = tc.iridescent


# ``intensity`` and the other image roles come from the shared table.
# ``sequential`` keeps the native (low = light) iridescent orientation.
CMAPS = {
    "sequential": TOL_IRIDESCENT,
}

RC = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "black",
    "text.color": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "grid.color": "#cccccc",
    "legend.facecolor": "white",
    "legend.edgecolor": "#999999",
    "legend.labelcolor": "black",
    "lines.linewidth": 1.5,
}
