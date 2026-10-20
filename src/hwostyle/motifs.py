"""The default motif table: how each recurring object looks, as plain data.

A motif is one object that recurs across figures (the star, a planet, a
detector). Its row says which color it takes, by role name or by neutral rank,
and which non-color channels (marker, line style, hatch, arrow style, font
style) tell it apart when the color is shared, dimmed or lost to color
vision. No drawing code lives here: a plotting library reads the rows and
resolves the color at call time with :func:`motif_color`, so a stored figure
state keeps the key and never a hex value.

Color budget: a figure spends at most :data:`HUE_BUDGET` hues. Hue motifs
beyond that need a second channel from the row. Reuse of a hue is allowed
only for the pairs in :data:`SHARING_SETS`, which never appear in the same
clip, because viewers remember colors across a whole clip. The same list
holds pairs that stay apart because their colors sit too close under color
vision (local zodi with alert and with posterior). Pairs in
:data:`EXCLUSION_PAIRS` name image color roles that share a map family and
likewise never appear together.

Two hues that co-occur and still fall under 10 CAM02-UCS dE (worst of normal
vision and three deficiencies) are listed in :data:`ACCEPTED_PAIRS` with the
non-color channels that must differ between their motifs. A checker accepts
such a pair only when those channels differ.

A label needs more contrast than a mark, so a row can name a role in
``label_color`` whose ink (see :data:`hwostyle.palettes.ROLE_LABEL_INKS`)
colors its text; :func:`motif_label_color` resolves it.
"""

from dataclasses import dataclass

from matplotlib.colors import to_hex, to_rgb

from .palettes import ALL_ROLE_NAMES, Roles
from .styles import MODE_RC

TABLE_VERSION = 3

# At most this many hue motifs in one figure; a fifth or sixth needs a second
# channel and a seventh is never allowed.
HUE_BUDGET = 4

# Opacity of a finished (dimmed) step, by mode. Dimmed hues lose separation
# faster on a white page than on black, so light and paper dim less.
DIM_LEVELS = {"dark": 0.35, "light": 0.5, "paper": 0.5, "barbie": 0.5}

# Neutral grays by rank: the blend fraction from the background (0) to the
# text color (1). A rank spends no hue. ``truth`` is None because it resolves
# to the fixed ``truth`` role, one gray for the whole library. ``text`` is the
# text color itself and ``background`` the axes background.
NEUTRAL_RANKS = {
    "background": 0.0,
    "furniture": 0.2,
    "scenery": 0.45,
    "threshold": 0.6,
    "data_flow": 0.6,
    "hardware": 0.7,
    "integration": 0.8,
    "text": 1.0,
    "truth": None,
}

# Pairs that never appear in the same clip: ones that may take one color for
# that reason, and ones kept apart because their colors fall too close under
# color vision. Names are motif keys or role names. The declaration is per clip, not per
# figure: a pair must not appear in the same frame, nor in two frames of one
# clip, because the color would change meaning between them.
SHARING_SCOPE = "clip"
SHARING_SETS = (
    ("disk", "prior"),
    ("local_zodi", "reference"),
    ("local_zodi", "alert"),
    ("local_zodi", "posterior"),
)

# Image color roles that share a map family and so never share a figure.
EXCLUSION_SCOPE = "figure"
EXCLUSION_PAIRS = (
    ("pupil", "probability"),
    ("pupil", "statistic"),
)


SIGNATURE_FIELDS = ("marker", "linestyle", "hatch", "arrowstyle", "fontstyle")


@dataclass(frozen=True)
class AcceptedPair:
    """Two co-occurring hues left under 10 dE on purpose.

    Attributes:
        a: Role name of the first hue.
        b: Role name of the second hue.
        modes: Modes in which the pair is accepted.
        channels: Fields of :data:`SIGNATURE_FIELDS` that must differ between
            the two motifs for the pair to be accepted.
        de: Measured CAM02-UCS distance, worst of normal vision and
            deuteranomaly, protanomaly and tritanomaly at severity 100.
    """

    a: str
    b: str
    modes: tuple[str, ...]
    channels: tuple[str, ...]
    de: float


# These pairs measure below the usual separation of 10 CAM02-UCS (worst case
# over normal vision and the three anomalies at severity 100; see
# AcceptedPair), so each is accepted only in its listed mode and only when the
# two motifs also differ in every channel of the record. Reference/alert (7.3,
# dark) needs a different line style and marker, for example a dashed
# reference line against the alert X. Reference/negative (6.6) and
# disk/positive (7.7), in paper mode, need a different marker: the negative
# square or the positive circle against a plain line or region. Local zodi with
# negative and prior with positive share those hues and take the same rule.
# Model/negative (9.6, dark) needs a different line style and marker: a solid model line
# against the negative square.
ACCEPTED_PAIRS = (
    AcceptedPair("reference", "alert", ("dark",), ("linestyle", "marker"), 7.3),
    AcceptedPair("model", "negative", ("dark",), ("linestyle", "marker"), 9.6),
    AcceptedPair("reference", "negative", ("paper",), ("marker",), 6.6),
    AcceptedPair("disk", "positive", ("paper",), ("marker",), 7.7),
    AcceptedPair("zodi", "negative", ("paper",), ("marker",), 6.6),
    AcceptedPair("prior", "positive", ("paper",), ("marker",), 7.7),
)


@dataclass(frozen=True)
class MotifRow:
    """One row of the motif table.

    Attributes:
        key: The motif key, for example ``"star"``.
        noun: A plain display name for labels.
        color: A hwostyle role name or a key of :data:`NEUTRAL_RANKS`.
        marker: Matplotlib marker when drawn as a point, else None.
        linestyle: Matplotlib line style of a line or outline.
        hatch: Hatch pattern when drawn as a region.
        arrowstyle: Matplotlib arrow style when drawn as an arrow.
        fontstyle: Font style of the motif's label.
        linewidth: Line width as a multiple of the consumer's base width.
        fill_alpha: Face opacity of a region in light, paper and barbie modes.
        fill_alpha_dark: Face opacity of a region in dark mode, or None to
            use ``fill_alpha``.
        on_image: ``(glyph, ink)`` used over an image, where the hue would
            collide with the map: a marker and a neutral rank. None when the
            motif is not drawn over images.
        label_color: Role whose label ink colors this motif's text, for a hue
            whose mark is too faint to read as words; None to label in the
            mark color.
    """

    key: str
    noun: str
    color: str
    marker: str | None = None
    linestyle: str = "-"
    hatch: str | None = None
    arrowstyle: str | None = None
    fontstyle: str | None = None
    linewidth: float = 1.0
    fill_alpha: float = 0.0
    fill_alpha_dark: float | None = None
    on_image: tuple[str, str] | None = None
    label_color: str | None = None

    def signature(self):
        """The channels other than color that identify this motif.

        Returns:
            ``(marker, linestyle, hatch, arrowstyle, fontstyle)``.
        """
        return (
            self.marker,
            self.linestyle,
            self.hatch,
            self.arrowstyle,
            self.fontstyle,
        )

    def fill(self, mode):
        """Face opacity of a region in ``mode``."""
        if mode == "dark" and self.fill_alpha_dark is not None:
            return self.fill_alpha_dark
        return self.fill_alpha


_ROWS = (
    MotifRow(
        "star",
        "star",
        "star",
        marker="*",
        linestyle="none",
        on_image=("+", "text"),
    ),
    MotifRow(
        "starlight",
        "starlight",
        "star",
        marker=".",
        linestyle="none",
        hatch="..",
    ),
    MotifRow(
        "planet",
        "planet",
        "planet",
        marker="o",
        linestyle="none",
        on_image=("o", "text"),
    ),
    MotifRow(
        "disk",
        "exozodiacal dust",
        "disk",
        hatch="///",
        linewidth=0.8,
        fill_alpha=0.12,
        fill_alpha_dark=0.22,
        label_color="disk",
    ),
    MotifRow(
        "local_zodi",
        "local zodiacal dust",
        "zodi",
        hatch="..",
        linewidth=0.8,
        fill_alpha=0.10,
        fill_alpha_dark=0.18,
        label_color="zodi",
    ),
    MotifRow("aperture", "aperture", "hardware", marker="|", linewidth=3.0),
    MotifRow(
        "optics",
        "instrument optics",
        "hardware",
        marker="d",
        fill_alpha=0.15,
    ),
    MotifRow(
        "detector",
        "detector",
        "hardware",
        marker="s",
        hatch="xx",
        fill_alpha=0.10,
    ),
    MotifRow(
        "pixel",
        "pixel",
        "planet",
        marker="s",
        fill_alpha=0.30,
        on_image=("s", "text"),
    ),
    MotifRow("ray", "light ray", "star", arrowstyle="-|>"),
    MotifRow(
        "integration",
        "integration direction",
        "integration",
        linestyle="--",
        arrowstyle="]->",
    ),
    MotifRow(
        "data_flow",
        "data flow",
        "data_flow",
        arrowstyle="simple",
        linewidth=0.8,
        fill_alpha=0.18,
    ),
    MotifRow(
        "reference_plane",
        "reference plane",
        "scenery",
        linestyle="-.",
        fontstyle="italic",
        linewidth=0.8,
        fill_alpha=0.10,
        fill_alpha_dark=0.25,
    ),
    MotifRow(
        "speckle",
        "speckle",
        "star",
        marker="x",
        linestyle="none",
        on_image=("x", "text"),
    ),
    MotifRow(
        "data",
        "measurement",
        "data",
        marker="|",
        linestyle="none",
        on_image=("|", "text"),
    ),
    MotifRow("model", "model", "model"),
    MotifRow("truth", "true value", "truth", linestyle="--"),
    MotifRow("prior", "prior", "prior", label_color="prior"),
    MotifRow("posterior", "posterior", "posterior", linewidth=1.6),
    MotifRow(
        "threshold",
        "threshold",
        "threshold",
        linestyle=":",
        fontstyle="italic",
    ),
    MotifRow(
        "alert",
        "alert",
        "alert",
        marker="X",
        linestyle="none",
        on_image=("X", "text"),
    ),
    MotifRow("positive", "certified claim", "positive", marker="o", linestyle="none"),
    MotifRow("negative", "rejected claim", "negative", marker="s", linestyle="none"),
    MotifRow(
        "cue",
        "cue",
        "text",
        linewidth=2.0,
        fill_alpha=0.25,
    ),
)

# Motif key -> row, in table order.
MOTIFS = {row.key: row for row in _ROWS}


def _check_mode(mode):
    if mode not in MODE_RC:
        msg = f"Unknown mode '{mode}'; expected one of {sorted(MODE_RC)}"
        raise ValueError(msg)


def neutral_color(rank, mode):
    """Resolve a neutral rank to a hex color in ``mode``.

    Args:
        rank: A key of :data:`NEUTRAL_RANKS`.
        mode: One of "dark", "light", "paper" or "barbie".

    Returns:
        A hex string. ``truth`` resolves to the fixed ``truth`` role.
    """
    _check_mode(mode)
    if rank not in NEUTRAL_RANKS:
        msg = f"No neutral rank '{rank}'. Available: {list(NEUTRAL_RANKS)}"
        raise KeyError(msg)
    level = NEUTRAL_RANKS[rank]
    if level is None:
        return Roles(mode)[rank]
    rc = MODE_RC[mode]
    bg = to_rgb(rc["axes.facecolor"])
    fg = to_rgb(rc["text.color"])
    return to_hex(tuple(b + level * (f - b) for b, f in zip(bg, fg, strict=True)))


def motif_color(key, mode, family=None):
    """Resolve the color of one motif in ``mode``.

    Args:
        key: A key of :data:`MOTIFS`.
        mode: One of "dark", "light", "paper" or "barbie".
        family: Palette family, or None for the mode default.

    Returns:
        A hex string.
    """
    _check_mode(mode)
    if key not in MOTIFS:
        msg = f"No motif '{key}'. Available: {list(MOTIFS)}"
        raise KeyError(msg)
    name = MOTIFS[key].color
    if name in ALL_ROLE_NAMES:
        return Roles(mode, family=family)[name]
    return neutral_color(name, mode)


def motif_label_color(key, mode, family=None):
    """Resolve the text color for a motif's label in ``mode``.

    Args:
        key: A key of :data:`MOTIFS`.
        mode: One of "dark", "light", "paper" or "barbie".
        family: Palette family, or None for the mode default.

    Returns:
        The label ink of the row's ``label_color`` role when it has one in this
        mode and family, else the mark color from :func:`motif_color`.
    """
    mark = motif_color(key, mode, family)
    role = MOTIFS[key].label_color
    if role is None:
        return mark
    return Roles(mode, family=family).label_ink(role)


def accepted_pair(a, b, mode):
    """The accepted-pair record for two role names in ``mode``, or None.

    This matches role names and mode only, ignoring role order. A record is a
    permission, not a verdict: a checker with the two motifs must also confirm
    that they differ in every field of the record's ``channels`` before it
    accepts the pair.

    Returns:
        The matching :class:`AcceptedPair` record, or None if the pair is not
        listed for ``mode``.
    """
    pair = {a, b}
    for rec in ACCEPTED_PAIRS:
        if mode in rec.modes and pair == {rec.a, rec.b}:
            return rec
    return None


def is_hue(key):
    """Whether a motif spends a hue (a color role) rather than a gray.

    ``truth`` is a role but a fixed gray, so it does not count.
    """
    color = MOTIFS[key].color
    return color in ALL_ROLE_NAMES and color != "truth"


def never_together(a, b):
    """Whether two motif keys or role names are declared never to co-occur.

    The check ignores order, so ``never_together("disk", "prior")`` equals
    ``never_together("prior", "disk")``.
    """
    pair = {a, b}
    return any(pair == set(p) for p in (*SHARING_SETS, *EXCLUSION_PAIRS))


__all__ = [
    "ACCEPTED_PAIRS",
    "DIM_LEVELS",
    "EXCLUSION_PAIRS",
    "EXCLUSION_SCOPE",
    "HUE_BUDGET",
    "MOTIFS",
    "NEUTRAL_RANKS",
    "SHARING_SCOPE",
    "SHARING_SETS",
    "SIGNATURE_FIELDS",
    "TABLE_VERSION",
    "AcceptedPair",
    "MotifRow",
    "accepted_pair",
    "is_hue",
    "motif_color",
    "motif_label_color",
    "neutral_color",
    "never_together",
]
