"""Barbie mode: serif fonts and RdPu colormap."""

CMAPS = {
    "intensity": "RdPu",
    "probability": "RdPu",
    "mask": ["#FFFFFF", "#D42A92"],
    "brand_intensity": ["#FFFFFF", "#D42A92", "#5E006F"],
    "brand_diverging": ["#FAA6B7", "#FFFFFF", "#5E006F"],
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
    "lines.linewidth": 1.0,
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": 16,
    "axes.titlesize": 16,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "image.cmap": "RdPu",
}
