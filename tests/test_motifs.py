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

# Roles that can appear together in one figure: a scene, an inference plot or
# a verdict plot. A pair within a family must stay separable unless the table
# declares it a sharing pair (never drawn together) or accepts it with a
# second channel.
FAMILIES = {
    "scene": ["star", "planet", "disk", "zodi", "model", "alert", "truth"],
    "inference": [
        "planet",
        "model",
        "prior",
        "posterior",
        "reference",
        "alert",
        "truth",
    ],
    "verdict": [
        "positive",
        "negative",
        "planet",
        "disk",
        "reference",
        "alert",
        "truth",
    ],
}
# Role names that stand for a motif key in the never-together list.
ROLE_OF_KEY = {"local_zodi": "zodi"}
# Roles that are plain aliases of another role (one hex in every mode), so the
# pair scan counts only the target.
ALIAS_OF = {"measured": "planet", "data": "planet", "predicted": "model"}
# Close paper pairs of a role that shares a hue with an accepted one (local
# zodi with reference, prior with disk) and has no record of its own yet. The
# scan lists them so that any other undeclared pair fails.
OPEN_PAIRS = {
    "paper": {frozenset(("zodi", "negative")), frozenset(("prior", "positive"))}
}
# Roles no motif row uses: a deprecated band color and an emphasis-text color.
# They sit outside the pair scan.
NOT_IN_TABLE = {"envelope", "highlight"}
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
    assert Roles("light").reference == "#7A9F56"
    assert Roles("light").label_ink("reference") == "#2E7D32"
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


@pytest.mark.parametrize("mode", ("light", "dark", "paper"))
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


def _co_occurring_pairs():
    pairs = set()
    for roles in FAMILIES.values():
        for a, b in itertools.combinations(roles, 2):
            pairs.add(frozenset((a, b)))
    declared = {
        frozenset(ROLE_OF_KEY.get(n, n) for n in p) for p in motifs.SHARING_SETS
    }
    return pairs - declared


@pytest.mark.parametrize("mode", ("light", "dark", "paper"))
def test_every_co_occurring_pair_clears_10_or_is_accepted_with_a_channel(mode):
    """Each pair in a shared figure is 10 dE apart, or accepted with channels."""
    roles = Roles(mode)
    for pair in _co_occurring_pairs():
        a, b = sorted(pair)
        worst = _worst_de(roles[a], roles[b])
        if worst >= 10.0:
            continue
        rec = motifs.accepted_pair(a, b, mode)
        assert rec is not None, f"{mode}: {a}-{b} is {worst:.1f} dE and not accepted"
        assert rec.channels, f"{a}-{b} is accepted without a second channel"
        assert set(rec.channels) <= set(motifs.SIGNATURE_FIELDS)
        assert abs(rec.de - worst) < 0.1, (a, b, rec.de, worst)


def test_accepted_pair_matches_roles_and_modes_with_valid_channels():
    """Records match both role orders only in their listed modes."""
    for rec in motifs.ACCEPTED_PAIRS:
        assert set(rec.channels) <= set(motifs.SIGNATURE_FIELDS)
        for mode in rec.modes:
            assert motifs.accepted_pair(rec.a, rec.b, mode) is rec
            assert motifs.accepted_pair(rec.b, rec.a, mode) is rec
        for mode in set(MODES) - set(rec.modes):
            assert motifs.accepted_pair(rec.a, rec.b, mode) is None
            assert motifs.accepted_pair(rec.b, rec.a, mode) is None


@pytest.mark.parametrize("mode", ("light", "dark", "paper"))
def test_every_role_pair_clears_10_or_is_declared(mode):
    """Every pair of roles, in or out of FAMILIES, is separated or declared.

    Barbie mode is a pink-only novelty palette and is not scanned.
    """
    roles = Roles(mode)
    for alias, target in ALIAS_OF.items():
        assert roles[alias] == roles[target], (mode, alias)
    scanned = [
        n for n in ALL_ROLE_NAMES if n not in ALIAS_OF | dict.fromkeys(NOT_IN_TABLE)
    ]
    keys = {role: key for key, role in ROLE_OF_KEY.items()}
    failures = []
    for a, b in itertools.combinations(scanned, 2):
        if motifs.never_together(a, b) or motifs.never_together(
            keys.get(a, a), keys.get(b, b)
        ):
            continue
        worst = _worst_de(roles[a], roles[b])
        if worst >= 10.0:
            continue
        if frozenset((a, b)) in OPEN_PAIRS.get(mode, ()):
            continue
        rec = motifs.accepted_pair(a, b, mode)
        if rec is None or abs(rec.de - worst) >= 0.1:
            failures.append(f"{a}-{b}: {worst:.1f} dE, record={rec}")
    assert not failures, f"{mode}: " + "; ".join(failures)


def test_accepted_pairs_differ_in_every_required_motif_channel():
    """Rows that take the two hues of a record differ in each of its channels."""
    checked = 0
    for rec in motifs.ACCEPTED_PAIRS:
        rows_a = [r for r in motifs.MOTIFS.values() if r.color == rec.a]
        rows_b = [r for r in motifs.MOTIFS.values() if r.color == rec.b]
        for a, b in itertools.product(rows_a, rows_b):
            checked += 1
            for channel in rec.channels:
                assert getattr(a, channel) != getattr(b, channel), (rec, a.key, b.key)
    assert checked >= 2


def test_dark_model_negative_is_accepted_only_with_both_channels():
    """The dark solid model line stays distinct from the negative square."""
    rec = motifs.accepted_pair("model", "negative", "dark")
    assert rec is not None
    assert rec.channels == ("linestyle", "marker")
    dark = Roles("dark")
    worst = _worst_de(dark.model, dark.negative)
    assert worst < 10.0
    assert abs(rec.de - worst) < 0.1
    for mode in ("light", "paper"):
        assert motifs.accepted_pair("model", "negative", mode) is None


def test_paper_star_clears_every_other_role_and_reads_on_white():
    """Paper star marks clear every other role by 10 dE and white by 3:1."""
    roles = Roles("paper")
    for role in ALL_ROLE_NAMES:
        if role != "star":
            assert _worst_de(roles.star, roles[role]) >= 10.0, role
    assert hwostyle.colors.contrast_ratio(roles.star, "#FFFFFF") >= 3.0


def test_accepted_pairs_are_really_under_10_and_not_cleared_elsewhere():
    """An accepted record names a pair that is under 10 in each of its modes."""
    for rec in motifs.ACCEPTED_PAIRS:
        for mode in rec.modes:
            roles = Roles(mode)
            assert _worst_de(roles[rec.a], roles[rec.b]) < 10.0, (rec, mode)
    assert motifs.accepted_pair("alert", "reference", "dark") is not None
    assert motifs.accepted_pair("alert", "reference", "light") is None


def test_local_zodi_is_never_with_alert_or_posterior():
    """The dust motif is declared apart from alert and posterior, per clip."""
    assert motifs.SHARING_SCOPE == "clip"
    for other in ("alert", "posterior"):
        assert motifs.never_together("local_zodi", other)
        assert motifs.never_together(other, "local_zodi")


def test_tuned_hexes_by_mode():
    """The chosen per-mode hexes hold."""
    dark, light, paper = Roles("dark"), Roles("light"), Roles("paper")
    assert dark.disk == dark.prior == "#9251BD"
    assert dark.posterior == "#B38A61"
    assert light.model == light.predicted == "#882255"
    assert light.posterior == paper.posterior == "#662506"
    assert light.disk == light.prior == "#6A1B9A"
    assert light.alert == "#B71C1C"
    assert light.reference == light.zodi == "#7A9F56"
    assert paper.alert == "#C32D22"
    assert paper.star == "#92924F"
    assert Roles("paper", family="tol-light").star != "#92924F"
    assert light.star == "#F9A825"
    assert dark.star == "#F5D300"
    assert Roles("paper", family="tol-light").alert != "#C32D22"
    assert Roles("dark", family="spectral").disk != "#9251BD"


@pytest.mark.parametrize(
    ("key", "mode", "ink"),
    [
        ("local_zodi", "dark", "#15903E"),
        ("disk", "dark", "#9E63C4"),
        ("prior", "dark", "#9E63C4"),
        ("local_zodi", "light", "#2E7D32"),
    ],
)
def test_label_ink_reads_four_and_a_half_to_one_on_the_page(key, mode, ink):
    """A label ink differs from its mark and reaches 4.5:1 on the page."""
    page = "#000000" if mode == "dark" else "#FFFFFF"
    got = motifs.motif_label_color(key, mode)
    assert got == ink
    assert got != motifs.motif_color(key, mode)
    assert hwostyle.colors.contrast_ratio(got, page) >= 4.5


def test_label_color_falls_back_to_the_mark():
    """Rows without an ink, and modes or families without one, label in the mark."""
    assert motifs.motif_label_color("star", "dark") == motifs.motif_color(
        "star", "dark"
    )
    assert motifs.motif_label_color("local_zodi", "paper") == motifs.motif_color(
        "local_zodi", "paper"
    )
    assert motifs.motif_label_color(
        "disk", "dark", family="spectral"
    ) == motifs.motif_color("disk", "dark", family="spectral")
