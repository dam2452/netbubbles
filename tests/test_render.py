import matplotlib.pyplot as plt
import pytest

from netbubbles.graph import BubbleGraph
from netbubbles.render import (
    add_legend,
    draw,
)
from netbubbles.render.legend import (
    _balance_ncol,
    _resolve_ncol,
)
from netbubbles.style import Style


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


class TestDraw:
    def test_returns_axes(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        assert isinstance(draw(g), plt.Axes)

    def test_returns_provided_axes(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        _, ax_in = plt.subplots()
        assert draw(g, ax=ax_in) is ax_in

    def test_with_custom_pos(self):
        g = BubbleGraph()
        g.add_node("A")
        g.add_node("B")
        ax = draw(g, pos={"A": (0.0, 0.0), "B": (1.0, 0.0)})
        assert isinstance(ax, plt.Axes)

    def test_with_title(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        assert isinstance(draw(g, title="My Graph"), plt.Axes)

    def test_with_subtitle(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        assert isinstance(draw(g, title="T", subtitle="S"), plt.Axes)

    def test_no_edges(self):
        g = BubbleGraph()
        g.add_nodes(["A", "B", "C"])
        assert isinstance(draw(g), plt.Axes)

    def test_self_loop(self):
        g = BubbleGraph()
        g.add_node("A")
        g.add_edge("A", "A", weight=2)
        assert isinstance(draw(g, pos={"A": (0.0, 0.0)}), plt.Axes)

    def test_background_false(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        assert isinstance(draw(g, background=False), plt.Axes)

    def test_positions_stored_on_graph(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        pos = {"A": (0.0, 1.0), "B": (1.0, 0.0)}
        draw(g, pos=pos)
        assert g.positions == pos

    def test_custom_style(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1})
        assert isinstance(draw(g, style=Style(curve_strength=0.3)), plt.Axes)

    def test_bidirectional_edges(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 3, ("B", "A"): 2})
        assert isinstance(draw(g), plt.Axes)

    def test_many_nodes(self):
        edges = {(chr(65 + i), chr(65 + (i + 1) % 6)): float(i + 1) for i in range(6)}
        g = BubbleGraph.from_weighted_edges(edges)
        assert isinstance(draw(g), plt.Axes)


class TestAddLegend:
    def test_basic(self):
        fig, _ = plt.subplots()
        add_legend(fig, ["A", "B"], {"A": "red", "B": "blue"})

    def test_empty_nodes_no_error(self):
        fig, _ = plt.subplots()
        add_legend(fig, [], {})

    def test_vertical(self):
        fig, _ = plt.subplots()
        add_legend(fig, ["A", "B"], {"A": "red", "B": "blue"}, vertical=True)

    def test_ncol_int(self):
        fig, _ = plt.subplots()
        add_legend(fig, ["A", "B", "C"], {"A": "r", "B": "g", "C": "b"}, ncol=2)

    def test_ncol_nxm_string(self):
        fig, _ = plt.subplots()
        add_legend(fig, ["A", "B", "C", "D"], {"A": "r", "B": "g", "C": "b", "D": "y"}, ncol="2x2")

    def test_ncol_nxm_invalid_raises(self):
        fig, _ = plt.subplots()
        with pytest.raises(ValueError):
            add_legend(fig, ["A"], {"A": "r"}, ncol="bad")

    def test_missing_color_uses_default(self):
        fig, _ = plt.subplots()
        add_legend(fig, ["A"], {})


class TestBalanceNcol:
    def test_no_waste(self):
        assert _balance_ncol(3, 9) == 3

    def test_reduces_waste(self):
        result = _balance_ncol(4, 9)
        assert ((-9) % result) <= ((-9) % 4) or result == 4

    def test_minimum_one(self):
        assert _balance_ncol(1, 5) == 1

    def test_single_item(self):
        assert 1 <= _balance_ncol(3, 1) <= 3


class TestResolveNcol:
    def test_int_passthrough(self):
        fig, _ = plt.subplots()
        handles = [plt.Rectangle((0, 0), 1, 1)] * 4
        ncol, out = _resolve_ncol(2, handles, ["a", "b", "c", "d"], 12.0, fig)
        assert ncol == 2
        assert out is handles

    def test_nxm_clips_handles(self):
        fig, _ = plt.subplots()
        handles = [plt.Rectangle((0, 0), 1, 1)] * 6
        ncol, out = _resolve_ncol("2x2", handles, ["a"] * 6, 12.0, fig)
        assert ncol == 2
        assert len(out) == 4

    def test_nxm_invalid_raises(self):
        fig, _ = plt.subplots()
        with pytest.raises(ValueError):
            _resolve_ncol("bad", [], [], 12.0, fig)

    def test_auto_returns_positive_int(self):
        fig, _ = plt.subplots()
        handles = [plt.Rectangle((0, 0), 1, 1)] * 5
        ncol, _ = _resolve_ncol(None, handles, ["label"] * 5, 12.0, fig)
        assert isinstance(ncol, int)
        assert ncol >= 1
