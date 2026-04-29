import pytest

from netbubbles.graph import (
    BubbleGraph,
    Edge,
    Node,
)


class TestNode:
    def test_display_label_default(self):
        assert Node(name="A").display_label == "A"

    def test_display_label_custom(self):
        assert Node(name="A", label="Alpha").display_label == "Alpha"

    def test_default_color(self):
        assert Node(name="A").color == "#CCCCCC"

    def test_default_radius(self):
        assert Node(name="A").radius == 0.46

    def test_metadata_default_empty(self):
        assert Node(name="A").metadata == {}

    def test_metadata_stored(self):
        assert Node(name="A", metadata={"k": 1}).metadata == {"k": 1}


class TestEdge:
    def test_self_loop(self):
        assert Edge(source="A", target="A").is_self_loop is True

    def test_not_self_loop(self):
        assert Edge(source="A", target="B").is_self_loop is False

    def test_default_weight(self):
        assert Edge(source="A", target="B").weight == 1.0

    def test_custom_attributes_stored(self):
        e = Edge(source="X", target="Y", weight=3.0, color="red", linewidth=2.0, alpha=0.5)
        assert e.color == "red"
        assert e.linewidth == 2.0
        assert e.alpha == 0.5


class TestBubbleGraph:
    def test_add_node(self):
        g = BubbleGraph()
        g.add_node("A", color="red")
        assert "A" in g.nodes
        assert g.nodes["A"].color == "red"

    def test_add_node_returns_self(self):
        g = BubbleGraph()
        assert g.add_node("A") is g

    def test_add_nodes(self):
        g = BubbleGraph()
        g.add_nodes(["A", "B", "C"])
        assert len(g.nodes) == 3

    def test_add_nodes_with_colors(self):
        g = BubbleGraph()
        g.add_nodes(["A", "B"], colors={"A": "red"})
        assert g.nodes["A"].color == "red"
        assert g.nodes["B"].color == "#CCCCCC"

    def test_add_edge_auto_creates_nodes(self):
        g = BubbleGraph()
        g.add_edge("A", "B", weight=5)
        assert "A" in g.nodes and "B" in g.nodes
        assert len(g.edges) == 1

    def test_add_edge_returns_self(self):
        g = BubbleGraph()
        assert g.add_edge("A", "B") is g

    def test_add_edges(self):
        g = BubbleGraph()
        g.add_edges([("A", "B", 1.0), ("B", "C", 2.0)])
        assert len(g.edges) == 2
        assert len(g.nodes) == 3

    def test_get_node(self):
        g = BubbleGraph()
        g.add_node("A", color="blue")
        assert g.get_node("A").color == "blue"

    def test_get_node_missing_raises(self):
        g = BubbleGraph()
        with pytest.raises(KeyError):
            g.get_node("Z")

    def test_node_names(self):
        g = BubbleGraph()
        g.add_nodes(["X", "Y"])
        assert sorted(g.node_names) == ["X", "Y"]

    def test_positions_setter(self):
        g = BubbleGraph()
        g.add_node("A")
        g.positions = {"A": (1.0, 2.0)}
        assert g.positions["A"] == (1.0, 2.0)

    def test_empty_graph(self):
        g = BubbleGraph()
        assert g.nodes == {}
        assert g.edges == []


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

    def test_from_weighted_edges_no_colors(self):
        g = BubbleGraph.from_weighted_edges({("A", "B"): 1.0})
        assert g.nodes["A"].color == "#CCCCCC"

    def test_from_adjacency(self):
        g = BubbleGraph.from_adjacency([[0, 2], [3, 0]], ["X", "Y"], threshold=0)
        assert len(g.edges) == 2

    def test_from_adjacency_threshold(self):
        g = BubbleGraph.from_adjacency([[0, 0.5], [3, 0]], ["X", "Y"], threshold=1)
        assert len(g.edges) == 1

    def test_from_adjacency_diagonal_self_loops(self):
        g = BubbleGraph.from_adjacency([[1, 0], [0, 1]], ["A", "B"], threshold=0)
        self_loops = [e for e in g.edges if e.is_self_loop]
        assert len(self_loops) == 2

    def test_from_adjacency_all_zero_no_edges(self):
        g = BubbleGraph.from_adjacency([[0, 0], [0, 0]], ["A", "B"])
        assert len(g.edges) == 0

    def test_from_adjacency_with_colors(self):
        g = BubbleGraph.from_adjacency(
            [[0, 1], [0, 0]], ["P", "Q"], colors={"P": "green"}, threshold=0,
        )
        assert g.nodes["P"].color == "green"


class TestTransforms:
    def _make_graph(self) -> BubbleGraph:
        g = BubbleGraph()
        g.add_node("A", color="red")
        g.add_node("B", color="blue")
        g.add_node("C", color="green")
        g.add_edge("A", "B", weight=3)
        g.add_edge("B", "C", weight=5)
        g.add_edge("A", "B", weight=2)
        return g

    def test_aggregate_edges_count(self):
        agg = self._make_graph().aggregate_edges()
        assert len(agg.edges) == 2

    def test_aggregate_edges_sum(self):
        agg = self._make_graph().aggregate_edges()
        ab = next(e for e in agg.edges if e.source == "A" and e.target == "B")
        assert ab.weight == 5.0

    def test_aggregate_edges_preserves_node_colors(self):
        agg = self._make_graph().aggregate_edges()
        assert agg.nodes["A"].color == "red"

    def test_subgraph_excludes_node(self):
        sub = self._make_graph().subgraph(["A", "B"])
        assert "C" not in sub.nodes

    def test_subgraph_edge_count(self):
        sub = self._make_graph().subgraph(["A", "B"])
        assert len(sub.edges) == 2

    def test_subgraph_preserves_color(self):
        sub = self._make_graph().subgraph(["A", "B"])
        assert sub.nodes["A"].color == "red"

    def test_filter_edges_heavy(self):
        heavy = self._make_graph().filter_edges(lambda e: e.weight > 3)
        assert len(heavy.edges) == 1

    def test_filter_edges_keeps_all_nodes(self):
        heavy = self._make_graph().filter_edges(lambda e: e.weight > 3)
        assert set(heavy.nodes.keys()) == {"A", "B", "C"}

    def test_filter_edges_none_pass(self):
        result = self._make_graph().filter_edges(lambda e: e.weight > 100)
        assert len(result.edges) == 0
        assert len(result.nodes) == 3

    def test_filter_edges_all_pass(self):
        g = self._make_graph()
        assert len(g.filter_edges(lambda _: True).edges) == len(g.edges)
