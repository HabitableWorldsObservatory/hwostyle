"""Dark mode: neon-on-black for talks and presentations."""

import tol_colors as tc

from ..palettes import CYBERPUNK_DARK

RC = {
    "figure.facecolor": "black",
    "axes.facecolor": "black",
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "white",
    "text.color": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "#333333",
    "legend.facecolor": "#1a1a1a",
    "legend.edgecolor": "#444444",
    "legend.labelcolor": "white",
    "lines.linewidth": 2.5,
}

# The shared table is drawn for a white page. On black the sequential Tol maps
# that run pale to dark are reversed so low values sit at the page end;
# ``intensity`` already runs dark to pale in the shared table.
CMAPS = {
    "probability": tc.YlOrBr.reversed(),
    "pupil": tc.WhOrBr.reversed(),
    "mask": ["#333333", "#737373"],
    "brand_intensity": ["#000000", CYBERPUNK_DARK["cyan"], "#FFFFFF"],
    "brand_diverging": [CYBERPUNK_DARK["pink"], "#000000", CYBERPUNK_DARK["cyan"]],
}
