"""Social network graph helpers — follower/mention/interaction graphs."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..graph import BubbleGraph


_CLUSTER_COLORS = [
    "#E41A1C", "#377EB8", "#4DAF4A", "#984EA3",
    "#FF7F00", "#A65628", "#F781BF", "#999999",
    "#66C2A5", "#FC8D62", "#8DA0CB", "#E78AC3",
]


def _cluster_color(cluster: int) -> str:
    return _CLUSTER_COLORS[cluster % len(_CLUSTER_COLORS)]


# ── Graph builders ───────────────────────────────────────────────

def from_edge_list(
    edges: List[Tuple[str, str, float]],
    *,
    clusters: Optional[Dict[str, int]] = None,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Build a social graph from an edge list.

    Parameters
    ----------
    edges:
        List of ``(source, target, weight)`` tuples.
        Weight = number of interactions.
    clusters:
        Optional ``{user: cluster_id}`` for colouring.
    """
    g = BubbleGraph()
    all_users = set()
    for src, tgt, _ in edges:
        all_users.add(src)
        all_users.add(tgt)

    for user in sorted(all_users):
        if node_colors and user in node_colors:
            color = node_colors[user]
        elif clusters and user in clusters:
            color = _cluster_color(clusters[user])
        else:
            color = "#CCCCCC"
        g.add_node(user, color=color, radius=node_radius, label=user)

    for src, tgt, w in edges:
        g.add_edge(src, tgt, weight=w)

    return g


def from_adjacency_file(
    path: str | Path,
    *,
    delimiter: str = "\t",
    has_header: bool = True,
    clusters: Optional[Dict[str, int]] = None,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Load a social graph from a CSV/TSV adjacency file.

    Expected columns: source, target, weight (with or without header).
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    start = 1 if has_header else 0
    edges: List[Tuple[str, str, float]] = []
    for line in lines[start:]:
        parts = line.strip().split(delimiter)
        if len(parts) >= 3:
            edges.append((parts[0], parts[1], float(parts[2])))
        elif len(parts) == 2:
            edges.append((parts[0], parts[1], 1.0))
    return from_edge_list(edges, clusters=clusters, node_radius=node_radius,
                          node_colors=node_colors)


def from_interaction_counts(
    counts: Dict[Tuple[str, str], float],
    *,
    min_interactions: int = 1,
    clusters: Optional[Dict[str, int]] = None,
    node_radius: float = 0.46,
    node_colors: Optional[Dict[str, str]] = None,
) -> BubbleGraph:
    """Build a graph from aggregated interaction counts.

    Parameters
    ----------
    counts:
        ``{(source, target): interaction_count}`` mapping.
    min_interactions:
        Drop pairs below this threshold.
    """
    edges = [
        (s, t, w) for (s, t), w in counts.items()
        if w >= min_interactions
    ]
    return from_edge_list(edges, clusters=clusters, node_radius=node_radius,
                          node_colors=node_colors)


# ── Community detection (simple label propagation) ───────────────

def detect_clusters(
    graph: BubbleGraph,
    *,
    iterations: int = 10,
) -> Dict[str, int]:
    """Simple label-propagation community detection.

    Returns ``{node_name: cluster_id}``.
    """
    labels = {name: i for i, name in enumerate(sorted(graph.nodes.keys()))}

    adj: Dict[str, List[str]] = defaultdict(list)
    for e in graph.edges:
        adj[e.source].append(e.target)
        adj[e.target].append(e.source)

    for _ in range(iterations):
        changed = False
        for node in sorted(labels.keys()):
            if not adj[node]:
                continue
            neighbor_labels = [labels[n] for n in adj[node]]
            counts: Dict[int, int] = defaultdict(int)
            for lbl in neighbor_labels:
                counts[lbl] += 1
            best = max(counts, key=counts.get)
            if best != labels[node]:
                labels[node] = best
                changed = True
        if not changed:
            break

    unique = sorted(set(labels.values()))
    remap = {old: new for new, old in enumerate(unique)}
    return {n: remap[l] for n, l in labels.items()}
