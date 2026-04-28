"""Tests for netbubbles core modules."""

import pytest

from netbubbles.graph import BubbleGraph, Edge, Node
from netbubbles.layout import bilayer, circular, focus, grid, manual
from netbubbles.style import Style, default_style


# ── Node / Edge ──────────────────────────────────────────────────

class TestNode:
    def test_display_label_default(self):
        n = Node(name="A")
        assert n.display_label == "A"

    def test_display_label_custom(self):
        n = Node(name="A", label="Alpha")
        assert n.display_label == "Alpha"


class TestEdge:
    def test_self_loop(self):
        assert Edge(source="A", target="A").is_self_loop is True

    def test_not_self_loop(self):
        assert Edge(source="A", target="B").is_self_loop is False


# ── BubbleGraph ──────────────────────────────────────────────────

class TestBubbleGraph:
    def test_add_node(self):
        g = BubbleGraph()
        g.add_node("A", color="red")
        assert "A" in g.nodes
        assert g.nodes["A"].color == "red"

    def test_add_nodes(self):
        g = BubbleGraph()
        g.add_nodes(["A", "B", "C"])
        assert len(g.nodes) == 3

    def test_add_edge_auto_creates_nodes(self):
        g = BubbleGraph()
        g.add_edge("A", "B", weight=5)
        assert "A" in g.nodes
        assert "B" in g.nodes
        assert len(g.edges) == 1

    def test_node_names(self):
        g = BubbleGraph()
        g.add_nodes(["X", "Y"])
        assert sorted(g.node_names) == ["X", "Y"]

    def test_positions(self):
        g = BubbleGraph()
        g.add_node("A")
        g.positions = {"A": (1.0, 2.0)}
        assert g.positions["A"] == (1.0, 2.0)


class TestConstructors:
    def test_from_weighted_edges(self):
        g = BubbleGraph.from_weighted_edges(
            {("A", "B"): 3, ("B", "C"): 5},
            colors={"A": "red"},
        )
        assert len(g.nodes) == 3
        assert len(g.edges) == 2
        assert g.nodes["A"].color == "red"
        assert g.nodes["B"].color == "#CCCCCC"

    def test_from_adjacency(self):
        matrix = [[0, 2], [3, 0]]
        g = BubbleGraph.from_adjacency(matrix, ["X", "Y"], threshold=0)
        assert len(g.edges) == 2

    def test_from_adjacency_threshold(self):
        matrix = [[0, 0.5], [3, 0]]
        g = BubbleGraph.from_adjacency(matrix, ["X", "Y"], threshold=1)
        assert len(g.edges) == 1


class TestTransforms:
    def _make_graph(self):
        g = BubbleGraph()
        g.add_node("A", color="red")
        g.add_node("B", color="blue")
        g.add_node("C", color="green")
        g.add_edge("A", "B", weight=3)
        g.add_edge("B", "C", weight=5)
        g.add_edge("A", "B", weight=2)
        return g

    def test_aggregate_edges(self):
        g = self._make_graph()
        agg = g.aggregate_edges()
        assert len(agg.edges) == 2
        ab = [e for e in agg.edges if e.source == "A" and e.target == "B"][0]
        assert ab.weight == 5.0

    def test_subgraph(self):
        g = self._make_graph()
        sub = g.subgraph(["A", "B"])
        assert "C" not in sub.nodes
        assert len(sub.edges) == 2

    def test_filter_edges(self):
        g = self._make_graph()
        heavy = g.filter_edges(lambda e: e.weight > 3)
        assert len(heavy.edges) == 1


# ── Layouts ──────────────────────────────────────────────────────

class TestLayouts:
    def test_circular(self):
        pos = circular(["A", "B", "C"])
        assert len(pos) == 3
        for p in pos.values():
            assert len(p) == 2

    def test_circular_order(self):
        pos = circular(["C", "A", "B"], order=["A", "B", "C"])
        keys = list(pos.keys())
        assert keys == ["A", "B", "C"]

    def test_focus(self):
        pos = focus(["A", "B", "C"], center="A")
        assert pos["A"] == (0.0, 0.0)
        assert len(pos) == 3

    def test_bilayer(self):
        pos = bilayer(["A", "B"], ["C", "D"])
        assert len(pos) == 4

    def test_grid(self):
        pos = grid(["A", "B", "C", "D"])
        assert len(pos) == 4

    def test_manual(self):
        pos = manual({"A": (1.0, 2.0)})
        assert pos["A"] == (1.0, 2.0)


# ── Style ────────────────────────────────────────────────────────

class TestStyle:
    def test_default(self):
        assert default_style is not None
        assert default_style.curve_strength > 0

    def test_edge_color(self):
        s = Style()
        assert isinstance(s.edge_color(0.0), str)
        assert isinstance(s.edge_color(1.0), str)

    def test_custom_tiers(self):
        from netbubbles.style import EdgeTier
        s = Style(edge_tiers=[
            EdgeTier("red", 3.0, 0.9),
            EdgeTier("blue", 1.0, 0.5),
        ])
        assert s.edge_color(0.0) == "blue"
        assert s.edge_color(1.0) == "red"
