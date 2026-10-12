# hwostyle

Matplotlib style sheets and utilities for HWO direct imaging figures.

## Installation

```bash
pip install hwostyle
```

For development:
```bash
git clone https://github.com/HabitableWorldsObservatory/hwostyle.git
cd hwostyle
pip install -e ".[dev,test]"
```

## Quick Start

```python
import hwostyle

# Switch to paper mode (white background, muted colors)
hwostyle.use("light")

# Switch to talk mode (black background, neon colors)
hwostyle.use("dark")

# Access the palette
colors = hwostyle.palette
colors.cyan   # '#08F7FE' in dark, '#0097A7' in light

# Use domain-specific colormaps
cmap = hwostyle.cmaps.intensity   # PSF images
cmap = hwostyle.cmaps.residual    # difference maps
cmap = hwostyle.cmaps.phase       # wavefront error
cmap = hwostyle.cmaps.statistic   # signed statistics, SNR maps (PuOr)

# Brand roles: name the entity, not the color
hwostyle.roles.planet
hwostyle.roles.positive           # certified claim
```

## Modes

| Feature | Dark (Talks) | Light (Papers) | Barbie |
|---------|-------------|----------------|--------|
| Background | Black | White | White |
| Colors | Neon (high saturation) | Muted (print-safe) | RdPu pinks |
| Line width | 2.5 | 1.5 | 1.0 |
| Font | Sans-serif | Sans-serif | Serif |
| Image cmap | `magma` | `viridis` | `RdPu` |

## Color Palette

| Name   | Dark         | Light       |
|--------|-------------|-------------|
| Cyan   | `#08F7FE`   | `#0097A7`   |
| Pink   | `#FE53BB`   | `#C2185B`   |
| Yellow | `#F5D300`   | `#F9A825`   |
| Green  | `#00FF41`   | `#2E7D32`   |
| Red    | `#FF0000`   | `#D32F2F`   |
| Purple | `#9467BD`   | `#7B1FA2`   |

### Roles

A role is what a plotted entity is; it resolves to one color per theme.
Palette-backed roles follow the palette family; fixed roles keep their
color in every family (paper and barbie use the light value).

| Role | Dark | Light | Use |
|------|------|-------|-----|
| `star` | yellow | yellow | stars |
| `planet`, `measured`, `data` | cyan | cyan | planets, measured data |
| `model`, `predicted`, `highlight` | pink | pink | model output, posterior draws |
| `reference` | green | green | reference curves |
| `disk`, `envelope` | purple | purple | disks, envelopes |
| `alert` | red | red | a wrong verdict, a warning |
| `prior` | purple | purple | prior curves |
| `positive` | `#4C8DFF` | `#1565C0` | verdict: certified claim |
| `negative` | `#FF8C1A` | `#E65100` | verdict: rejected claim |
| `posterior` | `#B07A4F` | `#8E5923` | posterior curves (not `model`) |
| `truth` | `#9A9A9A` | `#757575` | scenery and true values |

`hwostyle.cmaps.statistic` (PuOr) is the diverging map for signed statistics
and SNR maps; `residual` stays red-blue for difference images.

### Barbie Palette

| Name    | Hex       |
|---------|-----------|
| Blush   | `#FAA6B7` |
| Rose    | `#F768A1` |
| Magenta | `#D42A92` |
| Berry   | `#9A017B` |
| Plum    | `#5E006F` |
