"""Color palette definitions for hwostyle.

Palettes are organized by family (cyberpunk, spectral, biosignature, barbie)
and by mode (dark, light). Each palette is a dict mapping color names to hex
values.

Brand roles live here too (:class:`Roles`): they are palette color names
under a semantic alias, so a figure can ask for ``planet`` rather than
``cyan`` and get one pinned color per entity across every figure.
"""

from cycler import cycler

# =============================================================================
# Cyberpunk palette (default)
# =============================================================================

CYBERPUNK_DARK = {
    "cyan": "#08F7FE",
    "pink": "#FE53BB",
    "yellow": "#F5D300",
    "green": "#00FF41",
    "red": "#FF0000",
    "purple": "#9467BD",
}

CYBERPUNK_LIGHT = {
    "cyan": "#0097A7",
    "pink": "#C2185B",
    "yellow": "#F9A825",
    "green": "#2E7D32",
    "red": "#D32F2F",
    "purple": "#7B1FA2",
}

# =============================================================================
# Spectral line palette -- colors from real emission wavelengths
# =============================================================================

SPECTRAL = {
    "oiii": "#4AACE3",  # [OIII] 500 nm -- blue-green
    "h_alpha": "#E84855",  # H-alpha 656 nm -- warm red
    "h_beta": "#5BC0BE",  # H-beta 486 nm -- cyan
    "nai_d": "#F9C22E",  # NaI D 589 nm -- gold
    "nii": "#9B5DE5",  # [NII] 658 nm -- violet
    "sii": "#43AA8B",  # [SII] 672 nm -- teal
}

# =============================================================================
# Biosignature palette -- molecules HWO will hunt for
# =============================================================================

BIOSIGNATURE = {
    "o2": "#E84855",  # O2 A-band 760 nm -- deep red
    "h2o": "#4A90D9",  # Water -- blue (cultural association)
    "o3": "#43AA8B",  # Ozone Chappuis band -- green/teal
    "ch4": "#F4A261",  # Methane -- warm amber
    "co2": "#9B8EC4",  # Carbon dioxide -- gray-violet
    "rayleigh": "#5BC0BE",  # Rayleigh scattering slope -- sky blue
}

# =============================================================================
# Barbie palette -- RdPu-sampled pinks
# =============================================================================

BARBIE = {
    "blush": "#FAA6B7",
    "rose": "#F768A1",
    "magenta": "#D42A92",
    "berry": "#9A017B",
    "plum": "#5E006F",
}

# =============================================================================
# Tol Light palette -- from tol-colors, colorblind-friendly for papers
# =============================================================================

try:
    import tol_colors as tc

    _tol = tc.light
    TOL_LIGHT = {
        "light_blue": _tol.light_blue,
        "orange": _tol.orange,
        "light_yellow": _tol.light_yellow,
        "pink": _tol.pink,
        "light_cyan": _tol.light_cyan,
        "mint": _tol.mint,
        "pear": _tol.pear,
        "olive": _tol.olive,
        "pale_grey": _tol.pale_grey,
    }
except ImportError:
    TOL_LIGHT = None

# =============================================================================
# Registry: (mode, palette_family) -> color dict
# =============================================================================

# For spectral and biosignature, the same colors work on both backgrounds
# because they were designed for mid-range saturation.
PALETTE_REGISTRY = {
    ("dark", "cyberpunk"): CYBERPUNK_DARK,
    ("light", "cyberpunk"): CYBERPUNK_LIGHT,
    ("dark", "spectral"): SPECTRAL,
    ("light", "spectral"): SPECTRAL,
    ("dark", "biosignature"): BIOSIGNATURE,
    ("light", "biosignature"): BIOSIGNATURE,
    ("barbie", "barbie"): BARBIE,
    # Allow barbie mode to use other palettes too
    ("barbie", "cyberpunk"): BARBIE,
    ("barbie", "spectral"): SPECTRAL,
    ("barbie", "biosignature"): BIOSIGNATURE,
}

# Register tol palette if tol_colors is available
if TOL_LIGHT is not None:
    PALETTE_REGISTRY[("paper", "tol")] = TOL_LIGHT
    # Also allow tol palette in light mode
    PALETTE_REGISTRY[("light", "tol")] = TOL_LIGHT

# Backwards compat: legacy aliases
DARK_COLORS = CYBERPUNK_DARK
LIGHT_COLORS = CYBERPUNK_LIGHT
BARBIE_COLORS = BARBIE


class Palette:
    """Mode-aware color palette with named palette families.

    Provides named color access (by key), index access, and a matplotlib
    cycler for the current palette.

    Palette families:
        - ``"cyberpunk"``: Neon colors (dark) / muted variants (light).
          Default for dark and light modes.
        - ``"spectral"``: Colors from real emission lines (OIII, H-alpha,
          H-beta, NaI D, [NII], [SII]).
        - ``"biosignature"``: Colors representing molecules HWO will detect
          (O2, H2O, O3, CH4, CO2, Rayleigh).
        - ``"barbie"``: Monochromatic pink gradient from RdPu.
    """

    def __init__(self, mode="dark", family=None):
        """Initialize palette for the given mode and family.

        Args:
            mode: Either "dark", "light", or "barbie".
            family: Palette family name. If None, defaults to "cyberpunk"
                for dark/light and "barbie" for barbie mode.
        """
        self._mode = mode
        if family is None:
            if mode == "barbie":
                family = "barbie"
            elif mode == "paper":
                family = "tol"
            else:
                family = "cyberpunk"
        self._family = family

        key = (mode, family)
        if key not in PALETTE_REGISTRY:
            available = sorted({f for _, f in PALETTE_REGISTRY})
            msg = f"Unknown palette family '{family}'. Available: {available}"
            raise ValueError(msg)

        self._colors = PALETTE_REGISTRY[key]

    @property
    def mode(self):
        """Current mode name."""
        return self._mode

    @property
    def family(self):
        """Current palette family name."""
        return self._family

    @property
    def names(self):
        """Color names in this palette."""
        return list(self._colors.keys())

    @property
    def as_list(self):
        """All colors as a list in canonical order."""
        return list(self._colors.values())

    @property
    def as_dict(self):
        """All colors as a name -> hex dict."""
        return dict(self._colors)

    @property
    def cycler(self):
        """Matplotlib color cycler for the current palette."""
        return cycler(color=self.as_list)

    def __getattr__(self, name):
        """Access color by name (e.g. palette.cyan, palette.o2)."""
        if name.startswith("_"):
            raise AttributeError(name)
        colors = object.__getattribute__(self, "_colors")
        if name in colors:
            return colors[name]
        msg = (
            f"Palette '{self._family}' has no color '{name}'. "
            f"Available: {list(colors.keys())}"
        )
        raise AttributeError(msg)

    def __getitem__(self, idx):
        """Access color by index or name."""
        if isinstance(idx, str):
            return self._colors[idx]
        return self.as_list[idx]

    def __iter__(self):
        """Iterate over colors."""
        return iter(self.as_list)

    def __len__(self):
        """Number of colors in the palette."""
        return len(self._colors)

    def __repr__(self):
        """String representation."""
        return (
            f"Palette(mode='{self._mode}', family='{self._family}', "
            f"colors={self.as_list})"
        )


# =============================================================================
# Brand roles -- named plot entities as data
# =============================================================================

# Role -> palette color name. Roles are stored as NAMES rather than hex so
# mode tuning is automatic: ``planet`` is the cyberpunk ``cyan`` in both
# modes and picks up the muted light-mode hex without a second table.
#
# Two roles deliberately resolve to the same color in this first pass
# (``planet`` and ``measured`` are both cyan). Perceptual-distance tuning and
# collision cleanup are a later pass; this is the data plumbing.
ROLE_COLOR_NAMES = {
    "star": "yellow",
    "planet": "cyan",
    "disk": "purple",
    "measured": "cyan",
    "data": "cyan",
    "model": "pink",
    "predicted": "pink",
    "reference": "green",
    "envelope": "purple",
    "alert": "red",
    "highlight": "pink",
    # Inference roles. ``prior`` shares the purple slot with ``envelope`` and
    # ``disk``, which do not appear beside it in the same figure.
    "prior": "purple",
}

# Roles whose color is fixed rather than borrowed from a palette slot, because
# no slot is free of the roles above. They hold in every palette family and
# resolve by background: dark and light use their own hex; paper and barbie
# are white-background modes and use the light value.
#
# - ``positive`` / ``negative``: verdicts (a certified claim, a rejected claim).
#   Blue and orange survive every color vision deficiency in the pair, and
#   neither is ``model`` pink, ``alert`` red, nor ``data`` cyan.
# - ``posterior``: a posterior curve. An earthy tone, distinct from ``model``
#   (posterior draws), ``prior`` and the verdict pair.
# - ``truth``: scenery and true values, a neutral gray with 3:1 contrast on
#   the background so it reads without competing with data.
ROLE_FIXED_COLORS = {
    "positive": {"dark": "#4C8DFF", "light": "#1565C0"},
    "negative": {"dark": "#FF8C1A", "light": "#E65100"},
    "posterior": {"dark": "#B07A4F", "light": "#8E5923"},
    "truth": {"dark": "#9A9A9A", "light": "#757575"},
}

# Every role name, in registry order: palette-backed roles, then fixed ones.
ALL_ROLE_NAMES = [*ROLE_COLOR_NAMES, *ROLE_FIXED_COLORS]

# Canonical cyberpunk order. A family without the named color (spectral,
# biosignature, barbie, tol) uses the slot at this index, so two roles mapped
# to one name keep sharing a color in every family, and no role invents hex.
_ROLE_SLOT_ORDER = ["cyan", "pink", "yellow", "green", "red", "purple"]


class Roles:
    """Mode-aware registry of brand roles.

    Access colors by what the plotted entity is rather than by color name.
    The resolved value depends on the active mode and palette family, which
    is what keeps cause and effect sharing a color from panel to panel.

    Roles:
        star, planet, disk, measured (alias data), model (alias predicted),
        reference, envelope, alert, highlight, prior, and the fixed-color
        roles positive, negative (verdicts), posterior and truth.
    """

    def __init__(self, mode="dark", family=None):
        """Initialize roles for the given mode and palette family.

        Args:
            mode: One of "dark", "light", "paper", or "barbie".
            family: Palette family name, or None for the mode default.
        """
        self._mode = mode
        self._palette = Palette(mode, family=family)

    @property
    def mode(self):
        """Current mode name."""
        return self._mode

    @property
    def family(self):
        """Palette family the roles resolve through."""
        return self._palette.family

    @property
    def names(self):
        """Role names, in registry order."""
        return list(ALL_ROLE_NAMES)

    @property
    def as_dict(self):
        """All roles as a name -> hex dict."""
        return {name: self._resolve(name) for name in ALL_ROLE_NAMES}

    def _resolve(self, role):
        """Resolve one role name to a hex color for the active palette."""
        if role in ROLE_FIXED_COLORS:
            return ROLE_FIXED_COLORS[role]["dark" if self._mode == "dark" else "light"]
        color_name = ROLE_COLOR_NAMES[role]
        colors = self._palette.as_dict
        if color_name in colors:
            return colors[color_name]
        slot = _ROLE_SLOT_ORDER.index(color_name)
        return self._palette[slot % len(self._palette)]

    def __getattr__(self, name):
        """Access a role color by name (e.g. roles.planet)."""
        if name.startswith("_"):
            raise AttributeError(name)
        if name in ALL_ROLE_NAMES:
            return self._resolve(name)
        msg = f"No role '{name}'. Available: {ALL_ROLE_NAMES}"
        raise AttributeError(msg)

    def __getitem__(self, role):
        """Access a role color by name."""
        if role not in ALL_ROLE_NAMES:
            msg = f"No role '{role}'. Available: {ALL_ROLE_NAMES}"
            raise KeyError(msg)
        return self._resolve(role)

    def __contains__(self, role):
        """Whether a name is a known brand role."""
        return role in ALL_ROLE_NAMES

    def __repr__(self):
        """String representation."""
        return f"Roles(mode='{self._mode}', family='{self.family}')"
