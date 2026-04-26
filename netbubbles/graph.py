"""Core data model: BubbleGraph, Node, Edge."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Self, Tuple


@dataclass
class Node:
    name: str
    color: str = "#CCCCCC"
    radius: float = 0.46
    label: Optional[str] = None
    label_position: str = "outer"
    label_fontsize: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_label(self) -> str:
        return self.label if self.label is not None else self.name


@dataclass
class Edge:
    source: str
    target: str
    weight: float = 1.0
    color: Optional[str] = None
    linewidth: Optional[float] = None
    alpha: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_self_loop(self) -> bool:
        return self.source == self.target


class BubbleGraph:
    """Directed graph with bubble (circle) nodes and curved arrow edges."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Edge] = []
        self._positions: Dict[str, Tuple[float, float]] = {}

    # ── Node ops ─────────────────────────────────────────────────

    def add_node(self, name: str, **kwargs: Any) -> Self:
        self._nodes[name] = Node(name=name, **kwargs)
        return self

    def add_nodes(
        self,
        names: Iterable[str],
        *,
        colors: Optional[Dict[str, str]] = None,
        radius: float = 0.46,
    ) -> Self:
        for n in names:
            self.add_node(n, color=(colors or {}).get(n, "#CCCCCC"), radius=radius)
        return self

    def get_node(self, name: str) -> Node:
        return self._nodes[name]

    # ── Edge ops ─────────────────────────────────────────────────

    def add_edge(self, source: str, target: str, weight: float = 1.0, **kwargs: Any) -> Self:
        if source not in self._nodes:
            self.add_node(source)
        if target not in self._nodes:
            self.add_node(target)
        self._edges.append(Edge(source=source, target=target, weight=weight, **kwargs))
        return self

    def add_edges(
        self,
        pairs: Iterable[Tuple[str, str, float]],
    ) -> Self:
        for src, tgt, w in pairs:
            self.add_edge(src, tgt, weight=w)
        return self

    # ── Properties ───────────────────────────────────────────────

    @property
    def nodes(self) -> Dict[str, Node]:
        return self._nodes

    @property
    def edges(self) -> List[Edge]:
        return self._edges

    @property
    def node_names(self) -> List[str]:
        return list(self._nodes.keys())

    @property
    def positions(self) -> Dict[str, Tuple[float, float]]:
        return self._positions

    @positions.setter
    def positions(self, pos: Dict[str, Tuple[float, float]]) -> None:
        self._positions = pos

    # ── Constructors ─────────────────────────────────────────────

    @classmethod
    def from_weighted_edges(
        cls,
        pairs: Dict[Tuple[str, str], float],
        *,
        colors: Optional[Dict[str, str]] = None,
        radius: float = 0.46,
    ) -> Self:
        g = cls()
        for (src, tgt), w in pairs.items():
            for n in (src, tgt):
                if n not in g._nodes:
                    g.add_node(n, color=(colors or {}).get(n, "#CCCCCC"), radius=radius)
            g.add_edge(src, tgt, weight=w)
        return g

    @classmethod
    def from_adjacency(
        cls,
        matrix: List[List[float]],
        labels: List[str],
        *,
        colors: Optional[Dict[str, str]] = None,
        radius: float = 0.46,
        threshold: float = 0.0,
    ) -> Self:
        g = cls()
        for name in labels:
            g.add_node(name, color=(colors or {}).get(name, "#CCCCCC"), radius=radius)
        for i, src in enumerate(labels):
            for j, tgt in enumerate(labels):
                w = matrix[i][j]
                if w > threshold:
                    g.add_edge(src, tgt, weight=w)
        return g

    # ── Transforms ───────────────────────────────────────────────

    def aggregate_edges(self) -> Self:
        agg: Dict[Tuple[str, str], float] = defaultdict(float)
        for e in self._edges:
            agg[(e.source, e.target)] += e.weight
        g = BubbleGraph()
        for name, node in self._nodes.items():
            g.add_node(
                name,
                color=node.color,
                radius=node.radius,
                label=node.label,
                label_position=node.label_position,
                label_fontsize=node.label_fontsize,
                metadata=node.metadata,
            )
        for (src, tgt), w in agg.items():
            g.add_edge(src, tgt, weight=w)
        return g

    def subgraph(self, node_names: Iterable[str]) -> Self:
        keep = set(node_names)
        g = BubbleGraph()
        for n in keep:
            if n in self._nodes:
                nd = self._nodes[n]
                g.add_node(n, color=nd.color, radius=nd.radius, label=nd.label,
                           label_position=nd.label_position, label_fontsize=nd.label_fontsize,
                           metadata=nd.metadata)
        for e in self._edges:
            if e.source in keep and e.target in keep:
                g.add_edge(e.source, e.target, weight=e.weight, color=e.color,
                           linewidth=e.linewidth, alpha=e.alpha, metadata=e.metadata)
        return g

    def filter_edges(self, predicate) -> Self:
        g = BubbleGraph()
        for name, node in self._nodes.items():
            g.add_node(name, color=node.color, radius=node.radius, label=node.label,
                       label_position=node.label_position, label_fontsize=node.label_fontsize,
                       metadata=node.metadata)
        for e in self._edges:
            if predicate(e):
                g.add_edge(e.source, e.target, weight=e.weight, color=e.color,
                           linewidth=e.linewidth, alpha=e.alpha, metadata=e.metadata)
        return g
