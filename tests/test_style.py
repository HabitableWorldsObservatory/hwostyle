"""Tests for hwostyle palette and mode switching."""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pytest
import tol_colors as tc
from matplotlib.colors import to_hex

import hwostyle
from hwostyle.colors import (
    contrast_ratio,
    min_perceptual_distance,
    perceptual_distance,
    unsafe_pairs,
)
from hwostyle.palettes import (
    BARBIE,
    BIOSIGNATURE,
    CYBERPUNK_DARK,
    CYBERPUNK_LIGHT,
    ROLE_FIXED_COLORS,
    SPECTRAL,
    Palette,
)


class TestPalette:
    """Tests for the Palette class."""

    def test_dark_cyberpunk_colors(self):
        """Dark cyberpunk palette returns neon hex values."""
        p = Palette("dark")
        assert p.cyan == CYBERPUNK_DARK["cyan"]
        assert p.pink == CYBERPUNK_DARK["pink"]
        assert p.yellow == CYBERPUNK_DARK["yellow"]

    def test_light_cyberpunk_colors(self):
        """Light cyberpunk palette returns muted hex values."""
        p = Palette("light")
        assert p.cyan == CYBERPUNK_LIGHT["cyan"]
        assert p.pink == CYBERPUNK_LIGHT["pink"]

    def test_spectral_palette(self):
        """Spectral palette has emission line color names."""
        p = Palette("dark", family="spectral")
        assert p.oiii == SPECTRAL["oiii"]
        assert p.h_alpha == SPECTRAL["h_alpha"]
        assert len(p) == 6

    def test_biosignature_palette(self):
        """Biosignature palette has molecule color names."""
        p = Palette("light", family="biosignature")
        assert p.o2 == BIOSIGNATURE["o2"]
        assert p.h2o == BIOSIGNATURE["h2o"]
        assert p.ch4 == BIOSIGNATURE["ch4"]
        assert len(p) == 6

    def test_barbie_palette(self):
        """Barbie palette returns RdPu-sampled hex values."""
        p = Palette("barbie")
        assert len(p) == 5
        assert p[0] == BARBIE["blush"]
        assert p[2] == BARBIE["magenta"]

    def test_palette_length(self):
        """Palette has exactly 6 colors for cyberpunk."""
        p = Palette("dark")
        assert len(p) == 6

    def test_palette_indexing(self):
        """Palette supports integer indexing."""
        p = Palette("dark")
        assert p[0] == p.cyan

    def test_palette_string_indexing(self):
        """Palette supports string indexing."""
        p = Palette("dark", family="biosignature")
        assert p["o2"] == BIOSIGNATURE["o2"]

    def test_palette_iteration(self):
        """Palette is iterable."""
        p = Palette("dark")
        colors = list(p)
        assert len(colors) == 6

    def test_cycler_length(self):
        """Cycler contains the right number of colors."""
        p = Palette("dark")
        assert len(p.cycler) == 6

    def test_palette_names(self):
        """Palette exposes color names."""
        p = Palette("dark", family="spectral")
        assert "oiii" in p.names
        assert "h_alpha" in p.names

    def test_invalid_family_raises(self):
        """Invalid family name raises ValueError."""
        try:
            Palette("dark", family="rainbow")
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_invalid_attr_raises(self):
        """Accessing a nonexistent color by name raises AttributeError."""
        p = Palette("dark")
        try:
            _ = p.nonexistent_color
            raise AssertionError("Should have raised AttributeError")
        except AttributeError:
            pass

    def test_as_dict(self):
        """as_dict returns a name->hex mapping."""
        p = Palette("dark", family="biosignature")
        d = p.as_dict
        assert d["o2"] == BIOSIGNATURE["o2"]
        assert len(d) == 6


class TestColormaps:
    """Tests for the semantic colormap registry."""

    def test_readouts_is_magma(self):
        """The readouts category is magma in every mode."""
        for mode in ("dark", "light", "paper", "barbie"):
            hwostyle.use(mode)
            assert hwostyle.cmaps.readouts == "magma"

    def test_intensity_low_is_dark(self):
        """Paper intensity is oriented low = dark (a dark hole reads dark)."""
        hwostyle.use("paper")
        cmap = plt.get_cmap(hwostyle.cmaps.intensity)
        assert sum(cmap(0.0)[:3]) < sum(cmap(1.0)[:3])

    def test_intensity_resolves(self):
        """Intensity resolves to a usable colormap in every mode."""
        for mode in ("dark", "light", "paper", "barbie"):
            hwostyle.use(mode)
            assert plt.get_cmap(hwostyle.cmaps.intensity) is not None


class TestModes:
    """Tests for mode switching."""

    def test_use_dark(self):
        """use('dark') sets dark rcParams."""
        hwostyle.use("dark")
        assert plt.rcParams["figure.facecolor"] == "black"
        assert plt.rcParams["text.color"] == "white"

    def test_use_light(self):
        """use('light') sets light rcParams."""
        hwostyle.use("light")
        assert plt.rcParams["figure.facecolor"] == "white"
        assert plt.rcParams["text.color"] == "black"

    def test_use_barbie(self):
        """use('barbie') sets barbie rcParams."""
        hwostyle.use("barbie")
        assert plt.rcParams["figure.facecolor"] == "white"
        assert plt.rcParams["font.family"] == ["serif"]
        assert plt.rcParams["image.cmap"] == "RdPu"

    def test_use_with_palette_family(self):
        """use() accepts a palette_family argument."""
        hwostyle.use("light", palette_family="spectral")
        assert hwostyle.palette.family == "spectral"
        assert hwostyle.palette.oiii == SPECTRAL["oiii"]

    def test_use_biosignature(self):
        """use() with biosignature palette sets correct colors."""
        hwostyle.use("dark", palette_family="biosignature")
        assert hwostyle.palette.family == "biosignature"
        assert hwostyle.palette.o2 == BIOSIGNATURE["o2"]
        assert len(hwostyle.palette) == 6

    def test_context_manager_restores(self):
        """Context manager restores previous mode."""
        hwostyle.use("dark")
        with hwostyle.light():
            assert plt.rcParams["figure.facecolor"] == "white"
        assert plt.rcParams["figure.facecolor"] == "black"

    def test_context_manager_restores_family(self):
        """Context manager restores previous palette family."""
        hwostyle.use("light", palette_family="spectral")
        with hwostyle.dark(palette_family="biosignature"):
            assert hwostyle.palette.family == "biosignature"
        assert hwostyle.palette.family == "spectral"

    def test_barbie_context_manager(self):
        """Barbie context manager restores previous mode."""
        hwostyle.use("dark")
        with hwostyle.barbie():
            assert plt.rcParams["font.family"] == ["serif"]
            assert len(hwostyle.palette) == 5
        assert plt.rcParams["figure.facecolor"] == "black"
        assert len(hwostyle.palette) == 6

    def test_invalid_mode_raises(self):
        """Invalid mode raises ValueError."""
        try:
            hwostyle.use("neon")
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

    def test_palette_updates_on_mode_switch(self):
        """Global palette object updates when mode switches."""
        hwostyle.use("dark")
        assert hwostyle.palette.cyan == CYBERPUNK_DARK["cyan"]
        hwostyle.use("light")
        assert hwostyle.palette.cyan == CYBERPUNK_LIGHT["cyan"]


class TestOpdColormap:
    """Tests for the opd semantic colormap key."""

    def test_opd_resolves_in_every_mode(self):
        """The opd key resolves to a usable colormap in every mode."""
        for mode in ("dark", "light", "paper", "barbie"):
            hwostyle.use(mode)
            assert plt.get_cmap(hwostyle.cmaps.opd) is not None

    def test_opd_is_centered_on_a_light_neutral(self):
        """Zero OPD reads as a light neutral, not as an extreme."""
        for mode in ("dark", "light", "paper", "barbie"):
            hwostyle.use(mode)
            cmap = plt.get_cmap(hwostyle.cmaps.opd)
            mid = sum(cmap(0.5)[:3])
            assert mid > sum(cmap(0.0)[:3])
            assert mid > sum(cmap(1.0)[:3])

    def test_opd_is_a_distinct_key_from_phase(self):
        """The opd key is its own semantic key: phase stays the cyclic map."""
        hwostyle.use("dark")
        assert hwostyle.cmaps.opd != hwostyle.cmaps.phase


class TestRoles:
    """Tests for the brand role registry."""

    def test_roles_resolve_through_palette_names(self):
        """A role resolves to the palette color its name points at."""
        hwostyle.use("dark")
        assert hwostyle.roles.planet == CYBERPUNK_DARK["cyan"]
        assert hwostyle.roles.star == CYBERPUNK_DARK["yellow"]
        assert hwostyle.roles.alert == CYBERPUNK_DARK["red"]

    def test_mode_tuning_is_automatic(self):
        """The same role picks up the light-mode hex without a second table."""
        hwostyle.use("dark")
        assert hwostyle.roles.planet == CYBERPUNK_DARK["cyan"]
        hwostyle.use("light")
        assert hwostyle.roles.planet == CYBERPUNK_LIGHT["cyan"]

    def test_roles_update_on_mode_switch(self):
        """The global roles object tracks the active mode."""
        hwostyle.use("dark")
        assert hwostyle.roles.mode == "dark"
        hwostyle.use("light")
        assert hwostyle.roles.mode == "light"

    def test_aliases_share_a_color(self):
        """The data role aliases measured, and predicted aliases model."""
        hwostyle.use("dark")
        assert hwostyle.roles.data == hwostyle.roles.measured
        assert hwostyle.roles.predicted == hwostyle.roles.model

    def test_shared_name_shares_a_color_in_every_family(self):
        """Roles mapped to one palette name stay one color, families included."""
        for family in ("cyberpunk", "spectral", "biosignature"):
            hwostyle.use("dark", palette_family=family)
            assert hwostyle.roles.planet == hwostyle.roles.measured

    def test_non_cyberpunk_families_resolve_without_new_hex(self):
        """A family lacking cyberpunk names falls back to palette slots."""
        for family in ("spectral", "biosignature"):
            hwostyle.use("dark", palette_family=family)
            colors = set(hwostyle.palette.as_list)
            for name in hwostyle.roles.names:
                if name in ROLE_FIXED_COLORS:
                    continue
                assert hwostyle.roles[name] in colors

    def test_barbie_mode_resolves_every_role(self):
        """Barbie mode has five colors and still resolves all roles."""
        hwostyle.use("barbie")
        colors = set(hwostyle.palette.as_list)
        for name in hwostyle.roles.names:
            if name in ROLE_FIXED_COLORS:
                continue
            assert hwostyle.roles[name] in colors

    def test_as_dict_covers_every_role(self):
        """as_dict returns one entry per registered role."""
        hwostyle.use("dark")
        d = hwostyle.roles.as_dict
        assert set(d) == set(hwostyle.roles.names)
        assert all(v.startswith("#") for v in d.values())

    def test_unknown_role_raises_with_the_vocabulary(self):
        """An unknown role names the available roles."""
        hwostyle.use("dark")
        try:
            _ = hwostyle.roles.spaceship
            raise AssertionError("Should have raised AttributeError")
        except AttributeError as err:
            assert "planet" in str(err)

    def test_contains_reports_membership(self):
        """The registry answers membership questions."""
        hwostyle.use("dark")
        assert "planet" in hwostyle.roles
        assert "spaceship" not in hwostyle.roles


NEW_ROLES = ("positive", "negative", "statistic", "truth", "prior", "posterior")
FIXED_ROLES = ("positive", "negative", "truth", "posterior")
EXISTING_ROLES = (
    "star",
    "planet",
    "disk",
    "measured",
    "model",
    "reference",
    "envelope",
    "alert",
    "highlight",
)
BACKGROUND = {"dark": "#000000", "light": "#ffffff"}


class TestInferenceRoles:
    """Verdict, scenery, prior and posterior roles."""

    def test_every_new_role_is_defined(self):
        """Each new name resolves in both themes (statistic is a colormap)."""
        for mode in ("dark", "light"):
            hwostyle.use(mode)
            for name in NEW_ROLES:
                if name == "statistic":
                    assert plt.get_cmap(hwostyle.cmaps.statistic) is not None
                else:
                    assert hwostyle.roles[name].startswith("#")

    def test_statistic_is_reversed_nightfall_in_every_mode(self):
        """The statistic colormap is Tol nightfall_r and differs from residual."""
        for mode in ("dark", "light", "paper", "barbie"):
            hwostyle.use(mode)
            assert hwostyle.cmaps.statistic.name == "nightfall_r"
            assert hwostyle.cmaps.statistic != hwostyle.cmaps.residual

    def test_prior_follows_the_purple_slot(self):
        """Prior is the palette purple in each theme."""
        hwostyle.use("dark")
        assert hwostyle.roles.prior == CYBERPUNK_DARK["purple"]
        hwostyle.use("light")
        assert hwostyle.roles.prior == CYBERPUNK_LIGHT["purple"]

    def test_fixed_roles_hold_in_every_family_and_mode(self):
        """Fixed-color roles ignore the palette family."""
        for mode in ("dark", "light"):
            hwostyle.use(mode)
            want = {n: hwostyle.roles[n] for n in FIXED_ROLES}
            for family in ("spectral", "biosignature"):
                hwostyle.use(mode, palette_family=family)
                assert {n: hwostyle.roles[n] for n in FIXED_ROLES} == want
        hwostyle.use("barbie")
        assert hwostyle.roles.positive == ROLE_FIXED_COLORS["positive"]["light"]

    def test_new_hues_do_not_collide_with_existing_roles(self):
        """Posterior is not model, verdicts are not alert, nothing sits on a role."""
        for mode in ("dark", "light"):
            hwostyle.use(mode)
            r = hwostyle.roles
            assert r.posterior != r.model
            assert r.positive != r.alert
            assert r.negative != r.alert
            assert r.positive != r.model
            assert r.negative != r.model
            for new in FIXED_ROLES:
                for old in EXISTING_ROLES:
                    d = perceptual_distance(r[new], r[old])
                    assert d >= 20.0, (mode, new, old, d)

    def test_new_roles_are_distinct_from_each_other(self):
        """The fixed roles and prior separate, and verdicts survive CVD."""
        for mode in ("dark", "light"):
            hwostyle.use(mode)
            names = [*FIXED_ROLES, "prior"]
            hexes = [hwostyle.roles[n] for n in names]
            assert min_perceptual_distance(hexes)[0] >= 20.0
            pair = [hwostyle.roles.positive, hwostyle.roles.negative]
            assert (
                unsafe_pairs(pair, ["positive", "negative"], contrast_floor=1.0) == []
            )

    def test_new_roles_read_against_the_background(self):
        """Every new color keeps WCAG graphical contrast with its background."""
        for mode, bg in BACKGROUND.items():
            hwostyle.use(mode)
            for name in (*FIXED_ROLES, "prior"):
                assert contrast_ratio(hwostyle.roles[name], bg) >= 3.0, (mode, name)

    def test_truth_is_a_neutral_gray(self):
        """Truth carries no hue, so it cannot be mistaken for a data role."""
        for mode in ("dark", "light"):
            hwostyle.use(mode)
            r, g, b = (int(hwostyle.roles.truth[i : i + 2], 16) for i in (1, 3, 5))
            assert r == g == b


IMAGE_ROLES = (
    "intensity",
    "readouts",
    "probability",
    "pupil",
    "mask",
    "opd",
    "residual",
    "statistic",
    "phase",
)
SEQUENTIAL_ROLES = ("intensity", "probability", "pupil")
PAGE_RGB = {"light": 1.0, "paper": 1.0, "dark": 0.0}


def _luminance(rgb):
    """Relative luminance of an sRGB triple."""
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb[:3]]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _samples(role, n=17):
    """Sample the active colormap for a role at n points, rounded for comparison."""
    cmap = plt.get_cmap(getattr(hwostyle.cmaps, role))
    return tuple(
        tuple(round(float(c), 3) for c in cmap(x)) for x in np.linspace(0, 1, n)
    )


class TestDistinctiveRoles:
    """The image-role table: Tol maps, page-decided orientation, no shared maps."""

    def test_every_role_resolves_in_every_mode(self):
        """Each image role resolves to a usable colormap in all four modes."""
        for mode in ("light", "dark", "paper", "barbie"):
            hwostyle.use(mode)
            for role in IMAGE_ROLES:
                assert plt.get_cmap(getattr(hwostyle.cmaps, role)) is not None

    def test_sequential_low_end_sits_at_the_page_end(self):
        """Low values are the end of the map nearest the page color."""
        for mode, page in PAGE_RGB.items():
            hwostyle.use(mode)
            page_lum = _luminance((page, page, page))
            for role in SEQUENTIAL_ROLES:
                cmap = plt.get_cmap(getattr(hwostyle.cmaps, role))
                low = abs(_luminance(cmap(0.0)) - page_lum)
                high = abs(_luminance(cmap(1.0)) - page_lum)
                if role == "intensity":
                    # Intensity is low = dark on every page (a dark hole reads dark).
                    assert _luminance(cmap(0.0)) < _luminance(cmap(1.0))
                else:
                    assert low < high, (mode, role)

    def test_dark_floor_of_sequential_maps_is_dark(self):
        """On black the low end of each sequential map is a dark color."""
        hwostyle.use("dark")
        for role in SEQUENTIAL_ROLES:
            cmap = plt.get_cmap(getattr(hwostyle.cmaps, role))
            assert _luminance(cmap(0.0)) < 0.05, role

    def test_no_two_image_roles_share_a_map(self):
        """The nine image roles resolve to nine different maps in light, dark, paper."""
        for mode in ("light", "dark", "paper"):
            hwostyle.use(mode)
            seen = {}
            for role in IMAGE_ROLES:
                key = _samples(role)
                assert key not in seen, (mode, role, seen.get(key))
                seen[key] = role

    def test_modes_share_the_same_maps_up_to_orientation(self):
        """Light and paper read one definition, so they are identical."""
        hwostyle.use("light")
        light = {role: _samples(role) for role in IMAGE_ROLES}
        hwostyle.use("paper")
        assert light == {role: _samples(role) for role in IMAGE_ROLES}

    def test_mask_is_two_grays(self):
        """Mask is a two-level gray pair per page, with no hue."""
        for mode, expected in (
            ("light", ("#cccccc", "#8c8c8c")),
            ("paper", ("#cccccc", "#8c8c8c")),
            ("dark", ("#333333", "#737373")),
        ):
            hwostyle.use(mode)
            cmap = plt.get_cmap(hwostyle.cmaps.mask)
            assert cmap.N == 2
            assert (to_hex(cmap(0.0)), to_hex(cmap(1.0))) == expected

    def test_diverging_maps_center_on_a_light_neutral(self):
        """Each diverging center is light and near neutral."""
        for mode in ("light", "dark", "paper"):
            hwostyle.use(mode)
            for role in ("opd", "residual", "statistic"):
                cmap = plt.get_cmap(getattr(hwostyle.cmaps, role))
                mid = cmap(0.5)[:3]
                assert _luminance(mid) > 0.8, (mode, role)
                assert max(mid) - min(mid) < 0.1, (mode, role)

    def test_tol_roles_use_tol_colors(self):
        """The Tol image roles are the tol_colors maps, not copies."""
        hwostyle.use("light")
        cm = hwostyle.cmaps
        assert cm.residual is tc.BuRd
        assert cm.probability is tc.YlOrBr
        assert cm.pupil is tc.WhOrBr
        assert _samples("opd") == tuple(
            tuple(round(float(c), 3) for c in tc.PRGn.reversed()(x))
            for x in np.linspace(0, 1, 17)
        )

    def test_brand_intensity_is_its_own_map(self):
        """brand_intensity stays the brand ramp, distinct from probability."""
        hwostyle.use("light")
        assert _samples("brand_intensity") != _samples("probability")


class TestDeprecatedRoles:
    """high_dynamic_range and the fixed envelope role warn but still resolve."""

    def test_high_dynamic_range_warns_and_names_the_replacement(self):
        """Reading the colormap warns and points at intensity and readouts."""
        hwostyle.use("dark")
        with pytest.warns(DeprecationWarning, match="intensity.*readouts"):
            value = hwostyle.cmaps.high_dynamic_range
        assert value == "inferno"

    def test_envelope_warns_by_attribute_and_by_key(self):
        """Both access paths warn and name the parent series color."""
        hwostyle.use("dark")
        with pytest.warns(DeprecationWarning, match="parent series color"):
            attr = hwostyle.roles.envelope
        with pytest.warns(DeprecationWarning, match="parent series color"):
            item = hwostyle.roles["envelope"]
        assert attr == item == hwostyle.palette.purple

    def test_as_dict_does_not_warn(self):
        """Listing every role is not a use of the deprecated one."""
        hwostyle.use("dark")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            hwostyle.roles.as_dict  # noqa: B018


def test_paper_roles_use_tol_muted_and_never_repeat():
    """Paper curve roles are six distinct Tol muted colors that read on white."""
    import tol_colors as tc

    from hwostyle.colors import contrast_ratio
    from hwostyle.palettes import Roles

    roles = Roles("paper")
    six = [roles[r] for r in ("planet", "model", "star", "reference", "alert", "disk")]
    assert len({c.lower() for c in six}) == 6
    assert {c.lower() for c in six} <= {c.lower() for c in tc.muted}
    for c in six:
        assert contrast_ratio(c, "#FFFFFF") >= 2.9


def test_tol_light_stays_available_by_name():
    """The earlier Tol light set stays reachable as the tol-light family."""
    from hwostyle.palettes import Palette

    assert Palette("paper", "tol-light")["light_blue"]
