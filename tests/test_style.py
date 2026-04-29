# pylint: disable=duplicate-code
from netbubbles.style import (
    EdgeTier,
    Style,
    default_style,
)


class TestDefaultStyle:
    def test_exists(self):
        assert default_style is not None

    def test_curve_strength_positive(self):
        assert default_style.curve_strength > 0

    def test_has_tiers(self):
        assert len(default_style.edge_tiers) > 0


class TestStyleEdgeMethods:
    def test_edge_color_returns_str(self):
        s = Style()
        assert isinstance(s.edge_color(0.0), str)
        assert isinstance(s.edge_color(1.0), str)

    def test_edge_linewidth_returns_float(self):
        s = Style()
        assert isinstance(s.edge_linewidth(0.0), float)
        assert isinstance(s.edge_linewidth(1.0), float)

    def test_edge_alpha_returns_float(self):
        s = Style()
        assert isinstance(s.edge_alpha(0.0), float)
        assert isinstance(s.edge_alpha(1.0), float)

    def test_linewidth_heavy_gt_light(self):
        s = Style()
        assert s.edge_linewidth(1.0) > s.edge_linewidth(0.0)


class TestCustomTiers:
    def _two_tier(self) -> Style:
        return Style(edge_tiers=[EdgeTier("red", 3.0, 0.9), EdgeTier("blue", 1.0, 0.5)])

    def test_low_frac_gives_light_tier(self):
        assert self._two_tier().edge_color(0.0) == "blue"

    def test_high_frac_gives_heavy_tier(self):
        assert self._two_tier().edge_color(1.0) == "red"

    def test_single_tier_always_same(self):
        s = Style(edge_tiers=[EdgeTier("green", 2.0, 0.7)])
        assert s.edge_color(0.0) == "green"
        assert s.edge_color(1.0) == "green"
