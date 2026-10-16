"""The default motif table: every row resolves, and shared colors stay separable."""

import itertools
from collections import defaultdict

import pytest
from colorspacious import cspace_convert
from matplotlib.colors import to_hex

import hwostyle
from hwostyle import motifs
from hwostyle.palettes import ALL_ROLE_NAMES, Palette, Roles

MODES = ("light", "dark", "paper", "barbie")
CVD = ("deuteranomaly", "protanomaly", "tritanomaly")
EXPECTED_KEYS = (
    "star starlight planet disk local_zodi aperture optics detector pixel ray "
    "integration data_flow reference_plane speckle data model truth prior "
    "posterior threshold alert positive negative cue"
).split()


def _srgb(hex_color):
    h = hex_color.lstrip("#")
    return [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def _de(a, b, cvd=None):
    """CAM02-UCS distance, optionally after simulating a deficiency at full severity."""
    out = []
    for hex_color in (a, b):
        rgb = _srgb(hex_color)
        if cvd is not None:
            rgb = cspace_convert(
                rgb,
                {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100},
                "sRGB1",
            ).clip(0, 1)
        out.append(cspace_convert(rgb, "sRGB1", "CAM02-UCS"))
    return float(((out[0] - out[1]) ** 2).sum() ** 0.5)


def _worst_de(a, b):
    return min(_de(a, b), *(_de(a, b, c) for c in CVD))


def test_the_table_has_the_agreed_keys():
    """The table holds exactly the agreed motif keys, in order."""
    assert list(motifs.MOTIFS) == EXPECTED_KEYS


@pytest.mark.parametrize("mode", MODES)
def test_every_motif_resolves_in_every_mode(mode):
    """Every motif resolves to a hex color in every mode."""
    for key in motifs.MOTIFS:
        color = motifs.motif_color(key, mode)
        assert len(color) == 7
        assert color.startswith("#")


@pytest.mark.parametrize("mode", MODES)
def test_motifs_that_share_a_color_differ_in_a_non_color_channel(mode):
    """Motifs sharing one color differ in marker, line style, hatch, arrow or font."""
    by_color = defaultdict(list)
    for key in motifs.MOTIFS:
        by_color[motifs.motif_color(key, mode).lower()].append(key)
    for color, keys in by_color.items():
        sigs = [motifs.MOTIFS[k].signature() for k in keys]
        assert len(set(sigs)) == len(sigs), f"{keys} share {color} and a signature"


def test_sharing_and_exclusion_pairs_are_declared_and_symmetric():
    """The never-together pairs are declared and match in either order."""
    assert ("disk", "prior") in motifs.SHARING_SETS
    assert ("local_zodi", "reference") in motifs.SHARING_SETS
    assert ("pupil", "probability") in motifs.EXCLUSION_PAIRS
    assert ("pupil", "statistic") in motifs.EXCLUSION_PAIRS
    for a, b in (*motifs.SHARING_SETS, *motifs.EXCLUSION_PAIRS):
        assert motifs.never_together(a, b)
        assert motifs.never_together(b, a)
    assert not motifs.never_together("star", "planet")


def test_the_sharing_pairs_really_share_a_color():
    """Disk and prior share a hue, and local zodi takes the reference green."""
    for mode in ("light", "dark", "paper"):
        assert motifs.motif_color("disk", mode) == motifs.motif_color("prior", mode)
        roles = Roles(mode)
        assert motifs.motif_color("local_zodi", mode) == roles.reference
        assert roles.zodi == roles.reference


def test_dark_reference_green_is_the_deeper_green_and_other_modes_keep_theirs():
    """Only the cyberpunk dark green is replaced."""
    assert Roles("dark").reference == "#117733"
    assert Roles("dark").zodi == "#117733"
    assert Roles("light").reference == "#2E7D32"
    assert (
        Roles("dark", family="spectral").reference
        in Palette("dark", "spectral").as_list
    )
    assert "zodi" in ALL_ROLE_NAMES


def test_star_against_reference_in_dark_mode_clears_20_under_deuteranopia():
    """Star against reference in dark mode stays above 20 dE under deuteranopia."""
    hwostyle.use("dark")
    star, ref = Roles("dark").star, Roles("dark").reference
    value = _de(star, ref, "deuteranomaly")
    print(f"dark star vs reference, deuteranomaly severity 100: {value:.1f} dE")
    assert value > 20.0
    assert _worst_de(star, ref) > 20.0


@pytest.mark.parametrize("mode", MODES)
def test_the_cue_is_the_text_color(mode):
    """The cue spends no hue: it takes the mode's text color."""
    text = hwostyle.styles.MODE_RC[mode]["text.color"]
    cue = motifs.motif_color("cue", mode)
    assert cue.lower() == to_hex(text).lower()
    assert not motifs.is_hue("cue")


def test_neutral_ranks_keep_their_levels():
    """Neutral ranks keep their blend levels."""
    ranks = motifs.NEUTRAL_RANKS
    assert ranks["furniture"] == 0.2
    assert ranks["scenery"] == 0.45
    assert ranks["hardware"] == 0.7
    assert ranks["integration"] == 0.8
    assert ranks["data_flow"] == 0.6
    assert ranks["threshold"] == 0.6
    assert ranks["truth"] is None
    assert motifs.neutral_color("truth", "dark") == Roles("dark").truth


def test_neutrals_spend_no_hue():
    """Every gray motif has equal channels in every mode."""
    for key in motifs.MOTIFS:
        if motifs.is_hue(key):
            continue
        for mode in MODES:
            r, g, b = _srgb(motifs.motif_color(key, mode))
            assert max(r, g, b) - min(r, g, b) < 0.01, (key, mode)


def test_dim_levels_follow_the_mode():
    """Dark mode dims to 0.35 and the white-page modes to 0.5."""
    assert motifs.DIM_LEVELS["dark"] == 0.35
    assert motifs.DIM_LEVELS["light"] == motifs.DIM_LEVELS["paper"] == 0.5


def test_unknown_names_raise():
    """Unknown motif keys, modes and ranks raise with the valid options."""
    with pytest.raises(KeyError, match="No motif"):
        motifs.motif_color("nebula", "dark")
    with pytest.raises(ValueError, match="Unknown mode"):
        motifs.motif_color("star", "sepia")
    with pytest.raises(KeyError, match="No neutral rank"):
        motifs.neutral_color("loud", "dark")


@pytest.mark.parametrize(
    "mode",
    (
        pytest.param(
            "light",
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "palette tuning pending Corey: light reference against model "
                    "measures 7.5 dE under deuteranomaly, under the 10 that counts "
                    "as indistinguishable"
                ),
            ),
        ),
        "dark",
        "paper",
    ),
)
def test_the_first_four_hue_motifs_stay_apart_in_every_vision_type(mode, capsys):
    """The four-hue budget stays separable in every mode and vision type."""
    roles = Roles(mode)
    four = [roles.planet, roles.model, roles.star, roles.reference]
    worst = min(_worst_de(a, b) for a, b in itertools.combinations(four, 2))
    print(f"{mode}: first four hues, worst pair {worst:.1f} dE")
    assert worst > 10.0


def test_each_pair_list_carries_its_scope():
    """A sharing pair is never in one clip; an exclusion, never in one figure."""
    assert motifs.SHARING_SCOPE == "clip"
    assert motifs.EXCLUSION_SCOPE == "figure"


def test_the_dark_reference_plane_fill_is_visible_on_black():
    """A region at 0.10 over black is invisible, so dark mode fills it harder."""
    row = motifs.MOTIFS["reference_plane"]
    assert row.fill("dark") >= 0.25
    assert row.fill("light") == 0.10
